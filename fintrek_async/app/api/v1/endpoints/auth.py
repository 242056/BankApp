"""
Эндпоинты для аутентификации и авторизации (ASYNC)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from slowapi import Limiter
from slowapi.util import get_remote_address
from datetime import datetime, timedelta
import logging

from fintrek_async.app.db.session import get_db
from fintrek_async.app.models.user import User
from fintrek_async.app.schemas.user import UserCreate, UserResponse
from fintrek_async.app.schemas.token import Token, RefreshTokenRequest
from fintrek_async.app.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)
from fintrek_async.app.core.password_validator import validate_password_strength

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
logger = logging.getLogger(__name__)

# Константы для account lockout
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")  # Ограничение для защиты от спама
async def register(
    request: Request,
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Регистрация нового пользователя
    
    - **email**: Email пользователя (должен быть уникальным)
    - **password**: Пароль (минимум 8 символов, должен содержать заглавные, строчные буквы, цифры и спецсимволы)
    - **name**: Имя пользователя
    """
    # Проверяем надежность пароля
    is_valid, errors = validate_password_strength(user_data.password)
    if not is_valid:
        logger.warning(f"Weak password attempt during registration for {user_data.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Пароль не соответствует требованиям безопасности",
                "errors": errors
            }
        )
    
    # Проверяем, существует ли пользователь с таким email (ASYNC)
    # Используем явное преобразование в строку для избежания проблем с типизацией
    result = await db.execute(
        select(User).where(User.email == str(user_data.email))
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    
    # Создаем нового пользователя
    new_user = User(
        email=user_data.email,
        name=user_data.name,
        password_hash=get_password_hash(user_data.password)
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=Token)
@limiter.limit("5/minute")  # Защита от brute force атак
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Вход пользователя
    
    Возвращает access и refresh токены
    """
    # Находим пользователя (ASYNC)
    result = await db.execute(
        select(User).where(User.email == str(email))
    )
    user = result.scalar_one_or_none()
    
    # Проверяем существование пользователя и пароль
    if not user:
        # Не раскрываем, что пользователь не найден (защита от email enumeration)
        logger.warning(f"Login attempt for non-existent email: {email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные"
        )
    
    # Проверяем, не заблокирован ли аккаунт
    if user.locked_until and user.locked_until > datetime.utcnow():
        remaining_time = (user.locked_until - datetime.utcnow()).seconds // 60
        logger.warning(f"Login attempt for locked account: {email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Аккаунт заблокирован. Попробуйте через {remaining_time} минут."
        )
    
    # Проверяем пароль
    if not verify_password(password, user.password_hash):
        # Увеличиваем счетчик неудачных попыток
        user.failed_login_attempts += 1
        
        # Блокируем аккаунт после MAX_LOGIN_ATTEMPTS попыток
        if user.failed_login_attempts >= MAX_LOGIN_ATTEMPTS:
            user.locked_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
            await db.commit()
            logger.warning(f"Account locked due to too many failed attempts: {email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Аккаунт заблокирован на {LOCKOUT_DURATION_MINUTES} минут из-за множества неудачных попыток входа."
            )
        
        await db.commit()
        logger.warning(f"Failed login attempt for {email}. Attempts: {user.failed_login_attempts}/{MAX_LOGIN_ATTEMPTS}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные"
        )
    
    # Успешный вход - сбрасываем счетчик
    user.failed_login_attempts = 0
    user.locked_until = None
    await db.commit()
    
    logger.info(f"Successful login for {email}")
    
    # Создаем токены
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
@limiter.limit("10/minute")  # Чуть больше для refresh, но все равно ограничено
async def refresh_token(
    request: Request,
    refresh_request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Обновление access токена с помощью refresh токена
    """
    # Декодируем refresh токен
    payload = decode_token(refresh_request.refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный refresh токен"
        )
    
    # Проверяем тип токена
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный тип токена"
        )
    
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен"
        )
    
    # Преобразуем user_id в UUID
    try:
        user_id = UUID(user_id_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный формат user_id в токене"
        )
    
    # Проверяем существование пользователя (ASYNC)
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден"
        )
    
    # Создаем новые токены
    new_access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }

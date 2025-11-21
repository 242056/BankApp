"""
API эндпоинты для управления пользователями
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from fintrek_async.app.api.v1.deps import get_db, get_current_user
from fintrek_async.app.models.user import User
from fintrek_async.app.schemas.user import UserUpdate, UserResponse
from fintrek_async.app.core.security import get_password_hash

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Получить информацию о текущем пользователе
    
    Возвращает профиль авторизованного пользователя.
    """
    return current_user


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Обновить профиль текущего пользователя
    
    Позволяет изменить имя, email или пароль.
    """
    # Обновить поля, если они предоставлены
    if user_update.full_name is not None:
        current_user.name = user_update.full_name
    
    if user_update.email is not None:
        # Проверить, не занят ли email
        existing_user = (await db.execute(select(User).where(
            User.email == user_update.email,
            User.id != current_user.id
        ))).scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="Email уже используется"
            )
        
        current_user.email = user_update.email
    
    if user_update.password is not None:
        current_user.password_hash = get_password_hash(user_update.password)
    
    await db.commit()
    await db.refresh(current_user)
    
    return current_user

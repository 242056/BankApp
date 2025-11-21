"""
Утилиты для работы с безопасностью
Хеширование паролей и работа с JWT токенами
"""
from datetime import datetime, timedelta
from typing import Optional, Union
from jose import jwt, JWTError
import bcrypt
from fintrek_async.app.core.config import settings


def _truncate_to_72_bytes(text: str) -> str:
    """
    Безопасно обрезать строку до 72 байт, не разрывая UTF-8 символы
    
    Args:
        text: Строка для обрезки
        
    Returns:
        Строка, обрезанная до 72 байт
    """
    text_bytes = text.encode('utf-8')
    if len(text_bytes) <= 72:
        return text
    
    # Обрезаем до 72 байт
    truncated = text_bytes[:72]
    
    # Удаляем неполные UTF-8 символы в конце
    while truncated:
        try:
            return truncated.decode('utf-8')
        except UnicodeDecodeError:
            truncated = truncated[:-1]
    
    return ''


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверка соответствия пароля его хешу
    
    Args:
        plain_password: Пароль в открытом виде
        hashed_password: Хешированный пароль из БД
        
    Returns:
        True если пароль совпадает, иначе False
    """
    # bcrypt имеет ограничение в 72 байта, обрезаем пароль если необходимо
    plain_password = _truncate_to_72_bytes(plain_password)
    
    try:
        # Используем bcrypt напрямую для проверки пароля
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """
    Хеширование пароля
    
    Args:
        password: Пароль в открытом виде
        
    Returns:
        Хешированный пароль
        
    Note:
        bcrypt имеет ограничение в 72 байта для пароля.
        Пароли длиннее 72 байт будут обрезаны.
    """
    # bcrypt имеет ограничение в 72 байта, обрезаем пароль если необходимо
    password = _truncate_to_72_bytes(password)
    
    # Используем bcrypt напрямую для хеширования пароля
    # Генерируем соль и хешируем пароль
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    return hashed.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Создание JWT access токена
    
    Args:
        data: Данные для включения в токен (обычно user_id)
        expires_delta: Время жизни токена (если не указано, используется значение из настроек)
        
    Returns:
        JWT токен в виде строки
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """
    Создание JWT refresh токена
    
    Args:
        data: Данные для включения в токен (обычно user_id)
        
    Returns:
        JWT refresh токен в виде строки
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """
    Декодирование JWT токена
    
    Args:
        token: JWT токен
        
    Returns:
        Словарь с данными из токена или None в случае ошибки
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


from cryptography.fernet import Fernet
import base64


def get_encryption_key() -> bytes:
    """
    Получить ключ шифрования из настроек
    
    Returns:
        Ключ шифрования в байтах
    """
    # Используем отдельный ключ для шифрования данных
    key = settings.ENCRYPTION_KEY
    
    # Преобразовать ключ в формат, подходящий для Fernet (32 байта в base64)
    if len(key) < 32:
        key = key.ljust(32, '0')
    else:
        key = key[:32]
    
    return base64.urlsafe_b64encode(key.encode())


def encrypt_token(token: str) -> str:
    """
    Зашифровать токен для безопасного хранения в БД
    
    Args:
        token: Токен в открытом виде
        
    Returns:
        Зашифрованный токен
    """
    f = Fernet(get_encryption_key())
    encrypted = f.encrypt(token.encode())
    return encrypted.decode()


def decrypt_token(encrypted_token: str) -> str:
    """
    Расшифровать токен из БД
    
    Args:
        encrypted_token: Зашифрованный токен
        
    Returns:
        Токен в открытом виде
    """
    f = Fernet(get_encryption_key())
    decrypted = f.decrypt(encrypted_token.encode())
    return decrypted.decode()

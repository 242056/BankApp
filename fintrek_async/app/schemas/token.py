"""
Pydantic схемы для JWT токенов
"""
from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class Token(BaseModel):
    """Схема ответа с токенами"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Схема данных внутри JWT токена"""
    sub: Optional[UUID] = None  # subject (user_id)
    exp: Optional[int] = None   # expiration time


class RefreshTokenRequest(BaseModel):
    """Схема запроса на обновление токена"""
    refresh_token: str

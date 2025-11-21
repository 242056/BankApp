"""
Pydantic схемы для User
Используются для валидации входных данных и форматирования ответов
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    """Базовая схема пользователя"""
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=100)


class UserCreate(UserBase):
    """Схема для создания пользователя (регистрация)"""
    password: str = Field(
        ..., 
        min_length=8, 
        max_length=72,  # bcrypt ограничение: 72 байта
        description="Пароль должен быть от 8 до 72 символов"
    )


class UserUpdate(BaseModel):
    """Схема для обновления пользователя"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(
        None, 
        min_length=8, 
        max_length=72,  # bcrypt ограничение: 72 байта
        description="Пароль должен быть от 8 до 72 символов"
    )


class UserInDB(UserBase):
    """Схема пользователя в БД (с дополнительными полями)"""
    id: UUID
    subscription_tier: str
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserBase):
    """Схема для ответа API (без чувствительных данных)"""
    id: UUID
    subscription_tier: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

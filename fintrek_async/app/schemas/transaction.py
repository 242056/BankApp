"""
Pydantic схемы для Transaction
"""
from pydantic import BaseModel, UUID4, Field, field_validator
from datetime import datetime
from decimal import Decimal
from typing import Optional, Union
from fintrek_async.app.models.transaction import TransactionType, TransactionStatus


class TransactionBase(BaseModel):
    """Базовая схема транзакции"""
    transaction_type: TransactionType = Field(..., description="Тип транзакции")
    amount: Decimal = Field(..., gt=0, description="Сумма транзакции")
    currency: str = Field(default="RUB", max_length=3, description="Валюта (ISO 4217)")
    description: Optional[str] = Field(None, max_length=500, description="Описание транзакции")
    merchant_name: Optional[str] = Field(None, max_length=200, description="Название продавца")
    notes: Optional[str] = Field(None, description="Заметки пользователя")
    transaction_date: datetime = Field(..., description="Дата транзакции")


class TransactionCreate(TransactionBase):
    """Схема для создания транзакции
    
    Важно:
    - account_id: обязательное поле, должен быть валидным UUID
    - category_id: опциональное поле, передайте валидный UUID или null (или не передавайте поле вообще)
    - related_account_id: опциональное поле, передайте валидный UUID или null (или не передавайте поле вообще)
    """
    account_id: UUID4 = Field(
        ..., 
        description="ID счета (обязательное поле, должен быть валидным UUID)",
        json_schema_extra={"example": "40d4b4d9-9cb8-4d84-bd4a-00e370f46cb1"}
    )
    category_id: Optional[UUID4] = Field(
        default=None,
        description="ID категории (опционально: передайте валидный UUID, null, или не передавайте поле)",
        json_schema_extra={"example": None}
    )
    related_account_id: Optional[UUID4] = Field(
        default=None,
        description="ID связанного счета для переводов (опционально: передайте валидный UUID, null, или не передавайте поле)",
        json_schema_extra={"example": None}
    )
    
    @field_validator('category_id', 'related_account_id', mode='before')
    @classmethod
    def convert_empty_string_to_none(cls, v):
        """Преобразует пустые строки и строку 'string' в None"""
        if v is None:
            return None
        if isinstance(v, str):
            v_stripped = v.strip()
            # Если это пустая строка или строка "string", преобразуем в None
            if v_stripped == '' or v_stripped.lower() == 'string':
                return None
            # Если это не валидный UUID формат, тоже возвращаем None
            # (Pydantic сам проверит валидность UUID после этого)
        return v


class TransactionUpdate(BaseModel):
    """Схема для обновления транзакции
    
    Все поля опциональны. Передавайте только те поля, которые нужно обновить.
    Для category_id передайте валидный UUID или null, чтобы убрать категорию.
    """
    category_id: Optional[UUID4] = Field(
        None, 
        description="ID категории (опционально, должен быть валидным UUID если указан, или null чтобы убрать категорию)"
    )
    description: Optional[str] = Field(None, max_length=500, description="Описание транзакции")
    notes: Optional[str] = Field(None, description="Заметки пользователя")
    status: Optional[TransactionStatus] = Field(None, description="Статус транзакции (PENDING, COMPLETED, CANCELLED)")

    @field_validator('category_id', mode='before')
    @classmethod
    def convert_update_category(cls, v):
        """Преобразует пустые строки и строку 'string'/'income'/'expense' в None"""
        if v is None:
            return None
        if isinstance(v, str):
            stripped = v.strip()
            if stripped == "" or stripped.lower() in {"string", "income", "expense"}:
                return None
        return v


class TransactionResponse(TransactionBase):
    """Схема ответа с транзакцией"""
    id: UUID4
    user_id: UUID4
    account_id: UUID4
    category_id: Optional[UUID4]
    related_account_id: Optional[UUID4]
    posted_date: Optional[datetime]
    status: TransactionStatus
    external_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    """Схема для списка транзакций"""
    transactions: list[TransactionResponse]
    total: int
    page: int
    page_size: int


class TransactionFilter(BaseModel):
    """Схема для фильтрации транзакций"""
    account_id: Optional[UUID4] = None
    category_id: Optional[UUID4] = None
    transaction_type: Optional[TransactionType] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None

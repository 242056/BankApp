"""
Pydantic схемы для Account
"""
from pydantic import BaseModel, UUID4, Field
from datetime import datetime
from decimal import Decimal
from typing import Optional
from fintrek_async.app.models.account import AccountType, AccountStatus


class AccountBase(BaseModel):
    """Базовая схема счета"""
    account_name: str = Field(..., min_length=1, max_length=100, description="Название счета")
    account_type: AccountType = Field(..., description="Тип счета")
    currency: str = Field(default="RUB", max_length=3, description="Валюта счета (ISO 4217)")


class AccountCreate(AccountBase):
    """Схема для создания счета"""
    balance: Decimal = Field(default=Decimal("0.00"), description="Начальный баланс")
    account_number: Optional[str] = Field(None, description="Номер счета (опционально)")


class AccountUpdate(BaseModel):
    """Схема для обновления счета"""
    account_name: Optional[str] = Field(None, min_length=1, max_length=100)
    balance: Optional[Decimal] = None
    status: Optional[AccountStatus] = None


class AccountResponse(AccountBase):
    """Схема ответа со счетом"""
    id: UUID4
    user_id: UUID4
    bank_connection_id: Optional[UUID4]
    account_number: Optional[str]
    balance: Decimal
    available_balance: Optional[Decimal]
    status: AccountStatus
    last_synced_at: Optional[datetime]
    sync_error: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AccountListResponse(BaseModel):
    """Схема для списка счетов"""
    accounts: list[AccountResponse]
    total: int

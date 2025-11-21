"""
Pydantic схемы для BankConnection
"""
from pydantic import BaseModel, UUID4, Field
from datetime import datetime
from typing import Optional
from fintrek_async.app.models.bank_connection import BankConnectionStatus


class BankConnectionBase(BaseModel):
    """Базовая схема подключения к банку"""
    bank_name: str = Field(..., min_length=1, max_length=200, description="Название банка")
    bank_bic: Optional[str] = Field(None, max_length=9, description="БИК банка")


class BankConnectionCreate(BankConnectionBase):
    """Схема для создания подключения к банку"""
    pass


class BankConnectionResponse(BankConnectionBase):
    """Схема ответа с подключением к банку"""
    id: UUID4
    user_id: UUID4
    status: BankConnectionStatus
    last_error: Optional[str]
    last_synced_at: Optional[datetime]
    token_expires_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BankConnectionListResponse(BaseModel):
    """Схема для списка подключений к банкам"""
    connections: list[BankConnectionResponse]
    total: int


class BankConnectionSync(BaseModel):
    """Схема для запроса синхронизации"""
    connection_id: UUID4 = Field(..., description="ID подключения к банку")


class BankConnectionSyncResponse(BaseModel):
    """Схема ответа на синхронизацию"""
    success: bool
    message: str
    accounts_synced: int
    transactions_synced: int

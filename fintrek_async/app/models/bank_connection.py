"""
Модель подключения к банку для SQLAlchemy
"""
from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

try:
    from fintrek_async.app.db.base import Base
except ImportError:
    from ..db.base import Base


class BankConnectionStatus(str, enum.Enum):
    """Статусы подключения к банку"""
    ACTIVE = "active"          # Активное подключение
    EXPIRED = "expired"        # Токен истек
    ERROR = "error"            # Ошибка подключения
    DISCONNECTED = "disconnected"  # Отключено пользователем


class BankConnection(Base):
    """Модель подключения к банку через Open API"""
    __tablename__ = "bank_connections"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Информация о банке
    bank_name = Column(String, nullable=False)
    bank_bic = Column(String(9), nullable=True)  # БИК банка
    
    # OAuth данные (зашифрованные)
    access_token_encrypted = Column(Text, nullable=True)
    refresh_token_encrypted = Column(Text, nullable=True)
    token_expires_at = Column(DateTime, nullable=True)
    
    # Статус подключения
    status = Column(Enum(BankConnectionStatus), default=BankConnectionStatus.ACTIVE, nullable=False)
    last_error = Column(Text, nullable=True)
    
    # Синхронизация
    last_synced_at = Column(DateTime, nullable=True)
    
    # Метаданные
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Отношения
    user = relationship("User", back_populates="bank_connections")
    accounts = relationship("Account", back_populates="bank_connection", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<BankConnection(id={self.id}, bank={self.bank_name}, status={self.status})>"

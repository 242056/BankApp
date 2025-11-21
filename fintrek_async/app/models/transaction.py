"""
Модель транзакции для SQLAlchemy
"""
from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, Enum, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

try:
    from fintrek_async.app.db.base import Base
except ImportError:
    from ..db.base import Base


class TransactionType(str, enum.Enum):
    """Типы транзакций"""
    INCOME = "income"      # Доход
    EXPENSE = "expense"    # Расход
    TRANSFER = "transfer"  # Перевод между счетами


class TransactionStatus(str, enum.Enum):
    """Статусы транзакций"""
    PENDING = "pending"    # Ожидает обработки
    COMPLETED = "completed"  # Завершена
    CANCELLED = "cancelled"  # Отменена


class Transaction(Base):
    """Модель транзакции"""
    __tablename__ = "transactions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Информация о транзакции
    transaction_type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(3), default="RUB", nullable=False)
    
    # Описание и детали
    description = Column(String, nullable=True)
    merchant_name = Column(String, nullable=True)  # Название продавца/получателя
    notes = Column(Text, nullable=True)  # Заметки пользователя
    category_guess = Column(String, nullable=True)  # ML-предположение о категории
    provider = Column(String, nullable=True)  # Источник данных (vbank, manual, etc.)
    
    # Даты
    transaction_date = Column(DateTime, nullable=False, index=True)  # Дата транзакции
    posted_date = Column(DateTime, nullable=True)  # Дата проведения
    
    # Статус
    status = Column(Enum(TransactionStatus), default=TransactionStatus.COMPLETED, nullable=False)
    
    # Для переводов между счетами
    related_account_id = Column(UUID(as_uuid=True), ForeignKey("accounts.id", ondelete="SET NULL"), nullable=True)
    
    # Внешний ID (от банка)
    external_id = Column(String, nullable=True, unique=True, index=True)
    
    # Метаданные
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Отношения
    user = relationship("User", back_populates="transactions")
    account = relationship("Account", back_populates="transactions", foreign_keys=[account_id])
    category = relationship("Category", back_populates="transactions")
    related_account = relationship("Account", foreign_keys=[related_account_id])
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, type={self.transaction_type}, amount={self.amount})>"

"""
Модель банковского счета для SQLAlchemy
"""
from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

try:
    from fintrek_async.app.db.base import Base
except ImportError:
    from ..db.base import Base



class AccountType(str, enum.Enum):
    """Типы счетов"""
    CHECKING = "checking"  # Текущий счет
    SAVINGS = "savings"    # Сберегательный счет
    CREDIT_CARD = "credit_card"  # Кредитная карта
    INVESTMENT = "investment"  # Инвестиционный счет
    LOAN = "loan"  # Кредит


class AccountStatus(str, enum.Enum):
    """Статусы счета"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CLOSED = "closed"
    ERROR = "error"  # Ошибка синхронизации


class Account(Base):
    """Модель банковского счета"""
    __tablename__ = "accounts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    bank_connection_id = Column(UUID(as_uuid=True), ForeignKey("bank_connections.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # Информация о счете
    account_name = Column(String, nullable=False)  # Название счета (задается пользователем)
    name = Column(String, nullable=True)  # Упрощенное название (для совместимости с VBank)
    account_number = Column(String, nullable=True)  # Номер счета (маскированный)
    account_type = Column(Enum(AccountType), nullable=False)
    currency = Column(String(3), default="RUB", nullable=False)  # ISO 4217
    
    # Внешние идентификаторы
    external_id = Column(String, nullable=True, index=True)  # ID счета в банке/провайдере
    provider = Column(String, nullable=True)  # Источник данных (vbank, manual, etc.)
    
    # Финансовые данные
    balance = Column(Numeric(15, 2), default=0.00, nullable=False)
    available_balance = Column(Numeric(15, 2), nullable=True)  # Доступный баланс (может отличаться от balance)
    
    # Статус и синхронизация
    status = Column(Enum(AccountStatus), default=AccountStatus.ACTIVE, nullable=False)
    last_synced_at = Column(DateTime, nullable=True)  # Время последней синхронизации
    sync_error = Column(String, nullable=True)  # Описание ошибки синхронизации
    
    # Метаданные
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Отношения
    user = relationship("User", back_populates="accounts")
    bank_connection = relationship("BankConnection", back_populates="accounts")
    # Используем primaryjoin для явного указания конкретного foreign key
    # Когда есть несколько FK к одной таблице, нужно явно указать primaryjoin
    # Используем lambda с отложенным импортом для получения реального Column объекта
    transactions = relationship(
        "Transaction", 
        back_populates="account",
        primaryjoin=lambda: (
            Account.id == __import__("fintrek_async.app.models.transaction", fromlist=["Transaction"])
            .Transaction.account_id
        ),
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Account(id={self.id}, name={self.account_name}, balance={self.balance})>"

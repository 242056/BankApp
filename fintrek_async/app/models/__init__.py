"""
Импорт всех моделей для Alembic
"""
# Используем относительные импорты для совместимости с alembic
# и абсолютные для использования в приложении
try:
    # Попытка абсолютного импорта (для использования в приложении)
    from fintrek_async.app.models.user import User, SubscriptionTier
    from fintrek_async.app.models.account import Account, AccountType, AccountStatus
    from fintrek_async.app.models.transaction import Transaction, TransactionType, TransactionStatus
    from fintrek_async.app.models.category import Category, CategoryType
    from fintrek_async.app.models.bank_connection import BankConnection, BankConnectionStatus
except ImportError:
    # Fallback на относительные импорты (для alembic)
    from .user import User, SubscriptionTier
    from .account import Account, AccountType, AccountStatus
    from .transaction import Transaction, TransactionType, TransactionStatus
    from .category import Category, CategoryType
    from .bank_connection import BankConnection, BankConnectionStatus

__all__ = [
    "User",
    "SubscriptionTier",
    "Account",
    "AccountType",
    "AccountStatus",
    "Transaction",
    "TransactionType",
    "TransactionStatus",
    "Category",
    "CategoryType",
    "BankConnection",
    "BankConnectionStatus",
]

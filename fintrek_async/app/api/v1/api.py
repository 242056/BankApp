"""
Сборка всех роутеров API v1
"""
from fastapi import APIRouter
from fintrek_async.app.api.v1.endpoints import auth, accounts, transactions, categories, bank_connections, ai_insights, analytics, users
from .endpoints import vbank as vbank_router

api_router = APIRouter()

# Подключаем роутер аутентификации
api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["Аутентификация"]
)

# Подключаем роутер счетов
api_router.include_router(
    accounts.router,
    prefix="/accounts",
    tags=["Счета"]
)

# Подключаем роутер транзакций
api_router.include_router(
    transactions.router,
    prefix="/transactions",
    tags=["Транзакции"]
)

# Подключаем роутер категорий
api_router.include_router(
    categories.router,
    prefix="/categories",
    tags=["Категории"]
)

# Подключаем роутер подключений к банкам
api_router.include_router(
    bank_connections.router,
    prefix="/bank-connections",
    tags=["Подключения к банкам"]
)

# Подключаем роутер AI-инсайтов
api_router.include_router(
    ai_insights.router,
    prefix="/ai",
    tags=["AI-инсайты"]
)

# Подключаем роутер аналитики
api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["Аналитика"]
)

# Подключаем роутер пользователей
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Пользователи"]
)

api_router.include_router(vbank_router.router)
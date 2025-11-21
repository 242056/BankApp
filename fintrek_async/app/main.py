"""
Главный файл FastAPI приложения
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from contextlib import asynccontextmanager
import logging

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from fintrek_async.app.core.config import settings
from fintrek_async.app.api.v1.api import api_router
from fintrek_async.app.core.cache import init_cache, close_cache, is_cache_enabled
from fintrek_async.app.core.exceptions import (
    DatabaseConnectionError,
    RedisConnectionError,
    ExternalAPIError,
    FinTrekException
)
from fintrek_async.app.middleware.security import SecurityHeadersMiddleware

logger = logging.getLogger(__name__)

# Инициализация rate limiter
# Если Redis доступен, используем его для distributed rate limiting
# Иначе используем in-memory storage
def get_limiter_storage_uri():
    """Получить URI для хранилища rate limiter"""
    if is_cache_enabled():
        return settings.REDIS_URL
    return "memory://"

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200/minute"],  # Глобальный лимит по умолчанию
    storage_uri=get_limiter_storage_uri(),
    strategy="fixed-window"
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Стартуем
    try:
        await init_cache()
        logger.info("✅ Application startup complete")
    except Exception as e:
        logger.error(f"❌ Error during startup: {e}")
        # Продолжаем работу даже если кэш не инициализирован
    
    yield
    
    # Завершаем
    try:
        await close_cache()
        logger.info("✅ Application shutdown complete")
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")

# Создание экземпляра FastAPI приложения
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
    📊 **Финтрек API** - Интеллектуальная платформа для управления личными финансами
    
    ## Возможности
    
    * **Аутентификация** - Регистрация, вход и управление JWT токенами
    * **Управление счетами** - CRUD операции для банковских счетов
    * **Транзакции** - Учет доходов и расходов с фильтрацией
    * **Категории** - Классификация транзакций
    * **Аналитика** - Агрегированные данные о финансах
    * **AI-Инсайты** - Персонализированные рекомендации и прогнозы
    * **Open Banking** - Интеграция с банковскими API
    
    ## Технологии
    
    * FastAPI + SQLAlchemy + PostgreSQL
    * Redis для кэширования
    * JWT аутентификация
    * AI/ML для анализа и рекомендаций
    """,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
    contact={
        "name": "Команда Финтрек",
        "email": "support@fintrek.com"
    },
    license_info={
        "name": "MIT"
    }
)

# Подключаем rate limiter к приложению
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Глобальные обработчики исключений

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """
    Кастомный обработчик для rate limit exceeded
    """
    logger.warning(f"Rate limit exceeded for {get_remote_address(request)}")
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "error": "Too Many Requests",
            "message": "Rate limit exceeded. Please slow down your requests.",
            "retry_after": exc.detail if hasattr(exc, 'detail') else "60 seconds"
        }
    )

@app.exception_handler(DatabaseConnectionError)
async def database_connection_error_handler(request: Request, exc: DatabaseConnectionError):
    """
    Обработчик ошибок подключения к базе данных
    """
    logger.error(f"Database connection error: {exc.message}")
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "error": "Database Unavailable",
            "message": "The database is temporarily unavailable. Please try again later.",
            "details": exc.details if settings.DEBUG else None
        }
    )


@app.exception_handler(ExternalAPIError)
async def external_api_error_handler(request: Request, exc: ExternalAPIError):
    """
    Обработчик ошибок внешних API
    """
    logger.error(f"External API error: {exc.message}")
    return JSONResponse(
        status_code=exc.status_code or status.HTTP_502_BAD_GATEWAY,
        content={
            "error": "External Service Error",
            "message": exc.message,
            "details": exc.details if settings.DEBUG else None
        }
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Обработчик HTTP исключений
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": "HTTP Error",
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Обработчик ошибок валидации запросов
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "Invalid request data",
            "details": exc.errors()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Обработчик всех необработанных исключений (500 ошибки)
    """
    logger.exception(f"Unhandled exception: {exc}")
    
    # В production не показываем детали ошибки
    error_details = str(exc) if settings.DEBUG else "An unexpected error occurred"
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": error_details,
            "request_id": getattr(request.state, "request_id", None)
        }
    )

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_origin_regex=settings.BACKEND_CORS_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security middleware
app.add_middleware(SecurityHeadersMiddleware)

# HTTPS redirect в production
if not settings.DEBUG:
    app.add_middleware(HTTPSRedirectMiddleware)
    logger.info("✅ HTTPS redirect enabled (production mode)")

# Trusted Host middleware (защита от Host header attacks)
if not settings.DEBUG:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # Настройте для production
    )

# Подключение роутеров
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/")
async def root():
    """Корневой эндпоинт для проверки работоспособности API"""
    return {
        "message": "Добро пожаловать в Финтрек API",
        "version": settings.VERSION,
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check эндпоинт"""
    return {"status": "healthy"}

"""
Настройка Redis для кэширования
"""
import redis.asyncio as redis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fintrek_async.app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Флаг для отслеживания состояния кэша
_cache_enabled = False


async def init_cache():
    """
    Инициализация кэша при старте приложения
    
    Если Redis недоступен, приложение продолжит работу без кэширования
    """
    global _cache_enabled
    
    try:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            socket_connect_timeout=5,  # Таймаут подключения
            socket_timeout=5  # Таймаут операций
        )
        
        # Проверяем подключение
        await redis_client.ping()
        
        FastAPICache.init(RedisBackend(redis_client), prefix="fintrek-cache:")
        _cache_enabled = True
        logger.info("✅ Redis cache initialized successfully")
        
    except redis.ConnectionError as e:
        logger.warning(f"⚠️  Redis connection failed: {e}. Running without cache.")
        _cache_enabled = False
    except redis.TimeoutError as e:
        logger.warning(f"⚠️  Redis connection timeout: {e}. Running without cache.")
        _cache_enabled = False
    except Exception as e:
        logger.error(f"❌ Unexpected error initializing Redis cache: {e}. Running without cache.")
        _cache_enabled = False


async def close_cache():
    """
    Закрытие соединения с Redis при остановке приложения
    """
    global _cache_enabled
    
    if not _cache_enabled:
        logger.info("Cache was not enabled, skipping close")
        return
    
    try:
        await FastAPICache.clear()
        logger.info("✅ Redis cache closed successfully")
    except Exception as e:
        logger.error(f"❌ Error closing Redis cache: {e}")


def is_cache_enabled() -> bool:
    """
    Проверить, включен ли кэш
    
    Returns:
        True если Redis доступен, False если работаем без кэша
    """
    return _cache_enabled

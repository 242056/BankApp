"""
Асинхронная сессия базы данных
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from fintrek_async.app.core.config import settings
from fintrek_async.app.core.exceptions import DatabaseConnectionError
import logging

logger = logging.getLogger(__name__)

# Создаем асинхронный engine
engine = create_async_engine(
    settings.ASYNC_DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,  # Проверка соединения перед использованием
    pool_recycle=3600,  # Переподключение каждый час
    pool_size=5,
    max_overflow=10
)

# Создаем фабрику асинхронных сессий
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


async def get_db():
    """
    Зависимость для получения асинхронной сессии БД
    
    Raises:
        DatabaseConnectionError: Если не удалось подключиться к БД
    """
    session = None
    try:
        session = AsyncSessionLocal()
        yield session
        await session.commit()
        
    except OperationalError as e:
        logger.error(f"❌ Database connection error: {e}")
        if session:
            await session.rollback()
        raise DatabaseConnectionError(
            "Failed to connect to database. Please try again later.",
            details={"error": str(e)}
        )
        
    except SQLAlchemyError as e:
        logger.error(f"❌ Database error: {e}")
        if session:
            await session.rollback()
        raise
        
    except Exception as e:
        logger.error(f"❌ Unexpected error in database session: {e}")
        if session:
            await session.rollback()
        raise
        
    finally:
        if session:
            await session.close()

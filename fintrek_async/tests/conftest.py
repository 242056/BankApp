"""
Конфигурация pytest для асинхронных тестов
"""
import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from fintrek_async.app.main import app
from fintrek_async.app.db.session import get_db
from fintrek_async.app.core.config import settings

# Тестовая база данных
TEST_DATABASE_URL = settings.ASYNC_DATABASE_URL.replace("fintrek_db", "fintrek_test_db")

# Создаем async engine для тестов
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop():
    """Создать event loop для всей сессии тестов"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Фикстура для асинхронной сессии БД"""
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Фикстура для асинхронного HTTP клиента"""
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def auth_headers(client: AsyncClient, db_session: AsyncSession) -> dict:
    """Фикстура для получения заголовков авторизации"""
    # Создаем тестового пользователя
    from fintrek_async.app.models.user import User
    from fintrek_async.app.core.security import get_password_hash, create_access_token
    
    test_user = User(
        email="test@example.com",
        name="Test User",
        password_hash=get_password_hash("testpassword")
    )
    db_session.add(test_user)
    await db_session.commit()
    await db_session.refresh(test_user)
    
    # Создаем токен
    access_token = create_access_token(data={"sub": str(test_user.id)})
    
    return {"Authorization": f"Bearer {access_token}"}

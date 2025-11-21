# from logging.config import fileConfig
# from sqlalchemy import pool
# from sqlalchemy.ext.asyncio import async_engine_from_config
# from alembic import context
# import sys
# from pathlib import Path
# import asyncio
#
# # Добавляем корневую директорию проекта в sys.path
# sys.path.append(str(Path(__file__).resolve().parents[1]))
#
#
#
#
# if sys.platform.startswith("win"):
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
#
# from app.core.config import settings
# from app.db.base import Base
# # Импортируем все модели, чтобы Alembic мог их обнаружить
# from app.models.user import User
# from app.models.account import Account
# from app.models.transaction import Transaction
# from app.models.category import Category
# from app.models.bank_connection import BankConnection
#
# # this is the Alembic Config object, which provides
# # access to the values within the .ini file in use.
# config = context.config
#
# # Устанавливаем ASYNC URL базы данных из настроек приложения
# config.set_main_option("sqlalchemy.url", settings.ASYNC_DATABASE_URL)
#
# # Interpret the config file for Python logging.
# # This line sets up loggers basically.
# if config.config_file_name is not None:
#     fileConfig(config.config_file_name)
#
# # add your model's MetaData object here
# # for 'autogenerate' support
# target_metadata = Base.metadata
#
#
# def run_migrations_offline() -> None:
#     """Run migrations in 'offline' mode.
#
#     This configures the context with just a URL
#     and not an Engine, though an Engine is acceptable
#     here as well.  By skipping the Engine creation
#     we don't even need a DBAPI to be available.
#
#     Calls to context.execute() here emit the given string to the
#     script output.
#
#     """
#     url = config.get_main_option("sqlalchemy.url")
#     context.configure(
#         url=url,
#         target_metadata=target_metadata,
#         literal_binds=True,
#         dialect_opts={"paramstyle": "named"},
#     )
#
#     with context.begin_transaction():
#         context.run_migrations()
#
#
# def do_run_migrations(connection):
#     """Выполнить миграции с переданным соединением"""
#     context.configure(
#         connection=connection,
#         target_metadata=target_metadata
#     )
#
#     with context.begin_transaction():
#         context.run_migrations()
#
#
# async def run_async_migrations():
#     """Асинхронная функция для выполнения миграций"""
#     connectable = async_engine_from_config(
#         config.get_section(config.config_ini_section, {}),
#         prefix="sqlalchemy.",
#         poolclass=pool.NullPool,
#     )
#
#     async with connectable.connect() as connection:
#         await connection.run_sync(do_run_migrations)
#
#     await connectable.dispose()
#
#
# def run_migrations_online() -> None:
#     """Run migrations in 'online' mode (ASYNC VERSION).
#
#     In this scenario we need to create an Engine
#     and associate a connection with the context.
#
#     """
#     asyncio.run(run_async_migrations())
#
#
# if context.is_offline_mode():
#     run_migrations_offline()
# else:
#     run_migrations_online()


# alembic/env.py
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
import sys
from pathlib import Path
import asyncio

# Добавляем корневую директорию проекта в sys.path
# Путь должен указывать на родительскую директорию fintrek_async (VtbHackathon)
# чтобы можно было импортировать fintrek_async.app
project_root = Path(__file__).resolve().parents[1]  # VtbHackathon
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Фикс для Windows + asyncpg (обязательно!)
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Импортируем настройки и метаданные
# Используем относительные импорты, так как alembic запускается из директории fintrek_async
from app.core.config import settings
from app.db.base import Base

# Импортируем модели (__init__.py теперь поддерживает относительные импорты)
from app.models.user import User
from app.models.account import Account
from app.models.transaction import Transaction
from app.models.category import Category
from app.models.bank_connection import BankConnection

# Alembic Config object
config = context.config

# Логирование
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Метаданные для автогенерации
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Оффлайн-режим (не используется в async)"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Выполнить миграции с синхронным соединением"""
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    """Асинхронные миграции — главная функция"""
    # Берём секцию из .ini
    configuration = config.get_section(config.config_ini_section) or {}

    # ЯВНО ПЕРЕОПРЕДЕЛЯЕМ URL — ГАРАНТИЯ!
    configuration["sqlalchemy.url"] = settings.ASYNC_DATABASE_URL

    # Отладка (можно удалить потом)
    print(f"[Alembic] Using DATABASE URL: {configuration['sqlalchemy.url']}")

    # Создаём async engine с правильным URL
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Запуск в онлайн-режиме (async)"""
    asyncio.run(run_async_migrations())


# Выбор режима
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
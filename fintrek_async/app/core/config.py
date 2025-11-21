"""
Конфигурация приложения
Загружает переменные окружения и предоставляет настройки для всего приложения
"""
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Основные настройки
    PROJECT_NAME: str = Field(default="Финтрек API", description="Название проекта")
    VERSION: str = Field(default="1.0.0", description="Версия API")
    API_V1_STR: str = Field(default="/api/v1", description="Префикс API")
    DEBUG: bool = Field(default=True, description="Режим отладки")
    
    # База данных PostgreSQL
    POSTGRES_SERVER: str = Field(default="localhost", description="Хост PostgreSQL")
    POSTGRES_USER: str = Field(default="myuser", description="Пользователь PostgreSQL")
    POSTGRES_PASSWORD: str = Field(default="mysecretpassword", description="Пароль PostgreSQL")
    POSTGRES_DB: str = Field(default="mydatabase", description="Имя базы данных")
    POSTGRES_PORT: int = Field(default=5432, description="Порт PostgreSQL")

    # VBank API
    VBANK_BASE_URL: str = Field(default="https://vbank.open.bankingapi.ru", description="URL VBank API")
    VBANK_CLIENT_ID: str = Field(default="", description="VBank client id")
    VBANK_CLIENT_SECRET: str = Field(default="", description="VBank client secret")
    VBANK_BANK_CODE: str = Field(default="VBank", description="Код банка VBank")
    
    @property
    def DATABASE_URL(self) -> str:
        """Формирование URL для подключения к БД"""
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def ASYNC_DATABASE_URL(self) -> str:
        """Формирование async URL для подключения к БД"""
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Redis
    REDIS_HOST: str = Field(default="localhost", description="Хост Redis")
    REDIS_PORT: int = Field(default=6379, description="Порт Redis")
    REDIS_DB: int = Field(default=0, description="Номер базы данных Redis")
    
    @property
    def REDIS_URL(self) -> str:
        """Формирование URL для подключения к Redis"""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # JWT настройки
    SECRET_KEY: str = Field(
        default="your-secret-key-change-this-in-production-min-32-chars",
        description="Секретный ключ для JWT",
        min_length=32
    )
    ENCRYPTION_KEY: str = Field(
        default="your-encryption-key-change-this-in-production-min-32-chars",
        description="Ключ для шифрования данных (должен отличаться от SECRET_KEY)",
        min_length=32
    )
    ALGORITHM: str = Field(default="HS256", description="Алгоритм шифрования JWT")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Время жизни access токена в минутах")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="Время жизни refresh токена в днях")
    
    @field_validator("SECRET_KEY")
    @classmethod
    def validate_secret_key(cls, v, info):
        """Проверка что SECRET_KEY изменен в production"""
        if not info.data.get("DEBUG", False):
            if "change-this" in v.lower():
                raise ValueError(
                    "SECRET_KEY must be changed in production! "
                    "Generate a secure key: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                )
        return v
    
    @field_validator("ENCRYPTION_KEY")
    @classmethod
    def validate_encryption_key(cls, v, info):
        """Проверка что ENCRYPTION_KEY изменен и отличается от SECRET_KEY"""
        if not info.data.get("DEBUG", False):
            if "change-this" in v.lower():
                raise ValueError(
                    "ENCRYPTION_KEY must be changed in production! "
                    "Generate a secure key: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                )
            if v == info.data.get("SECRET_KEY"):
                raise ValueError(
                    "ENCRYPTION_KEY must be different from SECRET_KEY for security reasons!"
                )
        return v
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:5173",
            "http://localhost:8000",
            "http://localhost:8080",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:8000",
            "http://127.0.0.1:8080",
        ],
        description="Разрешенные CORS origins"
    )

    BACKEND_CORS_ORIGIN_REGEX: str = Field(
        default=r"^https?://(localhost|127\.0\.0\.1|192\.168\.\d{1,3}\.\d{1,3}|10\.\d{1,3}\.\d{1,3}\.\d{1,3}|172\.(1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3})(:\d+)?$",
        description="Regex для разрешенных CORS origins (для локальной сети)"
    )
    
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Парсинг CORS origins из строки или списка"""
        if isinstance(v, str):
            # Если передана строка, разделяем по запятой
            return [origin.strip() for origin in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        # Позволяет загружать переменные из .env файла
        env_file_encoding = 'utf-8'


# Создаем глобальный экземпляр настроек
settings = Settings()

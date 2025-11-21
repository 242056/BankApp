# 🚀 Инструкция по установке и запуску Финтрек API

## Содержание
1. [Требования](#требования)
2. [Установка](#установка)
3. [Конфигурация](#конфигурация)
4. [Запуск](#запуск)
5. [Проверка работы](#проверка-работы)
6. [Troubleshooting](#troubleshooting)

---

## Требования

### Системные требования
- **Python**: 3.11 или выше
- **PostgreSQL**: 14 или выше
- **Redis**: 6 или выше
- **OS**: macOS, Linux, или Windows (с WSL)

### Проверка версий
```bash
python --version    # Должно быть >= 3.11
psql --version      # Должно быть >= 14
redis-cli --version # Должно быть >= 6
```

---

## Установка

### Шаг 1: Клонирование репозитория

```bash
cd /path/to/your/projects
git clone <repository-url>
cd VtbHackathon
```

### Шаг 2: Создание виртуального окружения

```bash
# Создать виртуальное окружение
python -m venv .venv

# Активировать виртуальное окружение
# macOS/Linux:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate
```

### Шаг 3: Установка зависимостей

```bash
# Обновить pip
pip install --upgrade pip

# Установить зависимости
pip install -r requirements.txt
```

**Ожидаемый результат:**
```
Successfully installed fastapi-0.104.1 uvicorn-0.24.0 ...
```

---

## Конфигурация

### Шаг 1: Настройка PostgreSQL

#### Создание базы данных

```bash
# Войти в PostgreSQL
psql -U postgres

# Создать пользователя и базу данных
CREATE USER myuser WITH PASSWORD 'mysecretpassword';
CREATE DATABASE mydatabase OWNER myuser;
GRANT ALL PRIVILEGES ON DATABASE mydatabase TO myuser;

# Выйти
\q
```

#### Проверка подключения

```bash
psql -h localhost -U myuser -d mydatabase
# Введите пароль: mysecretpassword
```

### Шаг 2: Настройка Redis

#### Запуск Redis

**macOS (Homebrew):**
```bash
brew services start redis
```

**Linux (systemd):**
```bash
sudo systemctl start redis
sudo systemctl enable redis
```

**Docker:**
```bash
docker run -d -p 6379:6379 redis:latest
```

#### Проверка Redis

```bash
redis-cli ping
# Ожидаемый ответ: PONG
```

### Шаг 3: Создание .env файла

```bash
# Скопировать пример
cp .env.example .env

# Отредактировать .env
nano .env  # или используйте любой редактор
```

#### Минимальная конфигурация .env

```bash
# Application
DEBUG=true
PROJECT_NAME=Финтрек API
API_V1_STR=/api/v1

# Database
POSTGRES_SERVER=localhost
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mysecretpassword
POSTGRES_DB=mydatabase
POSTGRES_PORT=5432

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# Security Keys (для разработки можно оставить как есть)
SECRET_KEY=your-secret-key-change-this-in-production-min-32-chars
ENCRYPTION_KEY=your-encryption-key-change-this-in-production-min-32-chars

# JWT
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
BACKEND_CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8000

# VBank API (опционально)
VBANK_BASE_URL=https://vbank.open.bankingapi.ru
VBANK_CLIENT_ID=106
VBANK_CLIENT_SECRET=y70ZIjvCOi3oaTmKQh9qivHFJHTJt3A7
VBANK_BANK_CODE=VBank
```

### Шаг 4: Выполнение миграций базы данных

```bash
# Перейти в директорию с Alembic
cd fintrek_async

# Выполнить миграции
alembic upgrade head

# Вернуться в корень проекта
cd ..
```

**Ожидаемый результат:**
```
INFO  [alembic.runtime.migration] Running upgrade  -> 090c1a402a7e, initial_schema
INFO  [alembic.runtime.migration] Running upgrade 090c1a402a7e -> f05ee718e966, add_vbank_integration_fields
```

---

## Запуск

### Режим разработки

#### Вариант 1: Через uvicorn напрямую

```bash
# Убедитесь что виртуальное окружение активировано
source .venv/bin/activate  # macOS/Linux

# Запустить сервер
uvicorn fintrek_async.app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Вариант 2: Через Python модуль

```bash
python -m uvicorn fintrek_async.app.main:app --reload --host 0.0.0.0 --port 8000
```

**Ожидаемый вывод:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Redis cache initialized successfully
INFO:     Application startup complete
INFO:     Application startup complete.
```

### Режим production

```bash
# Установить DEBUG=false в .env
# Сгенерировать уникальные ключи

# Запустить с Gunicorn
gunicorn fintrek_async.app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

---

## Проверка работы

### 1. Health Check

```bash
curl http://localhost:8000/health
```

**Ожидаемый ответ:**
```json
{"status": "healthy"}
```

### 2. Root Endpoint

```bash
curl http://localhost:8000/
```

**Ожидаемый ответ:**
```json
{
  "message": "Добро пожаловать в Финтрек API",
  "version": "1.0.0",
  "docs": "/docs"
}
```

### 3. API Documentation

Откройте в браузере:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 4. Тестовая регистрация

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!@#",
    "name": "Test User"
  }'
```

**Ожидаемый ответ:**
```json
{
  "id": "...",
  "email": "test@example.com",
  "name": "Test User",
  "subscription_tier": "free",
  "created_at": "..."
}
```

### 5. Тестовый вход

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "email=test@example.com&password=Test123!@#"
```

**Ожидаемый ответ:**
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer"
}
```

---

## Troubleshooting

### Проблема: "ModuleNotFoundError: No module named 'fintrek_async'"

**Решение:**
```bash
# Убедитесь что вы в корневой директории проекта
pwd  # Должно показать .../VtbHackathon

# Убедитесь что виртуальное окружение активировано
which python  # Должно показать путь к .venv1/bin/python

# Переустановите зависимости
pip install -r requirements.txt
```

### Проблема: "connection to server at localhost:5432 failed"

**Решение:**
```bash
# Проверьте что PostgreSQL запущен
# macOS:
brew services list | grep postgresql

# Linux:
sudo systemctl status postgresql

# Запустите PostgreSQL если не запущен
# macOS:
brew services start postgresql

# Linux:
sudo systemctl start postgresql
```

### Проблема: "Error connecting to Redis"

**Решение:**
```bash
# Проверьте что Redis запущен
redis-cli ping

# Если не отвечает, запустите Redis
# macOS:
brew services start redis

# Linux:
sudo systemctl start redis

# Docker:
docker start redis  # или docker run -d -p 6379:6379 redis:latest
```

### Проблема: "column users.failed_login_attempts does not exist"

**Решение:**
```bash
# Выполните миграции
cd fintrek_async
alembic upgrade head
cd ..
```

### Проблема: "SECRET_KEY must be changed in production"

**Решение:**
```bash
# Установите DEBUG=true в .env для разработки
echo "DEBUG=true" >> .env

# Или сгенерируйте уникальные ключи для production
python -c 'import secrets; print(secrets.token_urlsafe(32))'
# Скопируйте результат в .env как SECRET_KEY

python -c 'import secrets; print(secrets.token_urlsafe(32))'
# Скопируйте результат в .env как ENCRYPTION_KEY
```

### Проблема: Rate limit exceeded (429 ошибка)

**Причина:** Слишком много запросов

**Решение:**
- Подождите 1 минуту
- Или увеличьте лимиты в `main.py` (для разработки)

### Проблема: "Redis connection failed. Running without cache"

**Это не ошибка!** Приложение работает без кэша если Redis недоступен.

**Если хотите включить кэш:**
```bash
# Запустите Redis
brew services start redis  # macOS
sudo systemctl start redis # Linux
```

---

## Дополнительные команды

### Создание новой миграции

```bash
cd fintrek_async
alembic revision --autogenerate -m "описание изменений"
alembic upgrade head
cd ..
```

### Откат миграции

```bash
cd fintrek_async
alembic downgrade -1  # Откатить одну миграцию
cd ..
```

### Запуск тестов

```bash
pytest
pytest --cov=app tests/  # С coverage
```

### Очистка кэша Python

```bash
find . -type d -name __pycache__ -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

---

## Полезные ссылки

- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **Root**: http://localhost:8000/

---

## Следующие шаги

После успешного запуска:

1. **Изучите API** через Swagger UI
2. **Создайте тестового пользователя**
3. **Попробуйте создать счет и транзакции**
4. **Протестируйте AI insights**
5. **Настройте VBank интеграцию** (опционально)

---

## Поддержка

Если возникли проблемы:
1. Проверьте логи сервера
2. Убедитесь что PostgreSQL и Redis запущены
3. Проверьте .env конфигурацию
4. Посмотрите раздел [Troubleshooting](#troubleshooting)


---

**Успешного запуска! 🚀**

# 📊 Финтрек API - Интеллектуальная платформа для управления личными финансами

## Описание проекта

**Финтрек** - это современная платформа для управления личными финансами с интеграцией Open Banking API и AI-powered аналитикой. Проект разработан на FastAPI с асинхронной архитектурой для максимальной производительности.

### Ключевые возможности

- 🔐 **Безопасная аутентификация** - JWT токены, bcrypt хеширование, account lockout
- 💳 **Управление счетами** - Поддержка множественных банковских счетов
- 📈 **Транзакции** - Учет доходов и расходов с автоматической категоризацией
- 🏦 **Open Banking** - Интеграция с VBank API для синхронизации данных
- 🤖 **AI Аналитика** - Умные рекомендации и прогнозы на основе ML
- 📊 **Аналитика** - Детальная статистика расходов и доходов
- 🔄 **Real-time синхронизация** - Автоматическое обновление данных из банков
- 🛡️ **Enterprise Security** - Rate limiting, HTTPS enforcement, security headers

---

## Архитектура проекта

### Технологический стек

**Backend:**
- **FastAPI** 0.104+ - Современный async web framework
- **SQLAlchemy** 2.0+ - ORM с async поддержкой
- **PostgreSQL** - Основная база данных
- **Redis** - Кэширование и rate limiting
- **Alembic** - Миграции базы данных

**Security:**
- **JWT** - Аутентификация и авторизация
- **bcrypt** - Хеширование паролей
- **slowapi** - Rate limiting и DDoS защита
- **Fernet** - Шифрование токенов

**ML/AI:**
- Собственные алгоритмы категоризации транзакций
- Прогнозирование расходов
- Детекция аномалий
- Персонализированные рекомендации

---

## Структура проекта

```
VtbHackathon/
├── fintrek_async/              # Основное приложение
│   ├── alembic/                # Миграции базы данных
│   │   ├── versions/           # История миграций
│   │   └── env.py              # Конфигурация Alembic
│   │
│   ├── app/                    # Код приложения
│   │   ├── api/                # API endpoints
│   │   │   └── v1/
│   │   │       ├── endpoints/  # Роутеры
│   │   │       │   ├── auth.py           # Аутентификация
│   │   │       │   ├── accounts.py       # Управление счетами
│   │   │       │   ├── transactions.py   # Транзакции
│   │   │       │   ├── categories.py     # Категории
│   │   │       │   ├── analytics.py      # Аналитика
│   │   │       │   ├── ai_insights.py    # AI рекомендации
│   │   │       │   ├── bank_connections.py # Open Banking
│   │   │       │   ├── vbank.py          # VBank интеграция
│   │   │       │   └── users.py          # Управление пользователями
│   │   │       ├── api.py      # Главный роутер
│   │   │       └── deps.py     # Зависимости (get_current_user)
│   │   │
│   │   ├── clients/            # HTTP клиенты
│   │   │   └── vbank.py        # VBank API клиент
│   │   │
│   │   ├── core/               # Ядро приложения
│   │   │   ├── config.py       # Конфигурация (Pydantic Settings)
│   │   │   ├── security.py     # JWT, bcrypt, шифрование
│   │   │   ├── cache.py        # Redis кэширование
│   │   │   ├── exceptions.py   # Кастомные исключения
│   │   │   └── password_validator.py # Валидация паролей
│   │   │
│   │   ├── db/                 # База данных
│   │   │   ├── base.py         # Базовая модель
│   │   │   └── session.py      # Async сессии
│   │   │
│   │   ├── middleware/         # Middleware
│   │   │   └── security.py     # Security headers
│   │   │
│   │   ├── ml/                 # Machine Learning
│   │   │   ├── transaction_categorizer.py  # Категоризация
│   │   │   ├── spending_analyzer.py        # Анализ расходов
│   │   │   ├── recommendation_engine.py    # Рекомендации
│   │   │   └── forecasting_model.py        # Прогнозирование
│   │   │
│   │   ├── models/             # SQLAlchemy модели
│   │   │   ├── user.py         # Пользователь
│   │   │   ├── account.py      # Счет
│   │   │   ├── transaction.py  # Транзакция
│   │   │   ├── category.py     # Категория
│   │   │   └── bank_connection.py # Банковское подключение
│   │   │
│   │   ├── schemas/            # Pydantic схемы
│   │   │   ├── user.py         # User schemas
│   │   │   ├── account.py      # Account schemas
│   │   │   ├── transaction.py  # Transaction schemas
│   │   │   ├── category.py     # Category schemas
│   │   │   ├── token.py        # Token schemas
│   │   │   └── bank_connection.py # BankConnection schemas
│   │   │
│   │   ├── services/           # Бизнес-логика
│   │   │   ├── open_banking_service.py # Open Banking
│   │   │   ├── sync_service.py         # Синхронизация
│   │   │   └── vbank_import.py         # VBank импорт
│   │   │
│   │   └── main.py             # Точка входа приложения
│   │
│   ├── scripts/                # Утилиты
│   ├── tests/                  # Тесты
│   ├── alembic.ini             # Конфигурация Alembic
│   └── pytest.ini              # Конфигурация pytest
│
├── VTB/                        # Frontend (не трогаем)
│
├── .env.example                # Пример конфигурации
├── .gitignore                  # Git ignore
├── requirements.txt            # Python зависимости
└── README.md                   # Этот файл
```

---

## Основные компоненты

### 1. API Endpoints

#### Аутентификация (`/api/v1/auth`)
- `POST /register` - Регистрация пользователя
- `POST /login` - Вход (rate limit: 5/min)
- `POST /refresh` - Обновление токена

#### Счета (`/api/v1/accounts`)
- `GET /` - Список счетов
- `POST /` - Создать счет
- `GET /{id}` - Детали счета
- `PUT /{id}` - Обновить счет
- `DELETE /{id}` - Удалить счет

#### Транзакции (`/api/v1/transactions`)
- `GET /` - Список транзакций (с фильтрацией)
- `POST /` - Создать транзакцию
- `GET /{id}` - Детали транзакции
- `PUT /{id}` - Обновить транзакцию
- `DELETE /{id}` - Удалить транзакцию

#### AI Insights (`/api/v1/ai-insights`)
- `GET /recommendations` - Персональные рекомендации
- `GET /forecast` - Прогноз расходов
- `GET /anomalies` - Детекция аномалий
- `GET /financial-health` - Оценка финансового здоровья

#### VBank Integration (`/api/v1/vbank`)
- `POST /sync-accounts` - Синхронизация счетов (rate limit: 10/min)
- `POST /sync-transactions` - Синхронизация транзакций

### 2. ML Модули

**Transaction Categorizer**
- Автоматическая категоризация транзакций
- Обучение на исторических данных
- Поддержка пользовательских правил

**Spending Analyzer**
- Анализ паттернов расходов
- Детекция рекуррентных платежей
- Выявление аномалий

**Recommendation Engine**
- Персонализированные советы
- Анализ финансового поведения
- Проактивные уведомления

**Forecasting Model**
- Прогноз расходов на месяц
- Прогноз доходов
- Прогноз баланса

### 3. Security Features

**Authentication & Authorization**
- JWT access tokens (30 min)
- JWT refresh tokens (7 days)
- Password strength validation
- Account lockout (5 attempts / 15 min)

**Network Security**
- HTTPS enforcement (production)
- Security headers (CSP, X-Frame-Options, etc.)
- CORS configuration
- Trusted host middleware

**DDoS Protection**
- Rate limiting (slowapi)
- Redis-backed distributed limiting
- Per-endpoint limits

**Data Protection**
- Separate encryption keys (JWT vs data)
- bcrypt password hashing
- SQL injection protection (ORM)
- Input validation (Pydantic)

---

## База данных

### Схема

**Users**
- id, email, password_hash, name
- subscription_tier
- failed_login_attempts, locked_until (security)
- created_at, updated_at

**Accounts**
- id, user_id, bank_connection_id
- name, account_number, account_type
- balance, available_balance
- currency, status
- external_id, provider (VBank)

**Transactions**
- id, user_id, account_id, category_id
- transaction_type, amount, currency
- description, merchant_name
- transaction_date, posted_date
- status, external_id
- category_guess, provider (VBank)

**Categories**
- id, user_id, parent_id
- name, category_type, icon
- is_system (предустановленные)

**BankConnections**
- id, user_id, provider
- access_token (encrypted), refresh_token (encrypted)
- token_expires_at, status
- last_synced_at, last_error

---

## API Documentation

После запуска сервера доступна интерактивная документация:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/api/v1/openapi.json

---

## Производительность

**Асинхронная архитектура:**
- Все I/O операции асинхронные
- Connection pooling для БД
- Redis для кэширования
- Оптимизированные SQL запросы

**Кэширование:**
- Результаты аналитики
- Категории
- Пользовательские настройки

**Rate Limiting:**
- Защита от перегрузки
- Graceful degradation

---

## Мониторинг и логирование

**Логирование:**
- Все попытки входа
- Блокировки аккаунтов
- Ошибки API
- Rate limit violations

**Рекомендуемые инструменты:**
- Sentry - error tracking
- Prometheus - метрики
- Grafana - визуализация

---

## Разработка

### Требования
- Python 3.11+
- PostgreSQL 14+
- Redis 6+

### Запуск в dev режиме
См. [INSTALLATION.md](INSTALLATION.md)

### Тестирование
```bash
pytest
pytest --cov=app tests/
```

### Миграции
```bash
cd fintrek_async
alembic revision --autogenerate -m "description"
alembic upgrade head
```

---

## Production Deployment

**Checklist:**
- [ ] Set `DEBUG=false`
- [ ] Generate unique `SECRET_KEY` and `ENCRYPTION_KEY`
- [ ] Configure `allowed_hosts` in TrustedHostMiddleware
- [ ] Set up HTTPS
- [ ] Configure CORS origins
- [ ] Set up monitoring (Sentry, Prometheus)
- [ ] Configure backups
- [ ] Set up CI/CD

---

## Лицензия

MIT License

---

## Контакты

- Email: support@fintrek.com
- Security: security@fintrek.com

---

## Changelog

### v1.0.0 (2025-11-21)
- ✅ Базовая функциональность
- ✅ VBank интеграция
- ✅ AI/ML модули
- ✅ Enterprise security
- ✅ Rate limiting
- ✅ Comprehensive error handling

# 🚀 Быстрый запуск Fullstack (Frontend + Backend)

## Ваш стек

- **Backend**: FastAPI (Python) на порту 8000
- **Frontend**: Vite + React + TypeScript + Shadcn UI на порту 5173
- **Database**: PostgreSQL
- **Cache**: Redis

## Предварительные требования

Перед запуском убедитесь, что у вас установлены:
1. **Python 3.11+**
2. **Node.js 18+** (для запуска фронтенда)
   - Проверить: `node -v`
   - Скачать: [nodejs.org](https://nodejs.org)

---

## Запуск за 3 шага

### Шаг 1: Запуск Backend

```bash
# Терминал 1
cd /Users/andrejivanov/PycharmProjects/VtbHackathon

# Активировать виртуальное окружение
source .venv/bin/activate

# Запустить backend
uvicorn fintrek_async.app.main:app --reload --host 0.0.0.0 --port 8000
```

**Проверка:**
```bash
curl http://localhost:8000/health
# Ожидаемый ответ: {"status":"healthy"}
```

### Шаг 2: Запуск Frontend

```bash
# Терминал 2
cd /Users/andrejivanov/PycharmProjects/VtbHackathon/fintrek_async/VTB

# Установить зависимости (первый раз)
npm install

# Запустить dev сервер
npm run dev
```

**Результат:**
```
VITE v5.4.19  ready in 500 ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

### Шаг 3: Открыть в браузере

Откройте: **http://localhost:5173**

---

## Проверка связи Frontend ↔ Backend

Frontend уже настроен на правильный API URL:
```
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

**Тест в DevTools (F12 → Console):**
```javascript
fetch('http://localhost:8000/api/v1/health')
  .then(res => res.json())
  .then(data => console.log(data))
```

---

## Доступные URL

| Сервис | URL | Описание |
|--------|-----|----------|
| Frontend | http://localhost:5173 | React приложение |
| Backend API | http://localhost:8000 | FastAPI сервер |
| API Docs | http://localhost:8000/docs | Swagger UI |
| ReDoc | http://localhost:8000/redoc | Alternative docs |
| Health Check | http://localhost:8000/health | Проверка здоровья |

---

## Полезные команды

### Backend:
```bash
# Остановить: Ctrl+C
# Логи в реальном времени
tail -f logs/app.log

# Миграции
cd fintrek_async && alembic upgrade head && cd ..
```

### Frontend:
```bash
# Build для production
npm run build

# Preview production build
npm run preview

# Lint
npm run lint
```

---

## Troubleshooting

### Проблема: Frontend показывает ошибку сети

**Решение:**
1. Убедитесь что backend запущен: `curl http://localhost:8000/health`
2. Проверьте CORS в backend `.env`:
   ```
   BACKEND_CORS_ORIGINS=http://localhost:5173
   ```
3. Перезапустите backend

### Проблема: Порт 5173 занят

**Решение:**
```bash
# Найти процесс
lsof -ti:5173

# Убить процесс
kill -9 $(lsof -ti:5173)

# Или использовать другой порт
npm run dev -- --port 3000
```

### Проблема: npm install не работает

**Решение:**
```bash
# Очистить кэш
rm -rf node_modules package-lock.json
npm install

# Или использовать bun (быстрее)
bun install
bun run dev
```

---

## Production Build

### Backend:
```bash
# Установить gunicorn
pip install gunicorn

# Запустить
gunicorn fintrek_async.app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Frontend:
```bash
cd fintrek_async/VTB

# Build
npm run build

# Результат в dist/
ls -la dist/

# Serve с nginx или другим web сервером
```

---

**Готово! Теперь у вас работает fullstack приложение! 🎉**

# System Monitoring

Сбор метрик с удалённых машин, хранение в БД, детекция инцидентов, UI + SSE-обновления.

## Стек

- **Django 5** (API, UI, ORM)
- **Celery 5** + **Redis** (очереди, планировщик)
- **MySQL 8** (данные)
- **HTTPX** (сбор метрик)
- **SSE** (реалтайм обновление UI)
- **uv**, **ruff** (окружение и линтер)
- **Docker Compose** (Redis и MySQL)

---

## Быстрый старт (локально)

1. Установить зависимости:

```bash
make install
```

2. Поднять СУБД и Redis в Docker (Colima/Docker Desktop должны быть запущены):

```bash
make docker
```

3. Применить миграции:

```bash
make migrate
```

4. Создать пользователя для входа в UI (`demo/demo`):

```bash
make login-demo
```

5. Запустить процессы в отдельных терминалах:

```bash
# мок-сервер метрик (порт 9001)
make main

# веб-сервер Django (порт 8000)
make server

# Celery worker
make celery
```

6. Открыть UI:

- `http://127.0.0.1:8000/ui/login` → логин `demo`, пароль `demo`
- `http://127.0.0.1:8000/ui/incidents`

---

## Наблюдение за инцидентами (готовые сценарии)

**Поднять нагрузку (CPU > 85%) на все машины, собрать метрики и посчитать инциденты:**

```bash
make spike
make collect-now
make evaluate
```

**Снять нагрузку, собрать и пересчитать (чтобы инциденты исчезли/закрылись):**

```bash
make calm
make collect-now
make evaluate
```

---

## Маршруты

### UI

- `/ui/login` — логин (cookie-based, простой токен)
- `/ui/incidents` — таблица инцидентов (галка **Only active**, SSE + автополлинг)

### API

- `GET /api/incidents?active=true|false` — список инцидентов (JSON: `{ total, items: [...] }`)
- `GET /api/incidents/stream` — SSE-поток (server-sent events)

### Admin

- `/admin` — стандартная админка Django

---

## Переменные окружения (.env пример)

```dotenv
DJANGO_SECRET_KEY=dev-only

DB_NAME=system_monitoring
DB_USER=app
DB_PASSWORD=app_pass
DB_HOST=127.0.0.1
DB_PORT=3306

CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0

REQUEST_CONNECT_TIMEOUT=3.0
REQUEST_READ_TIMEOUT=8.0
RETRY_LIMIT=3
```

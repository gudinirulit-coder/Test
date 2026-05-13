# Test Time API

Простой бэкенд на **FastAPI**: время и дата сервера в JSON. Подходит для отработки Docker и деплоя через GitHub Actions.

## Требования

- Python 3.10+ (локально)
- Docker (опционально)

## Локальный запуск

```bash
python -m pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Документация OpenAPI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Эндпоинты

| Метод | Путь | Описание |
|--------|------|----------|
| GET | `/` | Краткая справка по маршрутам |
| GET | `/time` | Текущее время в UTC (`utc`, `unix`) |
| GET | `/date` | Дата по календарю UTC |
| GET | `/date/local` | Дата в локальной зоне сервера |

## Docker

Сборка и запуск:

```bash
docker build -t time-api .
docker run --rm -p 8000:8000 time-api
```

Приложение слушает порт **8000**.

## CI/CD (GitHub Actions)

Файл [`.github/workflows/build-push-deploy.yml`](.github/workflows/build-push-deploy.yml):

1. Собирает образ и пушит в **GitHub Container Registry** (`ghcr.io/<владелец>/<репозиторий>:latest`).
2. По **SSH** подключается к серверу, делает `docker pull` и запускает контейнер `time-api` с пробросом `8000:8000`.

Триггеры: push в ветки `main` / `master` и ручной запуск **workflow_dispatch**. Список веток меняется в секции `on.push.branches` в YAML.

Секреты и нюансы (SSH, GHCR login для приватных образов) описаны в комментариях в начале того же workflow-файла.

## Структура репозитория

| Файл | Назначение |
|------|------------|
| `main.py` | Приложение FastAPI |
| `requirements.txt` | Зависимости Python |
| `Dockerfile` | Образ приложения |
| `.dockerignore` | Исключения для контекста сборки |
| `.gitignore` | Исключения для Git |

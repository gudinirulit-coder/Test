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

### Требования к серверу для деплоя

На машине, к которой подключается SSH, должны выполняться условия ниже. Иначе в логах Actions появится `docker: command not found` (код выхода 127).

1. **Установлен Docker Engine** (CLI `docker` в `PATH` в неинтерактивной SSH-сессии). Установка: официальная инструкция для вашей ОС, например [Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/).
2. Пользователь из секрета **`SSH_USER`** может выполнять `docker` без пароля: либо вход в группу `docker` (`sudo usermod -aG docker "$USER"` и перелогин), либо деплой под пользователем `root` (не рекомендуется без необходимости).

Проверка с вашего ПК:

```bash
ssh -i /путь/к/ключу SSH_USER@SSH_HOST "docker --version"
```

Должна вывестись версия Docker, без запроса пароля и без «permission denied» на сокет.

**`GITHUB_TOKEN`** для пуша в GHCR из Actions создавать не нужно: GitHub выдаёт его на время запуска workflow (в файле задано `permissions: packages: write`).

### Как добавить секреты для этого проекта

1. Откройте репозиторий на GitHub.
2. Перейдите в **Settings** (настройки репозитория).
3. В левом меню: **Secrets and variables** → **Actions**.
4. Вкладка **Secrets**: нажмите **New repository secret**.
5. В поле **Name** введите имя секрета **точно** как в таблице ниже (регистр важен). В **Secret** вставьте значение → **Add secret**.

Повторите шаги 4–5 для каждого нужного секрета.

| Имя секрета | Обязателен? | Что указать в значении |
|-------------|-------------|-------------------------|
| `SSH_HOST` | Да (для деплоя) | IP или домен сервера, например `203.0.113.10` или `deploy.example.com`. |
| `SSH_USER` | Да | Пользователь Linux для SSH (тот же, под которым на сервере доступен Docker). |
| `SSH_PRIVATE_KEY` | Да | Содержимое **приватного** SSH-ключа (весь блок от `-----BEGIN ... PRIVATE KEY-----` до `-----END ... PRIVATE KEY-----`, включая переносы строк). Обычно это файл `id_ed25519` или `id_rsa` на вашей машине — **не** коммитьте его в репозиторий. На сервере в `~/.ssh/authorized_keys` должен быть соответствующий **публичный** ключ. |
| `GHCR_USER` | Только для приватного образа | Логин GitHub, для которого вы выпустили токен ниже (часто ваш ник на GitHub). |
| `GHCR_TOKEN` | Только для приватного образа | [Personal access token](https://github.com/settings/tokens): для **classic** PAT включите scope **`read:packages`**. На сервере он используется в `docker login ghcr.io` перед `docker pull`. |

Если пакет в GHCR **публичный**, секреты `GHCR_USER` и `GHCR_TOKEN` можно **не** создавать: в workflow блок `docker login` не выполнится, а `docker pull` сработает без входа.

### Токен для приватного пакета GHCR (кратко)

1. GitHub → **Settings** (ваш профиль) → **Developer settings** → **Personal access tokens**.
2. Создайте токен (classic) с правом **`read:packages`**.
3. Сохраните токен в репозитории как секрет **`GHCR_TOKEN`**, логин — как **`GHCR_USER`**.

Первый пуш образа в GHCR может потребовать принять политику пакетов в интерфейсе GitHub (страница пакета в разделе **Packages**).

Дополнительные пояснения по SSH и нестандартному порту — в комментариях в начале файла [`.github/workflows/build-push-deploy.yml`](.github/workflows/build-push-deploy.yml).

## Структура репозитория

| Файл | Назначение |
|------|------------|
| `main.py` | Приложение FastAPI |
| `requirements.txt` | Зависимости Python |
| `Dockerfile` | Образ приложения |
| `.dockerignore` | Исключения для контекста сборки |
| `.gitignore` | Исключения для Git |

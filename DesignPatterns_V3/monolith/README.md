# Монолитный стек анализа аэрофотоснимков

## Обзор
Данный каталог содержит монолитную серверную реализацию, повторяющую
функциональность настольного приложения (`OLD/main.py`) и описанную в
`ARCHITECTURE.md`. Стек включает:
- Flask REST API (`app/`) с сущностями `Imagery`, `AnalysisRun`, `Heatmap`, `Report`
- Celery задачи (`tasks/`) для анализа изображений и генерации PDF-отчётов
- SQLAlchemy/SQLite (по умолчанию) с возможностью переключения на Postgres
- Хранилище файлов (локальное по умолчанию, легко заменить на MinIO)

## Быстрый старт (локально)
```bash
cd OLD/monolith
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export FLASK_APP=manage.py
flask init-db      # создаёт таблицы
python run.py      # запускает Flask (http://127.0.0.1:5000)
celery -A OLD.monolith.celery_app.celery_app worker --loglevel=info
```
Для отладки можно включить синхронное выполнение задач:
`export CELERY_TASK_ALWAYS_EAGER=1`.

## Docker Compose
`docker-compose.yml` поднимает web, worker, beat, Redis, Postgres и MinIO.
Команда:
```bash
docker compose up --build
```

## Ключевые эндпоинты
- `POST /imagery` – загрузка снимка (`multipart/form-data`, поле `file`, опционально `captured_at`, `gps_lat`, `gps_lon`).
- `GET /imagery`, `GET /imagery/<id>` – список и детальная информация.
- `POST /analysis-runs` – запуск анализа (json: `imagery_id`, `index_type`, `auto_report`).
- `GET /analysis-runs/<id>` – статус задачи и метрики.
- `POST /reports` – ручная генерация отчёта для готового анализа.
- `GET /reports/<id>` – детали и путь к PDF.

## Структура каталогов
```
app/                # Flask приложение, модели, роуты и сервисы
tasks/              # Celery задачи
storage/            # Локальное файловое хранилище (изображения/теплокарты/отчёты)
run.py              # Запуск dev-сервера
manage.py           # Flask CLI (migrate, shell)
celery_app.py       # Инициализация Celery с контекстом Flask
docker-compose.yml  # Инфраструктура (web + worker + Redis + Postgres + MinIO)
```

## Поток данных
1. `POST /imagery` сохраняет файл и создаёт запись `Imagery`.
2. `POST /analysis-runs` добавляет `AnalysisRun` и ставит в очередь Celery-задачу `run_analysis_task`.
3. Задача использует `OLD.image_processing` и `OLD.utils` для расчёта индексов/теплокарт, записывает `Heatmap`, обновляет статистику по зонам.
4. Если `auto_report=true`, планируется `generate_report_task`, который собирает PDF с исходником, тепловой картой и текстовым отчётом.

## Настройки окружения
См. `env.example` – основные переменные:
- `DATABASE_URL` – строка подключения SQLAlchemy
- `STORAGE_ROOT` – путь к локальному хранилищу
- `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`
- `MINIO_*` – параметры для перехода на MinIO (по умолчанию локальный диск)

## Тестовые сценарии
- `tests/local/http` – curl/postman коллекции (TODO).
Пока покрытие тестами отсутствует; рекомендуется начать с e2e через API.



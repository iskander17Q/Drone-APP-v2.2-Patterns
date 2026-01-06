import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_SQLITE = BASE_DIR / "monolith.db"


class Config:
    """Базовая конфигурация Flask/Celery."""

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"sqlite:///{DEFAULT_SQLITE}"
    )
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    STORAGE_ROOT = os.getenv("STORAGE_ROOT", str(BASE_DIR / "storage"))

    MAX_CONTENT_LENGTH = 512 * 1024 * 1024  # 512 MB

    CELERY_BROKER_URL = os.getenv(
        "CELERY_BROKER_URL", "redis://localhost:6379/0"
    )
    CELERY_RESULT_BACKEND = os.getenv(
        "CELERY_RESULT_BACKEND", "redis://localhost:6379/1"
    )
    CELERY_TASK_ALWAYS_EAGER = os.getenv("CELERY_TASK_ALWAYS_EAGER", "0") == "1"

    REPORT_LOCALE = os.getenv("REPORT_LOCALE", "ru")

    MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
    MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
    MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
    MINIO_BUCKET = os.getenv("MINIO_BUCKET")
    MINIO_SECURE = os.getenv("MINIO_SECURE", "0") == "1"


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    CELERY_TASK_ALWAYS_EAGER = True


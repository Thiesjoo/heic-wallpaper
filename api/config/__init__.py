import os


class CeleryConfig:
    CELERY_BROKER_URL = os.environ.get("BROKER_URL")
    CELERY_RESULT_BACKEND = os.environ.get("BROKER_URL")


class AppConfig:
    UPLOAD_FOLDER = "/static/uploads"
    PROCESSED_FOLDER = "/static/processed"
    DATABASE_URL = "test"

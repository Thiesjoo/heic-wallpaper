class CeleryConfig:
    CELERY_BROKER_URL = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND = "redis://redis:6379/0"


class AppConfig:
    UPLOAD_FOLDER = "/static/uploads"
    DATABASE_URL = "test"

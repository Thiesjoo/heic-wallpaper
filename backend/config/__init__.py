import os
from dotenv import load_dotenv

load_dotenv()


class CeleryConfig:
    CELERY_BROKER_URL = os.environ.get("BROKER_URL")
    CELERY_RESULT_BACKEND = os.environ.get("BROKER_URL")

class DatabaseConfig:
    DATABASE_URL = os.environ.get("DATABASE_URL")


class AppConfig:
    UPLOAD_S3_URL = os.environ.get("UPLOAD_S3_URL")
    UPLOAD_S3_BUCKET = os.environ.get("UPLOAD_S3_BUCKET")
    UPLOAD_S3_ACCESS_KEY = os.environ.get("UPLOAD_S3_ACCESS_KEY")
    UPLOAD_S3_SECRET_KEY = os.environ.get("UPLOAD_S3_SECRET_KEY")
    
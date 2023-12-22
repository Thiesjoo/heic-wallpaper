import os
from dotenv import load_dotenv

load_dotenv()


class CeleryConfig:
    CELERY_BROKER_URL = os.environ.get("BROKER_URL")
    CELERY_RESULT_BACKEND = os.environ.get("BROKER_URL")

class DatabaseConfig:
    DATABASE_URL = os.environ.get("DATABASE_URL")


class S3Config:
    def __init__(self, name):
        self.name = name
        self.S3_URL = os.environ.get(f"{name}_S3_URL")
        self.BUCKET = os.environ.get(f"{name}_S3_BUCKET")
        self.S3_ACCESS_KEY = os.environ.get(f"{name}_S3_ACCESS_KEY")
        self.S3_SECRET_KEY = os.environ.get(f"{name}_S3_SECRET_KEY")

class AppConfig:
    UPLOAD = S3Config("UPLOAD")
    RESULT = S3Config("RESULT")

    PUBLIC_URL = os.environ.get("PUBLIC_URL")
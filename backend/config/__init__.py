import os
from dotenv import load_dotenv

load_dotenv()


class CeleryConfig:
    CELERY_BROKER_URL = os.environ.get("BROKER_URL")
    CELERY_RESULT_BACKEND = os.environ.get("BROKER_URL")

class DatabaseConfig:
    DATABASE_URL = os.environ.get("DATABASE_URL", None)

    MAX_AGE_FOR_PENDING = 60 * 60  # 1h
    CLEANUP_INTERVAL = 30  # 30s

    @staticmethod
    def validate():
        if DatabaseConfig.DATABASE_URL is None :
            raise ValueError("DATABASE_URL is required")

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
    PUBLIC_ASSET_URL = os.environ.get("PUBLIC_ASSET_URL")
    AUTHENTIK_TOKEN = os.environ.get("AUTHENTIK_TOKEN")
    AUTHENTIK_API_URL = os.environ.get("AUTHENTIK_API_URL")
    AUTHENTIK_CLIENT_ID = os.environ.get("AUTHENTIK_CLIENT_ID")

    @staticmethod
    def validate():
        for s3 in [AppConfig.UPLOAD, AppConfig.RESULT]:
            for attr in ["S3_URL", "BUCKET", "S3_ACCESS_KEY", "S3_SECRET_KEY"]:
                if getattr(s3, attr) is None:
                    raise ValueError(f"{attr} is required for {s3.name}")
        if AppConfig.PUBLIC_URL is None:
            raise ValueError("PUBLIC_URL is required")
        if AppConfig.PUBLIC_ASSET_URL is None:
            raise ValueError("PUBLIC_ASSET_URL is required")
        if AppConfig.AUTHENTIK_TOKEN is None:
            raise ValueError("AUTHENTIK_TOKEN is required")
        if AppConfig.AUTHENTIK_API_URL is None:
            raise ValueError("AUTHENTIK_API_URL is required")

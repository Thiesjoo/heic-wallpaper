from uuid import uuid4

import boto3
from django.conf import settings

from wallpaper.models import WallpaperType

import logging

logging.info("S3 Service init, connecting to S3")

s3_uploads = boto3.client('s3',
                          endpoint_url= settings.CONFIG.UPLOAD.S3_URL,
                          config=boto3.session.Config(signature_version='s3v4'),
                          aws_access_key_id= settings.CONFIG.UPLOAD.S3_ACCESS_KEY,
                          aws_secret_access_key= settings.CONFIG.UPLOAD.S3_SECRET_KEY,
                          region_name=settings.CONFIG.UPLOAD.S3_REGION
                          )

s3_results = boto3.client('s3',
                          endpoint_url= settings.CONFIG.RESULT.S3_URL,
                          config=boto3.session.Config(signature_version='s3v4'),
                          aws_access_key_id= settings.CONFIG.RESULT.S3_ACCESS_KEY,
                          aws_secret_access_key= settings.CONFIG.RESULT.S3_SECRET_KEY,
                          region_name=settings.CONFIG.RESULT.S3_REGION
                          )


logging.info("S3 Service init done")

ALLOWED_EXTENSIONS = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "heic": "image/heic",
}

def get_extension(filename):
    return filename.rsplit(".", 1)[1].lower()


def determine_type_from_extension(extension):
    if extension == "heic":
        return WallpaperType.TIME_BASED
    else:
        return WallpaperType.GENERIC


def allowed_file(filename):
    return "." in filename and get_extension(filename) in ALLOWED_EXTENSIONS


DEFAULT_MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ADMIN_MAX_FILE_SIZE = 1024 * 1024 * 1024 # 1Gi

def get_presigned_post_url(file_type: str, max_file_size) -> (dict, str):
    uid = str(uuid4())

    return s3_uploads.generate_presigned_post(
        Bucket=settings.CONFIG.UPLOAD.BUCKET,
        Key=uid,
        Fields={
            "Content-Type": file_type
        },
        Conditions=[
            {"Content-Type": file_type},
            ["content-length-range", 1, max_file_size]
        ],
        ExpiresIn=3600
    ), uid

def file_exists(key: str):
    try:
        s3_uploads.head_object(Bucket=settings.CONFIG.UPLOAD.BUCKET, Key=key)
        return True
    except Exception as e:
        return False

def remove_all_references(key: str):
    try:
        s3_uploads.delete_object(Bucket=settings.CONFIG.UPLOAD.BUCKET, Key=key)
    except Exception as e:
        pass
    try:
        s3_results.delete_object(Bucket=settings.CONFIG.RESULT.BUCKET, Key=key)
    except Exception as e:
        pass
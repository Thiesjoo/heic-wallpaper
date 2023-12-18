import gc
import os
import shutil
import json

import time
from typing import Any

import boto3
from celery import Celery, group

from backend import image
from backend.database.redis import (
    WallpaperStatus,
    WallpaperType,
    update_data_of_wallpaper,
    update_status_of_wallpaper,
)

from backend.config import AppConfig, CeleryConfig
import backend.heic as heic

# Initialize Celery
celery = Celery(
    "worker",
    broker=CeleryConfig.CELERY_BROKER_URL,
    backend=CeleryConfig.CELERY_RESULT_BACKEND,
    include=["backend"]
)

s3_uploads = boto3.client('s3',
                          endpoint_url=AppConfig.UPLOAD.S3_URL,
                          config=boto3.session.Config(signature_version='s3v4'),
                          aws_access_key_id=AppConfig.UPLOAD.S3_ACCESS_KEY,
                          aws_secret_access_key=AppConfig.UPLOAD.S3_SECRET_KEY,
                          )

s3_results = boto3.client('s3',
                          endpoint_url=AppConfig.RESULT.S3_URL,
                          config=boto3.session.Config(signature_version='s3v4'),
                          aws_access_key_id=AppConfig.RESULT.S3_ACCESS_KEY,
                          aws_secret_access_key=AppConfig.RESULT.S3_SECRET_KEY,
                          )


def finish(key: str) -> None:
    print(f"Removing uploaded file: {key}")
    s3_uploads.delete_object(Bucket=AppConfig.UPLOAD.S3_BUCKET, Key=str)


@celery.task()
def heic_generate_single_image(fname: str, uid: str, idx: int):


@celery.task()
def heic_generate_preview(fname: str, uid: str):
    heic.generate_preview(fname, uid)


@celery.task()
def generate_preview(key: str, uid: str):
    img = image.open_image(s3_uploads, key)
    image.generate_preview(s3_results, img, uid)


@celery.task()
def generate_single_image(key: str, uid: str):
    img = image.open_image(s3_uploads, key)
    image.generate_normal_image(s3_results, img, uid, 0)


@celery.task()
def finish_processing(prev_results, key: str, uid: str, times: Any | None):
    update_status_of_wallpaper(uid, WallpaperStatus.READY)
    update_data_of_wallpaper(uid, times)

    finish(key)


@celery.task
def on_chord_error(request, exc, traceback, hmmm):
    print("Task {0!r} raised error: {1!r}".format(request.id, exc))


def handle_heic(self, fname: str, uid: str):
    complete_file_path = f"{AppConfig.UPLOAD_FOLDER}/{fname}"
    c = heic.get_wallpaper_config(complete_file_path)

    if "si" in c:
        raise Exception(
            "NOT_IMPLEMENTED_ERROR: Sun based wallpapers are not yet supported.")

    warnings = ""

    times = c["ti"]
    times.sort(key=lambda x: x["t"])
    prev = -0.1
    for d in times:
        cur = float(d["t"])
        if not 0.0 <= cur <= 1.0:
            warnings += (
                "Warning: Invalid time specification found. Might skip some images.\n"
            )
        if cur == prev:
            warnings += (
                "Warning: Ambigous time specifiation found. Might skip some images.\n"
            )
        prev = cur

    if warnings:
        print(warnings)

    total_length = heic.get_img_count(fname)

    self.update_state(
        state="PENDING",
        meta=f"Concurrently processing all image work (Preview and image resizing)",
    )

    tasks = [heic_generate_single_image.s(fname, uid, i) for i in range(total_length)]
    tasks.append(heic_generate_preview.s(fname, uid))

    job = group(tasks)

    (job | finish_processing.s(fname, uid, times, original_name)).delay()

    return "Processing multiple HEIC images"


@celery.task()
def handle_generic(key: str, uid: str):
    tasks = [
        generate_preview.s(key, uid),
        generate_single_image.s(key, uid),
    ]

    job = group(tasks)
    (job | finish_processing.s(key, uid, None)).delay()
    return "Processing normal image"


@celery.task(bind=True)
def handle_all_images(self, key: str, uid: str, type: WallpaperType):
    # create s3 dir
    s3_results.put_object(Bucket=AppConfig.RESULT.S3_BUCKET, Key=uid)

    if type == WallpaperType.HEIC:
        # return handle_heic(self, fname, uid)
        pass
    elif type == WallpaperType.GENERIC:
        return handle_generic(key, uid)

    raise ValueError("Invalid wallpaper type")

import logging
from typing import Any

import boto3
from celery import group, shared_task

from api.models import Wallpaper, WallpaperStatus, WallpaperType
from api.services import image_service, heic_service as heic
from api.services.wallpaper_service import delete_all_pending
from djangobackend import settings

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


def remove_upload_with_key(key: str) -> None:
    print(f"Removing uploaded file: {key}")
    s3_uploads.delete_object(Bucket=settings.CONFIG.UPLOAD.BUCKET, Key=key)


@shared_task()
def heic_generate_single_image(uid: str, idx: int):
    img = image_service.open_image(s3_uploads, uid)
    image_service.generate_normal_image(s3_results, heic.get_image_from_name(img, idx), uid, idx)


@shared_task()
def heic_generate_preview(uid: str):
    img = image_service.open_image(s3_uploads, uid)
    image_service.generate_preview(s3_results, heic.get_image_from_name(img, 0), uid)

@shared_task()
def generate_preview(uid: str):
    img = image_service.open_image(s3_uploads, uid)
    image_service.generate_preview(s3_results, img, uid)


@shared_task()
def generate_single_image(uid: str):
    img = image_service.open_image(s3_uploads, uid)
    image_service.generate_normal_image(s3_results, img, uid, 0)


@shared_task()
def finish_processing(prev_results: Any, uid: str, times: Any | None) -> None:
    wallpaper = Wallpaper.objects.get(uid=uid)
    wallpaper.status = WallpaperStatus.READY
    wallpaper.data = times
    wallpaper.save()

    remove_upload_with_key(uid)
#
#
# @shared_task
# def on_chord_error(request, exc, traceback, hmmm):
#     print("Task {0!r} raised error: {1!r}".format(request.id, exc))
#     print(hmmm)


def handle_heic(self, uid: str):
    img = image_service.open_image(s3_uploads, uid)
    try:
        c = heic.get_wallpaper_config(img)
    except Exception as e:
        wallpaper = Wallpaper.objects.get(uid=uid)
        wallpaper.type = WallpaperType.GENERIC
        wallpaper.save()
        logging.warning("Wallpaper was not a time-based wallpaper, rescheduled with generic")
        handle_all_images.delay(uid, WallpaperType.GENERIC)
        return "Wallpaper was not a time-based wallpaper, rescheduled with generic",str(e)

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
        logging.warning(warnings)

    total_length = heic.get_img_count(img)

    self.update_state(
        state="PENDING",
        meta=f"Concurrently processing all image work (Preview and image resizing)",
    )

    tasks = [heic_generate_single_image.s(uid, i) for i in range(total_length)]
    tasks.append(heic_generate_preview.s(uid))

    job = group(tasks)

    (job | finish_processing.s(uid, times)).delay()

    return "Processing multiple HEIC images"


def handle_generic(uid: str):
    tasks = [
        generate_preview.s(uid),
        generate_single_image.s(uid),
    ]

    job = group(tasks)
    (job | finish_processing.s(uid, None)).delay()
    return "Processing normal image"


@shared_task(bind=True)
def handle_all_images(self, uid: str, type: WallpaperType):
    type = int(type)
    logging.info(f"Processing wallpaper {uid} with type {type}")
    if type == WallpaperType.TIME_BASED:
        return handle_heic(self, uid)
    elif type == WallpaperType.GENERIC.value:
        return handle_generic(uid)

    raise ValueError("Invalid wallpaper type")

@shared_task()
def remove_broken_images():
    delete_all_pending()
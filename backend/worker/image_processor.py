import gc
import os
import shutil
import json

import time
from celery import Celery, group

from backend.database.redis import (
    WallpaperStatus,
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


def finish(filename):
    print(f"Removing uploaded file: {filename}")
    try:
        os.remove(f"{AppConfig.UPLOAD_FOLDER}/{filename}")
    except:
        pass


def remove_all_data(filename):
    try:
        shutil.rmtree(f"{AppConfig.PROCESSED_FOLDER}/{filename}/")
    except:
        pass


@celery.task()
def handle_singular_image(fname: str, uid: str, idx: int):
    heic.generate_normal_image(fname, uid, idx)


@celery.task()
def generate_preview(fname: str, uid: str):
    heic.generate_preview(fname, uid)


@celery.task()
def finish_processing(prev_results, fname, uid, times, original_name):
    update_status_of_wallpaper(uid, WallpaperStatus.READY)
    update_data_of_wallpaper(uid, times)

    json_location = f"{AppConfig.PROCESSED_FOLDER}/{uid}/data.json"
    with open(json_location, "w") as f:
        json.dump(
            {
                "date_created": int(time.time()),
                "status": 1,  # This is executed at the end, so wallpaper is ready
                "type": 2,  # This function only handles heic files for now
                "data": times,
                "original_name": original_name,
            },
            f,
        )

    finish(fname)


@celery.task
def on_chord_error(request, exc, traceback, hmmm):
    print("Task {0!r} raised error: {1!r}".format(request.id, exc))
    # TODO: This is gonna cause a whole bunch of errors because processes are still writing to this folder
    remove_all_data(hmmm)


@celery.task(bind=True)
def handle_image(self, fname: str, uid: str,  original_name: str):
    # try:
    complete_file_path = f"{AppConfig.UPLOAD_FOLDER}/{fname}"

    if not fname.endswith(".heic"):
        raise Exception("Files other than .heic cannot be handled right now")
        # TODO: Move file to correct dir and finish this task

    if not os.path.exists(complete_file_path):
        raise Exception(f"File upload did not complete {complete_file_path}")

    c = heic.get_wallpaper_config(complete_file_path)
    if "si" in c:
        raise Exception("Sun based wallpapers are not yet supported.")

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

    self.update_state(state="PENDING", meta="Opening file container")
    total_length = heic.get_img_count(fname)

    os.mkdir(f"{AppConfig.PROCESSED_FOLDER}/{uid}/")

    self.update_state(
        state="PENDING",
        meta=f"Concurrently processing all image work (Preview and image resizing)",
    )


    tasks = [handle_singular_image.s(fname, uid, i) for i in range(total_length)]
    tasks.append(generate_preview.s(fname, uid))

    job = group(tasks)

    c = (job | finish_processing.s(fname, uid, times, original_name)).delay()

    return "Processing"

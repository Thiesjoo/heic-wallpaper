import gc
import os
import shutil
import json

import time
from celery import Celery, group
from celery.exceptions import Ignore

import sys
from pyheif import HeifTopLevelImage, open_container, HeifFile
from database.redis import (
    WallpaperStatus,
    update_data_of_wallpaper,
    update_status_of_wallpaper,
)

sys.path.append("..")

from config import AppConfig, CeleryConfig
import heic

# Initialize Celery
celery = Celery(
    "worker",
    broker=CeleryConfig.CELERY_BROKER_URL,
    backend=CeleryConfig.CELERY_RESULT_BACKEND,
)


def finish(filename):
    print(f"Removing uploaded file: {filename}")
    try:
        os.remove(f"{AppConfig.UPLOAD_FOLDER}/{filename}")
    except:
        pass
    # TODO: Remove partially processed files?


def remove_all_data(filename):
    try:
        shutil.rmtree(f"{AppConfig.PROCESSED_FOLDER}/{filename}/")
    except:
        pass


@celery.task()
def handle_singular_image(name, idx):
    heic.generate_normal_image(name, idx)


@celery.task()
def generate_preview(name):
    heic.generate_preview(name)


@celery.task(bind=True)
def handle_image(self, name):
    try:
        # TODO: Check if file is heic:
        # Do all cool handling and database mapping

        complete_file_path = f"{AppConfig.UPLOAD_FOLDER}/{name}"

        if not name.endswith(".heic"):
            raise Exception("Files other than .heic cannot be handled right now")
            # Move file to correct dir and finish this task
        if not os.path.exists(complete_file_path):
            raise Exception("File upload did not complete")

        c = heic.get_wallpaper_config(complete_file_path)
        print(c)
        if "si" in c:
            raise Exception("Sun based wallpapers are not yet supported.")

        warnings = ""

        times = c["ti"]
        times.sort(key=lambda x: x["t"])
        prev = -0.1
        for d in times:
            cur = float(d["t"])
            if not 0.0 <= cur <= 1.0:
                warnings += "Warning: Invalid time specification found. Might skip some images.\n"
            if cur == prev:
                warnings += "Warning: Ambigous time specifiation found. Might skip some images.\n"
            prev = cur

        if warnings:
            print(warnings)

        self.update_state(state="PENDING", meta="Opening file container")
        heif_container = open_container(complete_file_path)
        all_images: list[HeifTopLevelImage] = heif_container.top_level_images
        total_length = len(all_images)

        os.mkdir(f"{AppConfig.PROCESSED_FOLDER}/{name}/")

        self.update_state(
            state="PENDING",
            meta=f"Concurrently processing all image work (Preview and image resizing)",
        )

        # Not sure if this takes data, but to be sure delete everything
        del all_images
        del heif_container
        gc.collect()

        tasks = [handle_singular_image.s(name, i) for i in range(total_length)]
        tasks.append(generate_preview.s(name))

        job = group(tasks)
        result = job.apply_async()
        result.get(disable_sync_subtasks=False)

        self.update_state(state="PENDING", meta=f"Storing JSON")
        update_status_of_wallpaper(name, WallpaperStatus.READY)
        update_data_of_wallpaper(name, times)

        json_location = f"{AppConfig.PROCESSED_FOLDER}/{name}/data.json"
        with open(json_location, "w") as f:
            json.dump(
                {
                    "time": int(time.time()),
                    "data": times,
                    "original_name": name,
                },
                f,
            )

        return "Finished"
    except Exception as e:
        self.update_state(state="FAILED", meta=str(e))
        print("Something went wrong on processing image: ", e)
        update_status_of_wallpaper(uuid, WallpaperStatus.ERROR)
        add_error_to_wallpaper(uuid, str(e))

        # remove_all_data(name)
        raise Ignore()
    finally:
        # finish(name)
        pass

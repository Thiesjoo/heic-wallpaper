from datetime import datetime
import os
import shutil

from time import sleep
from celery import Celery
from celery.exceptions import Ignore

import sys
from pyheif import HeifTopLevelImage, open_container, HeifFile
from PIL import Image

sys.path.append("..")

from config import AppConfig, CeleryConfig
import heic

# Initialize Celery
celery = Celery(
    "worker",
    broker=CeleryConfig.CELERY_BROKER_URL,
    backend=CeleryConfig.CELERY_RESULT_BACKEND,
)


@celery.task()
def func1(arg: int):
    print("Celery task tests")
    sleep(10)
    return arg + 1


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

        # now = datetime.now().time()
        # nowsecs = now.hour * 60 * 60 + now.minute * 60 + now.second
        # last_one = times[-1]
        # for time in times:
        #     if float(time["t"]) * 60 * 60 * 24 > nowsecs:
        #         if (
        #             float(time["t"]) * 60 * 60 * 24 - nowsecs < 10
        #         ):  # prevent floating errors or similar things
        #             last_one = time
        #         break
        #     last_one = time
        # index = last_one["i"]

        heif_container = open_container(complete_file_path)
        all_images: list[HeifTopLevelImage] = heif_container.top_level_images

        os.mkdir(f"{AppConfig.PROCESSED_FOLDER}/{name}/")

        for i, img in enumerate(all_images):
            heif_file: HeifFile = img.image
            heif_file.load()

            loaded_img = Image.frombytes(
                heif_file.mode,
                heif_file.size,
                heif_file.data,
                "raw",
                heif_file.mode,
                heif_file.stride,
            )

            loaded_img.thumbnail((3000, 3000))
            loaded_img.save(
                f"{AppConfig.PROCESSED_FOLDER}/{name}/{i}.png",
                quality=85,
                optimize=True,
            )

        return "Finished"
    except Exception as e:
        self.update_state(state="FAILED", meta=str(e))
        remove_all_data(name)
        raise Ignore()
    finally:
        finish(name)

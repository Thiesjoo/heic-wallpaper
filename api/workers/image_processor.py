import os
from time import sleep
from celery import Celery
import sys

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
    os.remove(f"{AppConfig.UPLOAD_FOLDER}/{filename}")
    # TODO: Remove partially processed files?


@celery.task(bind=True)
def handle_image(self, name):
    try:
        # TODO: Check if file is heic:
        # Do all cool handling and database mapping

        if not name.endswith(".heic"):
            raise Exception("Files other than .heic cannot be handled right now")
            # Move file to correct dir and finish this task
        if not os.path.exists(f"{AppConfig.UPLOAD_FOLDER}/{name}"):
            return "Idk man alles gaat kapot"

        c = heic.get_wallpaper_config(f"{AppConfig.UPLOAD_FOLDER}/{name}")
        print(c)
        return c
        # TODO: Do this check on upload
        if "si" in c:
            print("Sun based wallpapers are not yet supported.", file=sys.stderr)
            sys.exit(1)

        times = c["ti"]
        times.sort(key=lambda x: x["t"])
        prev = -0.1
        for d in times:
            cur = float(d["t"])
            if not 0.0 <= cur <= 1.0:
                print(
                    "Warning: Invalid time specification found. Might skip some images."
                )
            if cur == prev:
                print(
                    "Warning: Ambigous time specifiation found. Might skip some images."
                )
            prev = cur

        times = c["ti"]
        times.sort(key=lambda x: x["t"])
        now = datetime.now().time()
        nowsecs = now.hour * 60 * 60 + now.minute * 60 + now.second
        last_one = times[-1]
        for time in times:
            if float(time["t"]) * 60 * 60 * 24 > nowsecs:
                if (
                    float(time["t"]) * 60 * 60 * 24 - nowsecs < 10
                ):  # prevent floating errors or similar things
                    last_one = time
                break
            last_one = time
        index = last_one["i"]

        heif_container = pyheif.open_container(f"wallpapers/{name}")
        all_images = heif_container.top_level_images

        assert index < len(all_images)

        heif_file = all_images[index].image

        heif_file.load()
        print(heif_file)
        img = Image.frombytes(
            heif_file.mode,
            heif_file.size,
            heif_file.data,
            "raw",
            heif_file.mode,
            heif_file.stride,
        )

        img.thumbnail((3000, 3000))
        img.save("test.png", quality=85, optimize=True)

        print(filename)
        return "asd"
    except:
        print("Something went wrong!")
    finally:
        finish(name)

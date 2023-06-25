"""
Functions for reading and extracting data from heic files
"""
import base64
import gc
import plistlib
import subprocess
from config import AppConfig

from PIL import Image ,ImageSequence
from pi_heif import register_heif_opener
register_heif_opener()

def get_exif(fname):
    """
    Sadly, pillow and exifread do not support heic yet
    """
    args = ["exiftool", fname]
    r = subprocess.run(args, stdout=subprocess.PIPE)
    output = r.stdout.decode("utf-8")
    return {
        line.split(":")[0].strip(): line.split(":")[1].strip()
        for line in output.split("\n")[:-1]
    }


def get_image_container(fname: str) -> Image:
    complete_file_path = f"{AppConfig.UPLOAD_FOLDER}/{fname}"
    
    heic_pillow = Image.open(complete_file_path)
    return heic_pillow

def get_img_count(fname: str) -> int:
    img = get_image_container(fname)

    count = 0
    for idx,frame in enumerate(ImageSequence.Iterator(img)):
        count += 1
    img.close()
    del img
    gc.collect()
    return count

def get_image_from_name(fname: str, idx: int)-> Image:
    img = get_image_container(fname)
    return ImageSequence.Iterator(img)[idx]


def generate_preview(fname: str):
    heif_file = get_image_from_name(fname, 0)

    heif_file.thumbnail((1280, 720))
    heif_file.save(
        f"{AppConfig.PROCESSED_FOLDER}/{fname}/preview.png",
        quality=70,
        optimize=True,
    )
    heif_file.close()


def generate_normal_image(fname, idx):
    img = get_image_from_name(fname, idx)


    img.thumbnail((3840, 2160))
    img.save(
        f"{AppConfig.PROCESSED_FOLDER}/{fname}/{idx}.png",
    )
    img.close()


def get_wallpaper_config(fname):
    exif = get_exif(fname)

    if "H24" not in exif and "Solar" not in exif:
        raise Exception(
            "This is not a live wallpaper. We only support live wallpapers atm"
        )

    if "Solar" in exif:
        data = exif["Solar"]
    else:
        data = exif["H24"]

    dec = base64.b64decode(data)
    config = plistlib.loads(dec)

    return config

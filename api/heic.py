"""
Functions for reading and extracting data from heic files
"""
import base64
import gc
import plistlib
import subprocess
from pyheif import HeifTopLevelImage, open_container, HeifFile
from config import AppConfig
from PIL import Image


def get_exif(fname):
    """
    Sadly, pillow and exifread do not support heic yet
    """
    args = ["exiftool", fname]
    r = subprocess.run(args, stdout=subprocess.PIPE)
    # TODO: Error handling
    output = r.stdout.decode("utf-8")
    return {
        line.split(":")[0].strip(): line.split(":")[1].strip()
        for line in output.split("\n")[:-1]
    }


def get_image_container(fname: str):
    complete_file_path = f"{AppConfig.UPLOAD_FOLDER}/{fname}"
    heif_container = open_container(complete_file_path)
    all_images: list[HeifTopLevelImage] = heif_container.top_level_images
    return all_images


def get_image_from_name(fname: str, idx: int):
    return get_image_container(fname)[idx]


def generate_preview(fname):
    heif_file: HeifFile = get_image_from_name(fname, 0).image
    heif_file.load()

    loaded_img = Image.frombytes(
        heif_file.mode,
        heif_file.size,
        heif_file.data,
        "raw",
        heif_file.mode,
        heif_file.stride,
    )
    loaded_img.thumbnail((1280, 720))
    loaded_img.save(
        f"{AppConfig.PROCESSED_FOLDER}/{fname}/preview.png",
        quality=70,
        optimize=True,
    )
    loaded_img.close()


def generate_normal_image(fname, idx):
    img = get_image_from_name(fname, idx)

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

    loaded_img.thumbnail((3840, 2160))
    loaded_img.save(
        f"{AppConfig.PROCESSED_FOLDER}/{fname}/{idx}.png",
        quality=85,
        optimize=True,
    )
    loaded_img.close()
    del heif_file.data
    gc.collect()


def get_wallpaper_config(fname):
    exif = get_exif(fname)

    if "H24" not in exif and "Solar" not in exif:
        # TODO: Research more of heic spec
        raise Exception("This is not a live wallpaper")

    if "Solar" in exif:
        data = exif["Solar"]
    else:
        data = exif["H24"]

    dec = base64.b64decode(data)
    config = plistlib.loads(dec)

    return config

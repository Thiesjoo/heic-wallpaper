"""
Functions for reading and extracting data from heic files
"""
import base64
import gc
import plistlib
import subprocess

from botocore.client import BaseClient

from backend import image
from backend.config import AppConfig

from PIL import Image ,ImageSequence
from pi_heif import register_heif_opener
register_heif_opener()

def get_img_count(img: Image) -> int:
    count = 0
    for idx,frame in enumerate(ImageSequence.Iterator(img)):
        count += 1
    img.close()
    del img
    gc.collect()
    return count

def get_image_from_name(img_container: Image, idx: int)-> Image:
    heif_img = ImageSequence.Iterator(img_container)[idx]

    img = heif_img.copy()
    del heif_img
    del img_container
    gc.collect()
    return img



def get_wallpaper_config(image: Image):
    info = image.info

    xmp = str(info.get("xmp"))
    if xmp == "None":
        raise Exception("This is not a valid live wallpaper")

    start = xmp.find("apple_desktop:h24=\"")
    end = xmp.find("\"/>", start)
    if (start == -1 or end == -1):
        raise Exception("Not H24 heic, maybe solar")
    try:
        h24 = base64.b64decode(xmp[start + 19: end])
        config = plistlib.loads(h24)
    except:
        print(xmp)
        raise Exception("This is not a valid live wallpaper")

    return config

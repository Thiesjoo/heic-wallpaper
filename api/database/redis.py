# Wallpaper data structure:

"""
INDEXED BY: key - uuid
- status
- date_created
- original_name
- type (normal or heic)
- (OPTIONAL) sun data
"""


"""
Further more: store 1 array of uuid's
"""
from typing import Any, Tuple, TypedDict
import redis
from redis.commands.json.path import Path
import sys
from enum import Enum

sys.path.append("..")

from config import CeleryConfig

client = redis.Redis.from_url(CeleryConfig.CELERY_RESULT_BACKEND)

WALLPAPER_LOCATION = "wallpapers"
WALLPAPER_UUID_PREFIX = "wallpaper:"


class WallpaperTypes(int, Enum):
    NORMAL = 1
    HEIC = 2
    ANIMATED = 3


class WallpaperStatus(int, Enum):
    READY = 1
    PROCESSING = 2
    ERROR = 3
    DELETED = 4


class Wallpaper(TypedDict):
    original_name: str
    date_created: int
    status: int  # WallpaperStatus
    type: int  # WallpaperTypes
    data: Any  # TODO: Figure out how to type this
    error: Any


def get_all_wallpapers() -> list[Wallpaper]:
    return client.zrange(WALLPAPER_LOCATION, 0, -1, withscores=True)
    # Return every wallpaper


def get_single_wallpaper(uuid: str) -> Wallpaper | Tuple[str, int]:
    temp: Wallpaper = client.json().get(WALLPAPER_UUID_PREFIX + uuid)
    if temp["status"] == WallpaperStatus.PROCESSING:
        # 202 status code when result is still processing
        return "Still processing", 202
    # Should return URL, preview URL and data
    return temp


def add_wallpaper(uuid: str, wallpaper: Wallpaper):
    print(wallpaper)
    client.json().set(
        WALLPAPER_UUID_PREFIX + uuid, Path.root_path(), wallpaper, nx=True
    )
    print(wallpaper["date_created"])
    client.zadd(WALLPAPER_LOCATION, {uuid: wallpaper["date_created"]})


def update_status_of_wallpaper(uuid: str, status: str):
    client.json().set(WALLPAPER_UUID_PREFIX + uuid, ".status", status)


def update_data_of_wallpaper(uuid: str, data: Any):
    client.json().set(WALLPAPER_UUID_PREFIX + uuid, ".data", data)

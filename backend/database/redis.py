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
from typing import Any, List, Tuple, TypedDict
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
    create_by: str
    status: int  # WallpaperStatus
    type: int  # WallpaperTypes
    data: Any
    error: str


def get_all_wallpapers() -> List[Wallpaper]:
    all_ids = client.zrange(WALLPAPER_LOCATION, 0, -1)
    all_objs = [
        {
            **client.json().get(WALLPAPER_UUID_PREFIX + (uuid.decode("UTF-8"))),
            "uuid": uuid.decode("UTF-8"),
        }
        for uuid in all_ids
    ]

    return all_objs


def get_single_wallpaper(uuid: str) -> Wallpaper | Tuple[str, int]:
    temp: Wallpaper = client.json().get(WALLPAPER_UUID_PREFIX + uuid)
    if temp is None:
        return "Wallpaper not found", 404

    if "status" in temp and temp["status"] == WallpaperStatus.PROCESSING:
        # 202 status code when result is still processing
        return "Still processing", 202
    
    # Should return URL, preview URL and data
    return {**temp, "uuid": uuid}


def remove_single_wallpaper(uuid: str):
    client.json().delete(WALLPAPER_UUID_PREFIX + uuid)
    client.zrem(WALLPAPER_LOCATION, uuid)


def add_wallpaper(uuid: str, wallpaper: Wallpaper):
    client.json().set(
        WALLPAPER_UUID_PREFIX + uuid, Path.root_path(), wallpaper, nx=True
    )
    client.zadd(WALLPAPER_LOCATION, {uuid: wallpaper["date_created"]})


def update_status_of_wallpaper(uuid: str, status: int):
    client.json().set(WALLPAPER_UUID_PREFIX + uuid, ".status", status)


def update_data_of_wallpaper(uuid: str, data: Any):
    client.json().set(WALLPAPER_UUID_PREFIX + uuid, ".data", data)


def add_error_to_wallpaper(uuid: str, err: str):
    client.json().set(WALLPAPER_UUID_PREFIX + uuid, ".error", err)

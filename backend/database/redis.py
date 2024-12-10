# Wallpaper data structure:

"""
INDEXED BY: key - uuid
- status
- date_created
- original_name
- type (normal or heic)
- (OPTIONAL) sun data
"""
import time

"""
Further more: store 1 array of uuid's
"""
from enum import Enum
from typing import Any, List, Tuple, TypedDict

from redis.commands.json.path import Path

import redis
from backend.config import CeleryConfig, DatabaseConfig

DatabaseConfig.validate()
client = redis.Redis.from_url(DatabaseConfig.DATABASE_URL)

WALLPAPER_LOCATION = "wallpapers"
WALLPAPER_UUID_PREFIX = "wallpaper:"


class WallpaperType(int, Enum):
    GENERIC = 1
    HEIC = 2
    ANIMATED = 3


class WallpaperStatus(int, Enum):
    READY = 1
    UPLOADING = 2
    PROCESSING = 4
    ERROR = 8
    DELETED = 16


class Wallpaper(TypedDict):
    uid: str
    original_name: str
    date_created: int
    created_by: str
    status: int  # WallpaperStatus
    type: int  # WallpaperTypes
    data: Any
    error: str | None


def get_all_wallpapers() -> List[Wallpaper]:
    all_ids = client.zrange(WALLPAPER_LOCATION, 0, -1)
    all_objs = [
        {
            **client.json().get(WALLPAPER_UUID_PREFIX + (uuid.decode("UTF-8"))),
            "uid": uuid.decode("UTF-8"),
        }
        for uuid in all_ids
    ]

    return all_objs


def get_single_wallpaper(uid: str) -> Wallpaper | Tuple[str, int]:
    temp: Wallpaper = client.json().get(WALLPAPER_UUID_PREFIX + uid)
    if temp is None:
        return "Wallpaper not found", 404

    if "status" in temp and temp["status"] in [WallpaperStatus.PROCESSING,
                                               WallpaperStatus.UPLOADING]:
        # 202 status code when result is still processing
        return "Still processing", 202

    # Should return URL, preview URL and data
    return {**temp, "uid": uid}


def remove_single_wallpaper(uid: str):
    client.json().delete(WALLPAPER_UUID_PREFIX + uid)
    client.zrem(WALLPAPER_LOCATION, uid)


def add_wallpaper(uid: str, wallpaper: Wallpaper):
    client.json().set(
        WALLPAPER_UUID_PREFIX + uid, Path.root_path(), wallpaper, nx=True
    )
    client.zadd(WALLPAPER_LOCATION, {uid: wallpaper["date_created"]})


def update_status_of_wallpaper(uid: str, status: int):
    client.json().set(WALLPAPER_UUID_PREFIX + uid, ".status", status)


def update_data_of_wallpaper(uid: str, data: Any):
    client.json().set(WALLPAPER_UUID_PREFIX + uid, ".data", data)


def add_error_to_wallpaper(uid: str, err: str):
    client.json().set(WALLPAPER_UUID_PREFIX + uid, ".error", err)


def delete_all_pending():
    deleted = set()
    all_wallpapers = get_all_wallpapers()
    for wallpaper in all_wallpapers:
        if wallpaper["status"] == WallpaperStatus.PROCESSING and (
                wallpaper["date_created"] + DatabaseConfig.MAX_AGE_FOR_PENDING
                ) < int(time.time()):
                deleted.add(wallpaper["uid"])
                remove_single_wallpaper(wallpaper["uid"])

    return deleted

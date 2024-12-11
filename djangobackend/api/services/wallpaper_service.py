from datetime import datetime

import pytz as pytz

from api.models import WallpaperStatus, Wallpaper, WallpaperType
from djangobackend import settings


def get_wallpaper_by_id(id: int) -> Wallpaper:
    """
    Get a wallpaper by its ID
    """
    return Wallpaper.objects.filter(
        status=WallpaperStatus.READY
    ).get(id=id)

def delete_all_pending() -> list[int]:
    """
    Delete all pending images from the database and the S3 bucket
    """
    pending = Wallpaper.objects.filter(
        status__in=[WallpaperStatus.UPLOADING, WallpaperStatus.PROCESSING, WallpaperStatus.ERROR],
        date_created__lt=datetime.now() - settings.MAX_AGE_FOR_PENDING_WALLPAPERS
    ).all()

    deleted_uuids = []
    for wallpaper in pending:
        deleted_uuids.append(wallpaper.uid)
        wallpaper.delete()

    return deleted_uuids


def get_current_image_url_for_wallpaper(id: int, timezone: pytz.timezone = pytz.timezone("UTC")) -> str | None:
    """
    Get the current image for a wallpaper
    """
    try:
        wallpaper = get_wallpaper_by_id(id)
    except Wallpaper.DoesNotExist:
        return None

    if wallpaper.type == WallpaperType.GENERIC:
        return wallpaper.index_url(0)

    times = wallpaper.data
    if times is None:
        return wallpaper.index_url(0)

    now = datetime.now(timezone).time()
    print(now, times)
    nowsecs = now.hour * 60 * 60 + now.minute * 60 + now.second

    # https://github.com/mczachurski/wallpapper
    last_one = times[-1]
    for time in times:
        if nowsecs > float(time["t"]) * 60 * 60 * 24:
            last_one = time
    index = last_one["i"]

    return wallpaper.index_url(index)
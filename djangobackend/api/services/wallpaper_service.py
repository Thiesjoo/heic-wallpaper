import time
from datetime import datetime

from api.models import WallpaperStatus, Wallpaper
from djangobackend import settings


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
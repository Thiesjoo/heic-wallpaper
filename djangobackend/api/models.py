import logging

from django.db import models

from core.models import User
from djangobackend import settings


class WallpaperType(models.IntegerChoices):
    GENERIC = 1
    TIME_BASED = 2

class WallpaperStatus(models.IntegerChoices):
    READY = 1
    UPLOADING = 2
    PROCESSING = 3
    ERROR = 4
    DELETED = 5

class Wallpaper(models.Model):
    id = models.AutoField(primary_key=True)

    uid = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

    status = models.CharField(max_length=255, choices=WallpaperStatus.choices)
    type = models.CharField(max_length=255, choices=WallpaperType.choices)

    data = models.JSONField()

    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.uid}, status: {self.status})"

    def preview_url(self):
        return f"{settings.CONFIG.PUBLIC_ASSET_URL}/{self.uid}/preview.png"

    def index_url(self, index: int):
        return f"{settings.CONFIG.PUBLIC_ASSET_URL}/{self.uid}/{index}.png"

    def delete(self, *args, **kwargs):
        from api.services import s3_service
        s3_service.remove_all_references(self.uid)
        logging.info(f"Deleted references for {self.uid}")
        super().delete(*args, **kwargs)
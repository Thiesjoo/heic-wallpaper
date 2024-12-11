from rest_framework import viewsets, permissions, mixins, serializers
from rest_framework.viewsets import GenericViewSet

from api.models import Wallpaper
from api.serializers import WallpaperSerializer


class WallpapersViewSet(mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):

    queryset = Wallpaper.objects.all().prefetch_related('owner')
    serializer_class = WallpaperSerializer


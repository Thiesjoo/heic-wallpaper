from rest_framework import viewsets, permissions

from api.models import Wallpaper
from api.serializers import WallpaperSerializer


class WallpapersViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Wallpaper.objects.all()
    serializer_class = WallpaperSerializer

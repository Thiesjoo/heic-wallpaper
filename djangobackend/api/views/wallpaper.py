import pytz
from django.shortcuts import redirect
from rest_framework import viewsets, permissions, mixins, serializers, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.models import Wallpaper, WallpaperStatus
from api.serializers import WallpaperSerializer, WallpaperWithDetailsSerializer
from api.services.wallpaper_service import get_current_image_url_for_wallpaper


class WallpapersViewSet(mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):

    queryset = Wallpaper.objects.all().prefetch_related('owner')
    serializer_class = WallpaperSerializer

    def list(self, request, *args, **kwargs):
        # only return wallpapers that are ready
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(status=WallpaperStatus.READY)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        return Response(WallpaperWithDetailsSerializer(instance).data)


@api_view(['GET'])
def get_current_wallpaper(request, **kwargs):
    wallpaper_id = kwargs.get('id')
    timezone = request.GET.get('tz', "UTC")

    result = get_current_image_url_for_wallpaper(wallpaper_id, pytz.timezone(timezone))
    if result is None:
        return Response({
            "error": "Wallpaper not found"
        }, status=status.HTTP_404_NOT_FOUND)

    return redirect(result)
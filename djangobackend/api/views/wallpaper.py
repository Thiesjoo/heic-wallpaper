from rest_framework import viewsets, permissions, mixins, serializers
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from api.models import Wallpaper, WallpaperStatus
from api.serializers import WallpaperSerializer, WallpaperWithDetailsSerializer


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
from rest_framework import serializers

from api.models import Wallpaper


class WallpaperSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallpaper
        fields = ['url']
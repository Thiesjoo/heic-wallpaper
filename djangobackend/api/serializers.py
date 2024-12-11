from rest_framework import serializers

from api.models import Wallpaper
from core.serializers import UserSerializer


class WallpaperSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Wallpaper
        fields = ['id', 'uid', 'name', 'owner', 'status', 'type', 'data']
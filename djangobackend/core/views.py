from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.services.wallpaper_service import get_wallpaper_by_id
from core import authentication
from core.serializers import UserSerializer


class WhoamiView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class SetSettingsView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        wallpaper_id = request.data.get("wallpaper")

        try:
            wallpaper_id = int(wallpaper_id)
            wallpaper = get_wallpaper_by_id(wallpaper_id)
        except Exception as e:
            return Response({"error": "Invalid wallpaper ID"}, status=400)

        result, msg = authentication.set_user_wallpaper(request.user.uid,
                                                        wallpaper.live_url())

        if result:
            return Response({"success": True})
        else:
            return Response({"error": msg}, status=400)

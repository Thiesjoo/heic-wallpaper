from django.urls import include, path
from rest_framework import routers

from wallpaper import views as wallpaper_views
from core import views as core_views

router = routers.DefaultRouter()
router.register(r'wallpapers', wallpaper_views.WallpapersViewSet)


urlpatterns = [
    path('api/users/whoami/', core_views.WhoamiView.as_view()),
    path('api/users/set/', core_views.SetSettingsView.as_view()),
    path('api/', include(router.urls)),
    path('api/wallpaper/<int:id>/', wallpaper_views.get_current_wallpaper, name="api.views.get_current_wallpaper"),
    path('api/upload/', wallpaper_views.upload_view),
    path('api/upload/complete/', wallpaper_views.upload_complete),
]
from django.urls import include, path
from rest_framework import routers

from api import views as api_views
from core import views as core_views

router = routers.DefaultRouter()
router.register(r'wallpapers', api_views.WallpapersViewSet)


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('api/users/whoami/', core_views.WhoamiView.as_view()),
    path('api/', include(router.urls)),
    path('api/upload/', api_views.upload_view),
    path('api/upload/complete/', api_views.upload_complete),
]
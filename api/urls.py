from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from . import views

app_name = "api"

router = DefaultRouter()
router.register("sites", views.SiteViewSet, basename="site")
router.register("locations", views.LocationViewSet, basename="location")
router.register("walls", views.WallViewSet, basename="wall")
router.register("photos", views.PhotoViewSet, basename="photo")
router.register("people", views.PersonViewSet, basename="person")

urlpatterns = [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="api:schema"), name="docs"),
    path("", include(router.urls)),
]

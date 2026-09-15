# urls.py
from django.urls import path

from .views import (
    derived_image_detail_view,
    list_walls_view,
    overall_image_view,
    site_detail_view,
)

app_name = "graffiti"

urlpatterns = [
    path("", list_walls_view, name="walls_list"),
    path("site/<int:site_id>/", site_detail_view, name="site_detail"),
    path("wall/<int:wall_id>/", overall_image_view, name="overall_image"),
    path(
        "derived-image/<int:image_id>/",
        derived_image_detail_view,
        name="derived_image_detail",
    ),
]

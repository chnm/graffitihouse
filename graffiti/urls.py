# urls.py
from django.urls import path

from .views import derived_image_detail_view, overall_image_view

app_name = "graffiti"

urlpatterns = [
    path("wall/<int:wall_id>/", overall_image_view, name="overall_image"),
    path(
        "derived-image/<int:image_id>/",
        derived_image_detail_view,
        name="derived_image_detail",
    ),
]

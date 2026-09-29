from django.urls import path
from django.views.generic import RedirectView

from .views import (
    derived_image_detail_view,
    list_walls_view,
    overall_image_view,
    site_detail_view,
)

app_name = "graffiti"


def moved_to(pattern_name):
    """Permanently redirect an old URL to its new home, keeping any query."""
    return RedirectView.as_view(
        pattern_name=f"graffiti:{pattern_name}", permanent=True, query_string=True
    )


urlpatterns = [
    path("sites/", list_walls_view, name="walls_list"),
    path("sites/<int:site_id>/", site_detail_view, name="site_detail"),
    path("walls/<int:wall_id>/", overall_image_view, name="overall_image"),
    path(
        "graffiti/<int:image_id>/",
        derived_image_detail_view,
        name="derived_image_detail",
    ),
    # URLs used before the flat /sites/, /walls/, /graffiti/ scheme. Keep
    # these so links that were already shared or cited still work.
    path("graffiti/", moved_to("walls_list")),
    path("graffiti/site/<int:site_id>/", moved_to("site_detail")),
    path("graffiti/wall/<int:wall_id>/", moved_to("overall_image")),
    path("graffiti/derived-image/<int:image_id>/", moved_to("derived_image_detail")),
]

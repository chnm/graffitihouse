from django.urls import path
from django.views.generic import RedirectView

from . import views
from .views import HomePageView

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path(
        "about/",
        RedirectView.as_view(pattern_name="team", permanent=True),
        name="about",
    ),
    path("data/", views.data, name="data"),
    path(
        "museum/",
        RedirectView.as_view(pattern_name="graffiti:walls_list", permanent=True),
        name="museum",
    ),
    path("team/", views.team, name="team"),
]

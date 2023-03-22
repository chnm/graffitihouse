from django.urls import path
from .views import HomePageView
from . import views

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("about/", views.about, name="about"),
    path("museum/", views.museum, name="museum"),
]

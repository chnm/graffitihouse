from django.views.generic import TemplateView
from django.shortcuts import render


class HomePageView(TemplateView):
    template_name = "home.html"


def about(request):
    return render(request, "about.html")


def museum(request):
    return render(request, "museum.html")


handler404 = "pages.views.handler404"


def handler404(request, exception):
    return render(request, "404.html", status=404)

import random

from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView

from graffiti.models import GraffitiPhoto, GraffitiWall, Site


class HomePageView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sites"] = Site.objects.all()

        masonry_images = [
            {
                "image": wall.image,
                "label": wall.name,
                "type": "Wall",
                "url": reverse("graffiti:overall_image", args=[wall.pk]),
            }
            for wall in GraffitiWall.objects.exclude(image="")
            .filter(image__isnull=False)
            .order_by("?")[:3]
        ]
        masonry_images.extend(
            {
                "image": photo.image,
                "label": photo.identifier,
                "type": "Graffiti",
                "url": reverse("graffiti:derived_image_detail", args=[photo.pk]),
            }
            for photo in GraffitiPhoto.objects.exclude(image="")
            .filter(image__isnull=False)
            .order_by("?")[:3]
        )
        random.shuffle(masonry_images)
        context["masonry_images"] = masonry_images[:3]

        return context


def about(request):
    return render(request, "about.html")


def museum(request):
    return render(request, "museum.html")


def handler404(request, exception):
    return render(request, "404.html", status=404)

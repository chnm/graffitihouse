import random

from django.db.models import Count
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView

from graffiti.models import GraffitiPhoto, GraffitiWall, Site
from pages.models import TeamGroup, TeamMember


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
            for wall in GraffitiWall.objects.exclude(image="").order_by("?")[:3]
        ]
        masonry_images.extend(
            {
                "image": photo.image,
                "label": photo.identifier,
                "type": "Graffiti",
                "url": reverse("graffiti:derived_image_detail", args=[photo.pk]),
            }
            for photo in GraffitiPhoto.objects.exclude(image="").order_by("?")[:3]
        )
        random.shuffle(masonry_images)
        context["masonry_images"] = masonry_images[:3]

        return context


def data(request):
    """Explain the public API and how to cite and reuse the data."""
    api_root = request.build_absolute_uri(reverse("api:api-root"))
    # Use a documented site in the examples so every example link returns data.
    example_site = (
        Site.objects.annotate(wall_count=Count("graffitiwall"))
        .filter(wall_count__gt=0)
        .order_by("-wall_count")
        .first()
    )
    return render(
        request,
        "data.html",
        {"api_root": api_root, "example_site": example_site},
    )


def team(request):
    """List active project staff and collaborators, grouped in display order."""
    members = TeamMember.objects.filter(is_active=True)
    groups = [
        (label, [member for member in members if member.group == value])
        for value, label in TeamGroup.choices
    ]
    return render(
        request,
        "team.html",
        {"groups": [(label, people) for label, people in groups if people]},
    )


def handler404(request, exception):
    return render(request, "404.html", status=404)

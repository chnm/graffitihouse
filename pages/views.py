import random

from django.shortcuts import render
from django.views.generic import TemplateView

from graffiti.models import GraffitiPhoto, GraffitiWall, Site


class HomePageView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["sites"] = Site.objects.all()

        # Add random images for the "Preserving Historical Voices" section
        import os

        from django.conf import settings

        # Ensure MEDIA_ROOT exists in settings
        if not hasattr(settings, "MEDIA_ROOT"):
            from pathlib import Path

            settings.MEDIA_ROOT = Path(__file__).resolve().parent.parent / "images"

        # Get walls with valid images that actually exist on disk
        wall_images = []
        for wall in GraffitiWall.objects.filter(image__isnull=False).order_by("?")[:15]:
            if (
                wall.image
                and hasattr(wall.image, "url")
                and hasattr(wall.image, "path")
            ):
                # Handle both relative and absolute paths
                if os.path.exists(wall.image.path):
                    wall_images.append(wall)
                    if len(wall_images) >= 3:
                        break

        if wall_images:
            context["random_wall_images"] = wall_images[: min(3, len(wall_images))]

        # Get random graffiti photos as backup if not enough wall images
        needed = 3
        if context.get("random_wall_images"):
            needed = 3 - len(context["random_wall_images"])

        if needed > 0:
            # Get derived photos with valid images that actually exist
            graffiti_photos = []
            for photo in GraffitiPhoto.objects.filter(image__isnull=False).order_by(
                "?"
            )[: needed * 3]:
                if (
                    photo.image
                    and hasattr(photo.image, "url")
                    and hasattr(photo.image, "path")
                ):
                    # Handle both relative and absolute paths
                    if os.path.exists(photo.image.path):
                        graffiti_photos.append(photo)
                        if len(graffiti_photos) >= needed:
                            break

            if graffiti_photos:
                context["random_graffiti_photos"] = graffiti_photos

        return context


def about(request):
    return render(request, "about.html")


def museum(request):
    return render(request, "museum.html")


handler404 = "pages.views.handler404"


def handler404(request, exception):
    return render(request, "404.html", status=404)

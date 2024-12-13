import json

from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from .models import GraffitiPhoto, GraffitiWall


def overall_image_view(request, wall_id):
    wall = get_object_or_404(GraffitiWall, id=wall_id)
    derived_images = GraffitiPhoto.objects.filter(graffiti_wall=wall)
    derived_images_data = []
    for image in derived_images:
        coordinates = image.coordinates
        image_data = {
            "id": image.id,
            "coordinates": coordinates,
            "detail_url": reverse("graffiti:derived_image_detail", args=[image.id]),
        }
        derived_images_data.append(image_data)
    context = {"wall": wall, "derived_images": json.dumps(derived_images_data)}
    return render(request, "graffiti/wall_overview.html", context)


def derived_image_detail_view(request, image_id):
    derived_image = get_object_or_404(GraffitiPhoto, id=image_id)
    context = {"derived_image": derived_image}
    return render(request, "graffiti/derived_image_detail.html", context)

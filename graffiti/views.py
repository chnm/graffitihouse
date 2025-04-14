import json

from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from .models import GraffitiPhoto, GraffitiWall, Site


def list_walls_view(request):
    """View to list all sites and their walls"""
    sites = Site.objects.all().prefetch_related("graffitiwall_set")
    context = {"sites": sites}
    return render(request, "graffiti/walls_list.html", context)


def overall_image_view(request, wall_id):
    """View for a specific wall with its derived images"""
    wall = get_object_or_404(GraffitiWall, id=wall_id)
    derived_images = GraffitiPhoto.objects.filter(graffiti_wall=wall)
    derived_images_data = []
    for image in derived_images:
        coordinates = image.coordinates
        # Include more data for the modal
        image_data = {
            "id": image.id,
            "identifier": image.identifier,
            "graffiti_type": image.graffiti_type or "Not specified",
            "description": str(image.description) if image.description else "",
            "image_url": image.image.url if image.image else "",
            "coordinates": coordinates,
            "detail_url": reverse("graffiti:derived_image_detail", args=[image.id]),
            "tags": [tag.name for tag in image.tags.all()]
            if image.tags.exists()
            else [],
            "created_at": image.created_at.strftime("%B %d, %Y"),
            "updated_at": image.updated_at.strftime("%B %d, %Y"),
        }
        derived_images_data.append(image_data)
    context = {
        "wall": wall,
        "derived_images": json.dumps(derived_images_data),
        "derived_images_objects": derived_images,  # Add the actual QuerySet for Django template usage
    }
    return render(request, "graffiti/wall_overview.html", context)


def derived_image_detail_view(request, image_id):
    """View for a specific derived image"""
    derived_image = get_object_or_404(GraffitiPhoto, id=image_id)
    context = {"derived_image": derived_image}
    return render(request, "graffiti/derived_image_detail.html", context)

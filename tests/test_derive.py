import datetime
import io

import pytest
from django.core.files.base import ContentFile
from PIL import Image

from graffiti.models import GraffitiPhoto, GraffitiWall, Site


@pytest.mark.django_db
def test_derive_image_crops_rectangle_from_wall(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    buffer = io.BytesIO()
    Image.new("RGB", (100, 50), "white").save(buffer, format="PNG")
    wall = GraffitiWall(
        name="Wall",
        room="1",
        spatial_position="A1",
        wall_grid_position="A1",
        identifier="W1",
        date_taken=datetime.date(2020, 1, 1),
        site_id=Site.objects.create(name="Site"),
    )
    wall.image.save("wall.png", ContentFile(buffer.getvalue()), save=True)

    photo = GraffitiPhoto(
        graffiti_wall=wall, identifier="G1", x=10, y=5, width=30, height=20
    )
    photo.derive_image()
    photo.save()

    with Image.open(photo.image) as derived:
        assert derived.size == (30, 20)

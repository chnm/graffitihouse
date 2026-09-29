import datetime
import importlib
import io
import json

import pytest
from django.apps import apps
from django.core.files.base import ContentFile
from django.urls import reverse
from PIL import Image

from graffiti.models import GraffitiPhoto, GraffitiWall, Site

description_migration = importlib.import_module(
    "graffiti.migrations.0016_graffitiphoto_description_to_html"
)


def make_wall():
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
    return wall


@pytest.mark.django_db
def test_crop_tool_saves_description_as_html(admin_client, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    wall = make_wall()
    payload = {
        "metadata": {
            "coordinates": {
                "metadata": {
                    "wall_id": wall.id,
                    "identifier": "G1",
                    "graffiti_type": "name",
                    "description": "Two lines:\nCapt J. <Marshall>\n",
                },
                "canvas": {"x": 0, "y": 0, "width": 10, "height": 10},
            }
        }
    }

    response = admin_client.post(
        reverse("admin:save-derived-graffiti"),
        json.dumps(payload),
        content_type="application/json",
    )

    assert response.json()["success"]
    assert (
        GraffitiPhoto.objects.get(identifier="G1").description
        == "<p>Two lines:<br>Capt J. &lt;Marshall&gt;</p>"
    )


@pytest.mark.django_db
def test_migration_converts_only_plain_text_descriptions():
    wall = GraffitiWall.objects.create(
        name="Wall",
        image="images/wall.jpg",
        room="1",
        spatial_position="A1",
        wall_grid_position="A1",
        identifier="W1",
        date_taken=datetime.date(2020, 1, 1),
        site_id=Site.objects.create(name="Site"),
    )
    plain = GraffitiPhoto.objects.create(
        graffiti_wall=wall, identifier="P", description="Line one\nLine & two\n"
    )
    rich = GraffitiPhoto.objects.create(
        graffiti_wall=wall, identifier="R", description="<div>Already HTML</div>"
    )

    description_migration.plain_text_descriptions_to_html(apps, None)

    plain.refresh_from_db()
    rich.refresh_from_db()
    assert plain.description == "<p>Line one<br>Line &amp; two</p>"
    assert rich.description == "<div>Already HTML</div>"


@pytest.mark.django_db
def test_photo_changelist_shows_description_without_markup(admin_client):
    wall = GraffitiWall.objects.create(
        name="Wall",
        image="images/wall.jpg",
        room="1",
        spatial_position="A1",
        wall_grid_position="A1",
        identifier="W1",
        date_taken=datetime.date(2020, 1, 1),
        site_id=Site.objects.create(name="Site"),
    )
    GraffitiPhoto.objects.create(
        graffiti_wall=wall,
        identifier="R",
        description="<div>Name and unit:&nbsp;</div><blockquote>S C Hollingsworth</blockquote>",
    )

    response = admin_client.get(reverse("admin:graffiti_graffitiphoto_changelist"))

    assert "Name and unit: S C Hollingsworth" in response.content.decode()
    assert "&lt;blockquote&gt;" not in response.content.decode()

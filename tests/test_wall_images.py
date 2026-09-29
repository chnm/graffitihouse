import datetime
import importlib
import io
import logging

import pytest
from django.apps import apps
from django.core.files.base import ContentFile
from django.urls import reverse
from PIL import Image

from graffiti.models import GraffitiPhoto, GraffitiWall, Site

dimensions_migration = importlib.import_module(
    "graffiti.migrations.0017_graffitiwall_image_dimensions"
)


def png(width, height):
    buffer = io.BytesIO()
    Image.new("RGB", (width, height)).save(buffer, format="PNG")
    return ContentFile(buffer.getvalue())


def new_wall(**kwargs):
    return GraffitiWall(
        name="Wall",
        room="1",
        spatial_position="A1",
        wall_grid_position="A1",
        identifier="W1",
        date_taken=datetime.date(2020, 1, 1),
        site_id=Site.objects.create(name="Site"),
        **kwargs,
    )


@pytest.fixture(autouse=True)
def media(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    return tmp_path


@pytest.mark.django_db
def test_saving_a_wall_stores_its_image_size():
    wall = new_wall()
    wall.image.save("wall.png", png(40, 30), save=True)

    wall.refresh_from_db()
    assert (wall.image_width, wall.image_height) == (40, 30)

    wall.image.save("replacement.png", png(8, 6), save=True)

    wall.refresh_from_db()
    assert (wall.image_width, wall.image_height) == (8, 6)


@pytest.mark.django_db
def test_missing_image_file_is_logged_not_raised(caplog):
    wall = new_wall(image="images/missing.jpg")

    with caplog.at_level(logging.WARNING, logger="graffiti.models"):
        wall.save()

    assert (wall.image_width, wall.image_height) == (None, None)
    assert "missing.jpg" in caplog.text


@pytest.mark.django_db
def test_wall_page_shows_a_note_when_the_image_is_missing(client):
    wall = new_wall(image="images/missing.jpg")
    wall.save()

    response = client.get(reverse("graffiti:overall_image", args=[wall.id]))

    html = response.content.decode()
    assert response.status_code == 200
    assert 'id="map"' not in html
    assert "The image of this wall is unavailable" in html
    assert wall.name in html
    assert 'id="map-hint" class="callout__hint" hidden' in html


@pytest.mark.django_db
def test_missing_image_note_links_to_the_walls_graffiti(client):
    wall = new_wall(image="images/missing.jpg")
    wall.save()
    photo = GraffitiPhoto.objects.create(
        graffiti_wall=wall, identifier="G1", graffiti_type="name"
    )

    html = client.get(
        reverse("graffiti:overall_image", args=[wall.id])
    ).content.decode()

    link = reverse("graffiti:derived_image_detail", args=[photo.id])
    assert f'<a href="{link}">G1</a> (name)' in html


@pytest.mark.django_db
def test_wall_page_fills_in_a_missing_size_without_history(client):
    wall = new_wall()
    wall.image.save("wall.png", png(40, 30), save=True)
    GraffitiWall.objects.filter(pk=wall.pk).update(image_width=None, image_height=None)
    history_before = wall.history.count()

    response = client.get(reverse("graffiti:overall_image", args=[wall.id]))

    wall.refresh_from_db()
    html = response.content.decode()
    assert (wall.image_width, wall.image_height) == (40, 30)
    assert 'id="map"' in html
    assert "var imageWidth = 40;" in html
    assert wall.history.count() == history_before


@pytest.mark.django_db
def test_pages_listing_walls_never_read_image_files(client):
    wall = new_wall(image="images/missing.jpg")
    wall.save()
    site = wall.site_id

    assert client.get(reverse("graffiti:walls_list")).status_code == 200
    assert (
        client.get(reverse("graffiti:site_detail", args=[site.id])).status_code == 200
    )
    assert client.get(reverse("home")).status_code == 200


@pytest.mark.django_db
def test_migration_stores_sizes_and_skips_unreadable_files():
    readable = new_wall()
    readable.image.save("wall.png", png(40, 30), save=True)
    missing = new_wall(image="images/missing.jpg")
    missing.save()
    GraffitiWall.objects.update(image_width=None, image_height=None)

    dimensions_migration.store_image_dimensions(apps, None)

    readable.refresh_from_db()
    missing.refresh_from_db()
    assert (readable.image_width, readable.image_height) == (40, 30)
    assert (missing.image_width, missing.image_height) == (None, None)


@pytest.mark.django_db
def test_api_includes_wall_image_size(client):
    wall = new_wall()
    wall.image.save("wall.png", png(40, 30), save=True)

    body = client.get(f"/api/v1/walls/{wall.id}/").json()

    assert (body["image_width"], body["image_height"]) == (40, 30)

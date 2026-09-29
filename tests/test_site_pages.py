import datetime

import pytest
from django.urls import reverse
from PIL import Image

from graffiti.models import GraffitiWall, Site


def make_wall(site, name, room):
    return GraffitiWall.objects.create(
        name=name,
        image="images/wall.jpg",
        room=room,
        spatial_position="Wall A",
        wall_grid_position="A1",
        identifier=name,
        date_taken=datetime.date(2020, 1, 1),
        site_id=site,
    )


@pytest.mark.django_db
def test_site_index_separates_documented_from_pending(client):
    documented = Site.objects.create(name="Brandy Station")
    Site.objects.create(name="Liberia House")
    make_wall(documented, "W1", "201")

    html = client.get(reverse("graffiti:walls_list")).content.decode()

    assert "1 wall" in html
    assert html.index("Brandy Station") < html.index("Documentation in progress")
    assert html.index("Documentation in progress") < html.index("Liberia House")


@pytest.mark.django_db
def test_site_page_groups_walls_by_room(client):
    site = Site.objects.create(name="Brandy Station")
    make_wall(site, "W1", "201")
    make_wall(site, "W2", "201")
    make_wall(site, "W3", "200")

    html = client.get(reverse("graffiti:site_detail", args=[site.id])).content.decode()

    assert html.count("Room 200") >= 1 and html.count("Room 201") >= 1
    assert html.index("Room 200") < html.index("Room 201")
    assert "2 walls" in html


@pytest.mark.django_db
def test_wall_page_hides_internal_notes(client, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    (tmp_path / "images").mkdir()
    Image.new("RGB", (4, 4)).save(tmp_path / "images" / "wall.jpg")
    wall = make_wall(Site.objects.create(name="Site"), "W1", "201")
    wall.notes = "Internal project note"
    wall.conservation_notes = "Internal conservation note"
    wall.save()

    html = client.get(
        reverse("graffiti:overall_image", args=[wall.id])
    ).content.decode()

    assert "Internal project note" not in html
    assert "Internal conservation note" not in html


@pytest.mark.django_db
def test_unknown_url_renders_not_found_page(client, settings):
    settings.DEBUG = False

    response = client.get("/no-such-page/")

    assert response.status_code == 404
    assert "Page Not Found" in response.content.decode()

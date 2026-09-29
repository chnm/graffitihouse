import datetime

import pytest
from django.urls import reverse
from PIL import Image

from graffiti.models import GraffitiPhoto, GraffitiWall, Site


@pytest.fixture
def records(settings, tmp_path):
    # The wall page reads its image's size from disk, so give it a real file.
    settings.MEDIA_ROOT = tmp_path
    (tmp_path / "images").mkdir()
    Image.new("RGB", (4, 4)).save(tmp_path / "images" / "wall.jpg")
    site = Site.objects.create(name="Brandy Station Graffiti House")
    wall = GraffitiWall.objects.create(
        name="HB RM 302 Wall C",
        image="images/wall.jpg",
        room="302",
        spatial_position="C",
        wall_grid_position="C",
        identifier="W1",
        date_taken=datetime.date(2020, 1, 1),
        site_id=site,
    )
    photo = GraffitiPhoto.objects.create(graffiti_wall=wall, identifier="G1")
    return site, wall, photo


@pytest.mark.django_db
def test_pages_live_at_flat_urls(client, records):
    site, wall, photo = records

    assert reverse("graffiti:walls_list") == "/sites/"
    assert site.get_absolute_url() == f"/sites/{site.id}/"
    assert wall.get_absolute_url() == f"/walls/{wall.id}/"
    assert (
        reverse("graffiti:derived_image_detail", args=[photo.id])
        == f"/graffiti/{photo.id}/"
    )
    for path in [
        "/sites/",
        f"/sites/{site.id}/",
        f"/walls/{wall.id}/",
        f"/graffiti/{photo.id}/",
    ]:
        assert client.get(path).status_code == 200, path


@pytest.mark.django_db
def test_old_urls_redirect_permanently(client, records):
    site, wall, photo = records
    moves = {
        "/graffiti/": "/sites/",
        f"/graffiti/site/{site.id}/": f"/sites/{site.id}/",
        f"/graffiti/wall/{wall.id}/": f"/walls/{wall.id}/",
        f"/graffiti/derived-image/{photo.id}/": f"/graffiti/{photo.id}/",
        "/graffiti/?tag=cavalry": "/sites/?tag=cavalry",
    }

    for old, new in moves.items():
        response = client.get(old)
        assert response.status_code == 301, old
        assert response["Location"] == new, old


@pytest.mark.django_db
def test_breadcrumbs_trace_site_wall_and_graffiti(client, records):
    site, wall, photo = records

    html = client.get(f"/graffiti/{photo.id}/").content.decode()

    trail = html[html.index('class="breadcrumbs"') :]
    trail = trail[: trail.index("</nav>")]
    assert trail.index('href="/sites/"') < trail.index(f'href="/sites/{site.id}/"')
    assert trail.index(f'href="/sites/{site.id}/"') < trail.index(
        f'href="/walls/{wall.id}/"'
    )
    assert '<li aria-current="page">G1</li>' in trail


@pytest.mark.django_db
def test_nav_links_to_sites_list(client):
    html = client.get(reverse("home")).content.decode()

    assert 'href="/sites/" class="site-nav__link">Sites</a>' in html
    assert ">Graffiti</a>" not in html

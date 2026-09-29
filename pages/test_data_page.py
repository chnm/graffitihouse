import datetime
import re

import pytest
from django.urls import reverse

from graffiti.models import GraffitiWall, Site


@pytest.mark.django_db
def test_data_page_links_every_example_to_a_working_api_request(client):
    Site.objects.create(name="Empty site")
    documented = Site.objects.create(name="Brandy Station")
    GraffitiWall.objects.create(
        name="Wall",
        image="images/wall.jpg",
        room="1",
        spatial_position="A1",
        wall_grid_position="A1",
        identifier="W1",
        date_taken=datetime.date(2020, 1, 1),
        site_id=documented,
    )

    response = client.get(reverse("data"))

    assert response.status_code == 200
    html = response.content.decode()
    api_root = "http://testserver" + reverse("api:api-root")
    assert f'href="{api_root}"' in html
    assert f"walls/?site={documented.id}" in html
    assert "CC BY 4.0" in html
    links = set(re.findall(r'href="(http://testserver/api/v1/[^"]*)"', html))
    assert len(links) >= 10
    for link in links:
        path = link.removeprefix("http://testserver").replace("&amp;", "&")
        assert client.get(path).status_code == 200, path


@pytest.mark.django_db
def test_footer_links_to_data_page(client):
    html = client.get(reverse("home")).content.decode()

    assert f'href="{reverse("data")}"' in html


@pytest.mark.django_db
def test_links_use_https_behind_the_https_proxy(client):
    Site.objects.create(name="Brandy Station")

    # As Caddy forwards it: the public host, and the original scheme.
    proxied = {"host": "testserver", "x-forwarded-proto": "https"}
    page = client.get(reverse("data"), headers=proxied)
    api = client.get("/api/v1/sites/", headers=proxied)

    assert 'href="https://testserver/api/v1/"' in page.content.decode()
    assert api.json()["results"][0]["url"].startswith("https://testserver/")

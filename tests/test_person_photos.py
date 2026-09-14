import datetime

import pytest
from django.urls import reverse

from graffiti.models import GraffitiPhoto, GraffitiWall, Site
from people.models import Person


@pytest.mark.django_db
def test_person_detail_lists_every_associated_photo(client):
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
    person = Person.objects.create(last_name="Doe")
    person.associated_graffiti_photos.set(
        GraffitiPhoto.objects.create(graffiti_wall=wall, identifier=f"IMG_{n}")
        for n in (1, 2)
    )

    html = client.get(
        reverse("people:person_detail", kwargs={"person_id": person.id})
    ).content.decode()

    assert "IMG_1" in html and "IMG_2" in html

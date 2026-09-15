import datetime
import io

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image

from graffiti.models import GraffitiWall, Site


def make_wall(**kwargs):
    return GraffitiWall.objects.create(
        name="Wall",
        image="images/wall.jpg",
        room="1",
        spatial_position="A1",
        wall_grid_position="A1",
        identifier=kwargs.pop("identifier", "W1"),
        date_taken=datetime.date(2020, 1, 1),
        site_id=Site.objects.create(name="Site"),
        **kwargs,
    )


@pytest.mark.django_db
def test_student_can_delete_only_own_rows(client):
    student = get_user_model().objects.create_user("s", "s@example.org", is_staff=True)
    student.groups.add(Group.objects.get(name="Students"))
    client.force_login(student)

    own = make_wall(created_by=student, identifier="W1")
    other = make_wall(identifier="W2")

    assert (
        client.get(
            reverse("admin:graffiti_graffitiwall_delete", args=[own.id])
        ).status_code
        == 200
    )
    assert (
        client.get(
            reverse("admin:graffiti_graffitiwall_delete", args=[other.id])
        ).status_code
        == 403
    )


@pytest.mark.django_db
def test_admin_records_creator(client, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    buffer = io.BytesIO()
    Image.new("RGB", (2, 2)).save(buffer, format="PNG")
    student = get_user_model().objects.create_user("s", "s@example.org", is_staff=True)
    student.groups.add(Group.objects.get(name="Students"))
    client.force_login(student)
    site = Site.objects.create(name="Site")

    client.post(
        reverse("admin:graffiti_graffitiwall_add"),
        {
            "name": "New",
            "room": "1",
            "spatial_position": "A",
            "wall_grid_position": "A",
            "identifier": "N1",
            "image": SimpleUploadedFile("w.png", buffer.getvalue(), "image/png"),
            "date_taken": "2020-01-01",
            "site_id": site.id,
            "multispectral_images-TOTAL_FORMS": 0,
            "multispectral_images-INITIAL_FORMS": 0,
        },
    )
    assert GraffitiWall.objects.get(identifier="N1").created_by == student

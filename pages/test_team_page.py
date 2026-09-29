import io

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image

from pages.models import TeamGroup, TeamMember


def make_member(name, **kwargs):
    return TeamMember.objects.create(name=name, role="Researcher", **kwargs)


@pytest.mark.django_db
def test_team_page_lists_active_members_grouped_and_ordered(client):
    make_member("Zed Collaborator", group=TeamGroup.COLLABORATOR, order=0)
    make_member("Second Lead", group=TeamGroup.TEAM, order=2)
    make_member("First Lead", group=TeamGroup.TEAM, order=1)
    make_member("Also First", group=TeamGroup.TEAM, order=1)

    response = client.get(reverse("team"))

    assert response.status_code == 200
    html = response.content.decode()
    positions = [
        html.index(text)
        for text in (
            "Project team",
            "Also First",
            "First Lead",
            "Second Lead",
            "Collaborators",
            "Zed Collaborator",
        )
    ]
    assert positions == sorted(positions)


@pytest.mark.django_db
def test_team_page_hides_inactive_members(client):
    make_member("Visible Person")
    make_member("Hidden Person", is_active=False)

    html = client.get(reverse("team")).content.decode()

    assert "Visible Person" in html
    assert "Hidden Person" not in html


@pytest.mark.django_db
def test_team_page_omits_groups_with_no_active_members(client):
    make_member("Only Team Member", group=TeamGroup.TEAM)
    make_member("Former Collaborator", group=TeamGroup.COLLABORATOR, is_active=False)

    html = client.get(reverse("team")).content.decode()

    assert "Project team" in html
    assert "Collaborators" not in html


@pytest.mark.django_db
def test_team_page_shows_initials_when_there_is_no_photo(client):
    make_member("Ada Byron Lovelace")

    html = client.get(reverse("team")).content.decode()

    assert '<span class="avatar team-card__photo" aria-hidden="true">AL</span>' in html


@pytest.mark.django_db
def test_team_page_shows_photo_with_name_as_alt_text(client, settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path
    buffer = io.BytesIO()
    Image.new("RGB", (4, 4)).save(buffer, format="JPEG")
    member = make_member(
        "Pictured Person",
        photo=SimpleUploadedFile("p.jpg", buffer.getvalue(), "image/jpeg"),
        website="https://example.org/",
    )

    html = client.get(reverse("team")).content.decode()

    assert f'src="{member.photo.url}" alt="Pictured Person"' in html
    assert 'loading="lazy"' in html
    assert 'href="https://example.org/"' in html


@pytest.mark.django_db
def test_team_page_empty_state(client):
    make_member("Hidden Person", is_active=False)

    response = client.get(reverse("team"))

    assert response.status_code == 200
    assert "still putting this page together" in response.content.decode()


def test_about_permanently_redirects_to_team(client):
    response = client.get("/about/")

    assert response.status_code == 301
    assert response["Location"] == reverse("team")


def test_museum_permanently_redirects_to_sites_list(client):
    response = client.get("/museum/")

    assert response.status_code == 301
    assert response["Location"] == reverse("graffiti:walls_list")


@pytest.mark.django_db
def test_nav_links_to_team_page(client):
    html = client.get(reverse("home")).content.decode()

    assert html.count(f'href="{reverse("team")}"') == 2


@pytest.mark.django_db
def test_admin_changelist_and_add_form_load_for_superuser(client):
    admin = get_user_model().objects.create_superuser("admin", "a@example.org", "pw")
    client.force_login(admin)
    make_member("Listed Person")

    changelist = client.get(reverse("admin:pages_teammember_changelist"))
    add = client.get(reverse("admin:pages_teammember_add"))

    assert changelist.status_code == 200
    assert "Listed Person" in changelist.content.decode()
    assert add.status_code == 200

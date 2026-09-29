import importlib

import pytest
from django.apps import apps
from django.urls import reverse

from people.models import Person, Service

service_migration = importlib.import_module(
    "people.migrations.0006_service_rank_and_army_branch_choices"
)


@pytest.mark.django_db
def test_migration_moves_cavalry_and_maps_ranks():
    person = Person.objects.create(last_name="Marshall")
    cavalry = Service.objects.create(
        person=person, military_rank="Captain", military_branch="cavalry"
    )
    spaced = Service.objects.create(person=person, military_rank="Lieutenant  Colonel")
    unknown = Service.objects.create(person=person, military_rank="Capt.")

    service_migration.forwards(apps, None)

    cavalry.refresh_from_db()
    spaced.refresh_from_db()
    unknown.refresh_from_db()
    assert (cavalry.military_branch, cavalry.military_division) == ("army", "cavalry")
    assert cavalry.military_rank == "captain"
    assert spaced.military_rank == "lieutenant_colonel"
    assert unknown.military_rank == "Capt."


@pytest.mark.django_db
def test_person_page_shows_rank_and_army_branch_labels(client):
    person = Person.objects.create(last_name="Hollingsworth")
    Service.objects.create(
        person=person,
        military_rank="2nd_lieutenant",
        military_branch="army",
        military_division="signal_corps",
    )

    response = client.get(reverse("people:person_detail", args=[person.id]))

    content = response.content.decode()
    assert "2nd Lieutenant" in content
    assert "Army branch" in content
    assert "Signal Corps" in content


@pytest.mark.django_db
def test_service_heading_joins_rank_and_unit_with_a_comma(client):
    ranked = Person.objects.create(last_name="Hollingsworth")
    Service.objects.create(
        person=ranked, military_rank="private", military_unit="Company K"
    )
    unranked = Person.objects.create(last_name="Marshall")
    Service.objects.create(person=unranked, military_unit="Company E")

    ranked_page = client.get(reverse("people:person_detail", args=[ranked.id]))
    unranked_page = client.get(reverse("people:person_detail", args=[unranked.id]))
    people_list = client.get(reverse("people:people_list")).content.decode()

    assert "Private, Company K" in ranked_page.content.decode()
    assert ", Company E" not in unranked_page.content.decode()
    assert "Private, Company K" in people_list
    assert ", Company E" not in people_list

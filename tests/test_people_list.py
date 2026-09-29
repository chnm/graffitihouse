import pytest
from django.urls import reverse

from people.models import Person


@pytest.mark.django_db
def test_people_list_files_each_person_under_one_initial(client):
    for last_name in ["Adams", "de Vries", "Dawson", "Éclair", "Østergaard", "1st"]:
        Person.objects.create(last_name=last_name)

    response = client.get(reverse("people:people_list"))

    groups = {
        letter: [person.last_name for person in group]
        for letter, group in response.context["letter_groups"]
    }
    others = [person.last_name for person in response.context["other_people"]]
    assert list(groups) == ["A", "D", "E"]
    assert sorted(groups["D"]) == ["Dawson", "de Vries"]
    assert groups["E"] == ["Éclair"]
    assert sorted(others) == ["1st", "Østergaard"]
    assert sum(len(names) for names in groups.values()) + len(others) == 6
    assert 'id="other"' in response.content.decode()


@pytest.mark.django_db
def test_people_list_omits_other_section_when_empty(client):
    Person.objects.create(last_name="Adams")

    response = client.get(reverse("people:people_list"))

    assert response.context["other_people"] == []
    assert 'id="other"' not in response.content.decode()

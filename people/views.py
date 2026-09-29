import string
import unicodedata

from django.shortcuts import get_object_or_404, render

from .models import Person


def surname_initial(last_name):
    """Return the A-Z letter a surname is filed under, or None.

    Accented initials file under their base letter (É under E); anything
    that doesn't reduce to A-Z (digits, punctuation, Ø) returns None.
    """
    initial = unicodedata.normalize("NFKD", last_name.strip())[:1].upper()
    return initial if initial and initial in string.ascii_uppercase else None


def people_list(request):
    """View for listing all people in the project"""
    # Get all people, ordered by last name then first name
    people = Person.objects.all().order_by("last_name", "first_name")

    # Group in Python rather than with {% regroup %}, which only merges
    # adjacent rows and duplicated names that don't start with A-Z.
    by_letter = {letter: [] for letter in string.ascii_uppercase}
    other_people = []
    for person in people:
        initial = surname_initial(person.last_name)
        if initial:
            by_letter[initial].append(person)
        else:
            other_people.append(person)

    context = {
        "letter_groups": [
            (letter, group) for letter, group in by_letter.items() if group
        ],
        "other_people": other_people,
        "total_count": len(people),
    }

    return render(request, "people/people_list.html", context)


def person_detail(request, person_id):
    """View for showing details of a specific person"""
    # Get the person or return 404
    person = get_object_or_404(Person, id=person_id)

    context = {
        "person": person,
        "aliases": person.alias_set.all(),
        "organizations": person.organization_set.all(),
        "service_records": person.service_set.all(),
        "associated_photos": person.associated_graffiti_photos.all(),
    }

    return render(request, "people/person_detail.html", context)

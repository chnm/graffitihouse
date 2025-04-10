from django.shortcuts import get_object_or_404, render

from .models import Alias, Organization, Person, Service


def people_list(request):
    """View for listing all people in the project"""
    # Get all people, ordered by last name then first name
    people = Person.objects.all().order_by("last_name", "first_name")

    context = {
        "people": people,
        "total_count": people.count(),
    }

    return render(request, "people/people_list.html", context)


def person_detail(request, person_id):
    """View for showing details of a specific person"""
    # Get the person or return 404
    person = get_object_or_404(Person, id=person_id)

    # Get related information
    aliases = Alias.objects.filter(person=person)
    organizations = Organization.objects.filter(person=person)
    service_records = Service.objects.filter(person=person)

    context = {
        "person": person,
        "aliases": aliases,
        "organizations": organizations,
        "service_records": service_records,
    }

    return render(request, "people/person_detail.html", context)

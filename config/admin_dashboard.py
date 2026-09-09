from django.urls import reverse

from graffiti.models import GraffitiPhoto, GraffitiWall, Site
from people.models import Person
from source.models import AncillarySource


def dashboard_callback(request, context):
    """Populate the Unfold admin index with project-level activity."""
    stats = []
    if request.user.has_perm("graffiti.view_graffitiwall"):
        stats.append(
            {
                "title": "Walls",
                "value": GraffitiWall.objects.count(),
                "icon": "imagesmode",
                "link": reverse("admin:graffiti_graffitiwall_changelist"),
            }
        )
    if request.user.has_perm("graffiti.view_graffitiphoto"):
        stats.append(
            {
                "title": "Graffiti photos",
                "value": GraffitiPhoto.objects.count(),
                "icon": "photo_library",
                "link": reverse("admin:graffiti_graffitiphoto_changelist"),
            }
        )
    if request.user.has_perm("people.view_person"):
        stats.append(
            {
                "title": "People",
                "value": Person.objects.count(),
                "icon": "person",
                "link": reverse("admin:people_person_changelist"),
            }
        )
    if request.user.has_perm("source.view_ancillarysource"):
        stats.append(
            {
                "title": "Sources",
                "value": AncillarySource.objects.count(),
                "icon": "description",
                "link": reverse("admin:source_ancillarysource_changelist"),
            }
        )

    quick_actions = []
    action_definitions = (
        (
            "graffiti.add_graffitiwall",
            "Add a wall",
            "add_photo_alternate",
            "admin:graffiti_graffitiwall_add",
        ),
        (
            "graffiti.add_graffitiphoto",
            "Add a graffiti photo",
            "add_a_photo",
            "admin:graffiti_graffitiphoto_add",
        ),
        (
            "people.add_person",
            "Add a person",
            "person_add",
            "admin:people_person_add",
        ),
        (
            "source.add_ancillarysource",
            "Add a source",
            "note_add",
            "admin:source_ancillarysource_add",
        ),
    )
    for permission, title, icon, url_name in action_definitions:
        if request.user.has_perm(permission):
            quick_actions.append(
                {
                    "title": title,
                    "icon": icon,
                    "link": reverse(url_name),
                }
            )

    context.update(
        {
            "dashboard_stats": stats,
            "quick_actions": quick_actions,
            "recent_walls": GraffitiWall.objects.select_related("site_id").order_by(
                "-created_at"
            )[:5]
            if request.user.has_perm("graffiti.view_graffitiwall")
            else [],
            "recent_photos": GraffitiPhoto.objects.select_related(
                "graffiti_wall"
            ).order_by("-created_at")[:5]
            if request.user.has_perm("graffiti.view_graffitiphoto")
            else [],
            "site_count": Site.objects.count()
            if request.user.has_perm("graffiti.view_site")
            else None,
        }
    )
    return context

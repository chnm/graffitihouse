from django.urls import reverse

from graffiti.models import GraffitiPhoto, GraffitiWall, Site
from people.models import Person
from source.models import AncillarySource


def dashboard_callback(request, context):
    """Populate the Unfold admin index with project-level activity."""
    stat_definitions = (
        (
            "graffiti.view_graffitiwall",
            "Walls",
            GraffitiWall,
            "imagesmode",
            "admin:graffiti_graffitiwall_changelist",
        ),
        (
            "graffiti.view_graffitiphoto",
            "Graffiti photos",
            GraffitiPhoto,
            "photo_library",
            "admin:graffiti_graffitiphoto_changelist",
        ),
        (
            "people.view_person",
            "People",
            Person,
            "person",
            "admin:people_person_changelist",
        ),
        (
            "source.view_ancillarysource",
            "Sources",
            AncillarySource,
            "description",
            "admin:source_ancillarysource_changelist",
        ),
    )
    stats = [
        {
            "title": title,
            "value": model.objects.count(),
            "icon": icon,
            "link": reverse(url_name),
        }
        for permission, title, model, icon, url_name in stat_definitions
        if request.user.has_perm(permission)
    ]

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

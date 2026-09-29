"""Public, read-only API views.

Every viewset is a `ReadOnlyModelViewSet`, so only GET, HEAD and OPTIONS are
routed; writes get 405 for everyone. Authentication is disabled (see
`REST_FRAMEWORK` in settings), so every caller, staff included, sees exactly
the same public data and is subject to the anonymous throttle.
"""

from django.db.models import Count, Prefetch
from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from graffiti.models import GraffitiPhoto, GraffitiWall, Location, Site
from people.models import Person

from . import filters, serializers


class PublicReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    ordering = ["id"]


class LocationViewSet(PublicReadOnlyViewSet):
    """Places where graffiti sites are found."""

    queryset = Location.objects.all()
    serializer_class = serializers.LocationSerializer
    filterset_class = filters.LocationFilter
    search_fields = ["place", "address", "city", "state"]
    ordering_fields = ["id", "place", "city", "state"]


class SiteViewSet(PublicReadOnlyViewSet):
    """Structures or spaces with walls that carry graffiti."""

    queryset = (
        Site.objects.select_related("location")
        .prefetch_related("tags")
        .annotate(
            wall_count=Count("graffitiwall", distinct=True),
            photo_count=Count("graffitiwall__graffitiphoto", distinct=True),
        )
    )
    serializer_class = serializers.SiteSerializer
    filterset_class = filters.SiteFilter
    search_fields = ["name", "description", "location__place", "location__city"]
    ordering_fields = ["id", "name", "wall_count", "photo_count", "updated_at"]


class WallViewSet(PublicReadOnlyViewSet):
    """Photographed walls; each belongs to a site."""

    queryset = GraffitiWall.objects.prefetch_related("tags").annotate(
        photo_count=Count("graffitiphoto")
    )
    serializer_class = serializers.WallSerializer
    filterset_class = filters.WallFilter
    search_fields = ["name", "identifier", "room", "spatial_position", "description"]
    ordering_fields = [
        "id",
        "name",
        "identifier",
        "room",
        "spatial_position",
        "date_taken",
        "photo_count",
        "updated_at",
    ]


class PhotoViewSet(PublicReadOnlyViewSet):
    """Individual pieces of graffiti, cropped from a wall photograph."""

    queryset = (
        GraffitiPhoto.objects.select_related("graffiti_wall")
        .defer("coordinates")
        .prefetch_related(
            "tags",
            Prefetch("associated_people", queryset=Person.objects.only("id")),
        )
    )
    serializer_class = serializers.PhotoSerializer
    filterset_class = filters.PhotoFilter
    search_fields = ["identifier", "description"]
    ordering_fields = ["id", "identifier", "graffiti_type", "updated_at"]


class PersonViewSet(PublicReadOnlyViewSet):
    """People connected to the graffiti, with their service records."""

    queryset = Person.objects.prefetch_related(
        "tags",
        "alias_set",
        "organization_set",
        "service_set",
        Prefetch(
            "associated_graffiti_photos", queryset=GraffitiPhoto.objects.only("id")
        ),
    )
    serializer_class = serializers.PersonSerializer
    filterset_class = filters.PersonFilter
    search_fields = [
        "first_name",
        "middle_name_or_initial",
        "last_name",
        "alias__name",
        "organization__name",
    ]
    ordering = ["last_name", "first_name", "id"]
    ordering_fields = ["id", "last_name", "first_name", "date_of_birth", "updated_at"]

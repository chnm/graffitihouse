import django_filters

from graffiti.models import GraffitiPhoto, GraffitiType, GraffitiWall, Location, Site
from people.models import ArmyBranch, Branch, Governance, Person, Rank


def tag_filter():
    return django_filters.CharFilter(
        field_name="tags__name",
        lookup_expr="iexact",
        distinct=True,
        label="Tag name (case-insensitive exact match).",
    )


class LocationFilter(django_filters.FilterSet):
    state = django_filters.CharFilter(lookup_expr="iexact")
    city = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = Location
        fields = ["state", "city"]


class SiteFilter(django_filters.FilterSet):
    location = django_filters.NumberFilter(field_name="location")
    state = django_filters.CharFilter(
        field_name="location__state", lookup_expr="iexact"
    )
    tag = tag_filter()

    class Meta:
        model = Site
        fields = ["location", "state", "tag"]


class WallFilter(django_filters.FilterSet):
    site = django_filters.NumberFilter(field_name="site_id")
    room = django_filters.CharFilter(lookup_expr="iexact")
    date_taken = django_filters.DateFromToRangeFilter(
        label="Use date_taken_after / date_taken_before (YYYY-MM-DD)."
    )
    tag = tag_filter()

    class Meta:
        model = GraffitiWall
        fields = ["site", "room", "date_taken", "tag"]


class PhotoFilter(django_filters.FilterSet):
    wall = django_filters.NumberFilter(field_name="graffiti_wall")
    site = django_filters.NumberFilter(field_name="graffiti_wall__site_id")
    graffiti_type = django_filters.ChoiceFilter(choices=GraffitiType.choices)
    person = django_filters.NumberFilter(field_name="associated_people", distinct=True)
    tag = tag_filter()

    class Meta:
        model = GraffitiPhoto
        fields = ["wall", "site", "graffiti_type", "person", "tag"]


class PersonFilter(django_filters.FilterSet):
    governance = django_filters.ChoiceFilter(
        field_name="service__military_governance",
        choices=Governance.choices,
        distinct=True,
    )
    rank = django_filters.ChoiceFilter(
        field_name="service__military_rank", choices=Rank.choices, distinct=True
    )
    military_branch = django_filters.ChoiceFilter(
        field_name="service__military_branch", choices=Branch.choices, distinct=True
    )
    army_branch = django_filters.ChoiceFilter(
        field_name="service__military_division",
        choices=ArmyBranch.choices,
        distinct=True,
    )
    photo = django_filters.NumberFilter(
        field_name="associated_graffiti_photos", distinct=True
    )
    tag = tag_filter()

    class Meta:
        model = Person
        fields = [
            "governance",
            "rank",
            "military_branch",
            "army_branch",
            "photo",
            "tag",
        ]

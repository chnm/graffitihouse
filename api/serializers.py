"""Read-only serializers for the public API.

Conventions, applied everywhere:

* Each object carries its `id` and its API `url`; objects with a public page
  also carry `html_url`. A related object is given as `<name>` (its id) plus
  `<name>_url` (its API url), or as a list of `{"id", "url"}` references.
* Choice fields give the stored value (`military_rank`) and its label
  (`military_rank_display`); both are null when unset.
* Image fields are absolute URLs, or null when there is no file.

Only fields shown on the public site are exposed: internal notes,
`created_by`, change history, and ancillary sources are deliberately left out.
"""

from django.urls import reverse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from graffiti.models import GraffitiPhoto, GraffitiWall, Location, Site
from people.models import Alias, Organization, Person, Service


@extend_schema_field({"type": "array", "items": {"type": "string"}})
class TagListField(serializers.Field):
    """A taggit manager as a sorted list of tag names (uses prefetched tags)."""

    def __init__(self, **kwargs):
        kwargs.setdefault("read_only", True)
        super().__init__(**kwargs)

    def to_representation(self, value):
        return sorted(tag.name for tag in value.all())


@extend_schema_field(OpenApiTypes.URI)
class PublicPageURLField(serializers.Field):
    """The absolute URL of an object's public page on the website."""

    def __init__(self, **kwargs):
        kwargs.setdefault("read_only", True)
        kwargs.setdefault("source", "*")
        super().__init__(**kwargs)

    def to_representation(self, instance):
        path = (
            reverse("graffiti:derived_image_detail", args=[instance.pk])
            if isinstance(instance, GraffitiPhoto)
            else instance.get_absolute_url()
        )
        request = self.context.get("request")
        return request.build_absolute_uri(path) if request else path


class NullableChoiceField(serializers.ChoiceField):
    """A choice's stored value, with blank strings reported as null."""

    def __init__(self, choices, **kwargs):
        kwargs.setdefault("read_only", True)
        kwargs.setdefault("allow_null", True)
        super().__init__(choices, **kwargs)

    def to_representation(self, value):
        return super().to_representation(value) if value else None


class ChoiceDisplayField(serializers.CharField):
    """A choice's human-readable label (`get_<field>_display`), or null."""

    def __init__(self, field_name, **kwargs):
        kwargs.setdefault("read_only", True)
        kwargs.setdefault("allow_null", True)
        kwargs["source"] = f"get_{field_name}_display"
        super().__init__(**kwargs)

    def to_representation(self, value):
        return str(value) if value else None


def choices_of(model, field_name):
    return model._meta.get_field(field_name).choices


class ReferenceSerializer(serializers.Serializer):
    """`{"id", "url"}` for a related object; set `view_name` in a subclass."""

    id = serializers.IntegerField(read_only=True)


class PhotoReferenceSerializer(ReferenceSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="api:photo-detail")


class PersonReferenceSerializer(ReferenceSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="api:person-detail")


class LocationSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="api:location-detail")

    class Meta:
        model = Location
        fields = [
            "id",
            "url",
            "place",
            "address",
            "city",
            "state",
            "latitude",
            "longitude",
        ]


class SiteSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="api:site-detail")
    html_url = PublicPageURLField()
    description = serializers.CharField(
        read_only=True,
        allow_null=True,
        help_text="Plain text; the website renders line breaks as paragraphs.",
    )
    location = LocationSerializer(read_only=True, allow_null=True)
    image = serializers.ImageField(read_only=True, allow_null=True)
    tags = TagListField()
    wall_count = serializers.IntegerField(read_only=True)
    photo_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Site
        fields = [
            "id",
            "url",
            "html_url",
            "name",
            "description",
            "location",
            "image",
            "tags",
            "wall_count",
            "photo_count",
            "created_at",
            "updated_at",
        ]


class WallSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="api:wall-detail")
    html_url = PublicPageURLField()
    site = serializers.PrimaryKeyRelatedField(read_only=True, source="site_id")
    site_url = serializers.HyperlinkedRelatedField(
        read_only=True, source="site_id", view_name="api:site-detail"
    )
    description = serializers.CharField(
        read_only=True,
        allow_null=True,
        help_text="Sanitized HTML from the rich-text editor.",
    )
    image = serializers.ImageField(read_only=True)
    archival_image = serializers.ImageField(read_only=True, allow_null=True)
    tags = TagListField()
    photo_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = GraffitiWall
        fields = [
            "id",
            "url",
            "html_url",
            "name",
            "identifier",
            "site",
            "site_url",
            "room",
            "spatial_position",
            "wall_grid_position",
            "date_taken",
            "description",
            "image",
            "image_width",
            "image_height",
            "archival_image",
            "tags",
            "photo_count",
            "created_at",
            "updated_at",
        ]


class CropSerializer(serializers.Serializer):
    """The photo's rectangle, in pixels of its wall's `image`."""

    x = serializers.IntegerField()
    y = serializers.IntegerField()
    width = serializers.IntegerField()
    height = serializers.IntegerField()


class PhotoSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="api:photo-detail")
    html_url = PublicPageURLField()
    wall = serializers.PrimaryKeyRelatedField(read_only=True, source="graffiti_wall")
    wall_url = serializers.HyperlinkedRelatedField(
        read_only=True, source="graffiti_wall", view_name="api:wall-detail"
    )
    site = serializers.PrimaryKeyRelatedField(
        read_only=True, source="graffiti_wall.site_id"
    )
    site_url = serializers.HyperlinkedRelatedField(
        read_only=True, source="graffiti_wall.site_id", view_name="api:site-detail"
    )
    graffiti_type = NullableChoiceField(choices_of(GraffitiPhoto, "graffiti_type"))
    graffiti_type_display = ChoiceDisplayField("graffiti_type")
    description = serializers.CharField(
        read_only=True,
        allow_null=True,
        help_text="Sanitized HTML from the rich-text editor.",
    )
    image = serializers.ImageField(read_only=True, allow_null=True)
    crop = serializers.SerializerMethodField(
        help_text="Where the photo sits on its wall, in pixels of the wall's `image`; "
        "null when no rectangle was recorded."
    )
    tags = TagListField()
    people = PersonReferenceSerializer(
        many=True, read_only=True, source="associated_people"
    )

    class Meta:
        model = GraffitiPhoto
        fields = [
            "id",
            "url",
            "html_url",
            "identifier",
            "wall",
            "wall_url",
            "site",
            "site_url",
            "graffiti_type",
            "graffiti_type_display",
            "description",
            "image",
            "crop",
            "tags",
            "people",
            "created_at",
            "updated_at",
        ]

    @extend_schema_field(CropSerializer(allow_null=True))
    def get_crop(self, photo):
        if photo.rectangle is None:
            return None
        return {
            "x": photo.x,
            "y": photo.y,
            "width": photo.width,
            "height": photo.height,
        }


class AliasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alias
        fields = ["id", "name"]


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ["id", "name"]


class ServiceSerializer(serializers.ModelSerializer):
    military_rank = NullableChoiceField(choices_of(Service, "military_rank"))
    military_rank_display = ChoiceDisplayField("military_rank")
    military_branch = NullableChoiceField(choices_of(Service, "military_branch"))
    military_branch_display = ChoiceDisplayField("military_branch")
    # Stored as `military_division`; the project now calls it "Army branch".
    army_branch = NullableChoiceField(
        choices_of(Service, "military_division"), source="military_division"
    )
    army_branch_display = ChoiceDisplayField("military_division")
    military_governance = NullableChoiceField(
        choices_of(Service, "military_governance")
    )
    military_governance_display = ChoiceDisplayField("military_governance")

    class Meta:
        model = Service
        fields = [
            "id",
            "military_rank",
            "military_rank_display",
            "military_unit",
            "military_branch",
            "military_branch_display",
            "army_branch",
            "army_branch_display",
            "military_governance",
            "military_governance_display",
            "start_date",
            "end_date",
        ]


class PersonSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="api:person-detail")
    html_url = PublicPageURLField()
    description = serializers.CharField(
        read_only=True,
        allow_null=True,
        help_text="Rendered as HTML on the website; may contain markup.",
    )
    image = serializers.ImageField(read_only=True, allow_null=True)
    tags = TagListField()
    aliases = AliasSerializer(many=True, read_only=True, source="alias_set")
    organizations = OrganizationSerializer(
        many=True, read_only=True, source="organization_set"
    )
    service = ServiceSerializer(many=True, read_only=True, source="service_set")
    photos = PhotoReferenceSerializer(
        many=True, read_only=True, source="associated_graffiti_photos"
    )

    class Meta:
        model = Person
        fields = [
            "id",
            "url",
            "html_url",
            "first_name",
            "middle_name_or_initial",
            "last_name",
            "description",
            "image",
            "date_of_birth",
            "date_of_death",
            "tags",
            "aliases",
            "organizations",
            "service",
            "photos",
            "created_at",
            "updated_at",
        ]

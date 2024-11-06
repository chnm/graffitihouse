import logging

logger = logging.getLogger(__name__)

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from geopy.geocoders import Nominatim
from prose.fields import RichTextField
from taggit_selectize.managers import TaggableManager


# Graffiti is a specific wall from a site.
class GraffitiWall(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = RichTextField(blank=True, null=True)
    image = models.ImageField(upload_to="images/")
    room = models.CharField(max_length=255, help_text="Record the room name/number.")
    spatial_position = models.CharField(
        max_length=100,
        help_text="Record the region code for this wall (e.g., B1, C3).",
    )
    identifier = models.CharField(
        max_length=100,
        help_text="Identifier refers to the number produced by the camera/phone. Please ensure these match.",
    )
    has_part = models.ManyToManyField(
        "GraffitiPhoto",
        blank=True,
        help_text="A related resource that is included either physically or logically in the described resource.",
        related_name="graffiti_photo_has_part",
    )
    date_taken = models.DateField(help_text="Record the date the photograph was taken.")
    site_id = models.ForeignKey("Site", on_delete=models.CASCADE, verbose_name="Site")
    tags = TaggableManager(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # When a user draws a selection of graffiti, a new canvas coordinate
    # is added to the graffiti_has_part table
    def add_canvas(self, canvas):
        self.canvas = canvas
        self.save()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("detail", kwargs={"graffiti_id": self.id})

    def description_as_markdown(self):
        return mark_safe(self.description)

    description_as_markdown.allow_tags = True

    def image_canvas(self):
        if self.image:
            return mark_safe(
                '<img src="%s" style="width:100px; height:100px;" />' % self.image.url
            )
        else:
            return "No Image Found"

    image_canvas.short_description = "Image"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            WallRecordHistory.objects.create(
                photo_record=self, action="CREATE", data=self.to_dict()
            )
        else:
            WallRecordHistory.objects.create(
                photo_record=self, action="UPDATE", data=self.to_dict()
            )

    def to_dict(self):
        return {
            "id": self.id,
            "image": self.image.url,
            "name": self.name,
            "description": self.description,
            "room": self.room,
            "spatial_position": self.spatial_position,
            "identifier": self.identifier,
            "date_taken": self.date_taken,
        }

    def rollback(self, version):
        history_entry = self.history.filter(id__lte=version).order_by("-id").first()
        if history_entry:
            data = history_entry.data
            for key, value in data:
                setattr(self, key, value)
            self.save()
        else:
            raise ValueError("Invalid version for rollback.")


class WallRecordHistory(models.Model):
    photo_record = models.ForeignKey(
        GraffitiWall, on_delete=models.CASCADE, related_name="history"
    )
    action = models.CharField(max_length=10)  # 'CREATE', 'UPDATE', 'DELETE'
    data = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Wall Record Histories"


# GraffitiPhoto is a specific piece of graffiti from an overall wall.
class GraffitiPhoto(models.Model):
    GRAFFITI_TYPES = (
        ("Item 1", "Item 1"),
        ("Item 2", "Item 2"),
        ("Item 3", "Item 3"),
    )
    id = models.BigAutoField(primary_key=True)
    graffiti_wall = models.ForeignKey(
        GraffitiWall,
        on_delete=models.CASCADE,
        verbose_name="Graffiti wall",
        help_text="Select the graffiti wall this photo belongs to.",
    )
    graffiti_type = models.CharField(null=True, max_length=100, choices=GRAFFITI_TYPES)
    description = RichTextField(blank=True, null=True)
    image = models.ImageField(upload_to="images/derived/", null=True)
    identifier = models.CharField(
        max_length=100,
        help_text="Identifier refers to the number produced by the camera/phone. Please ensure these match.",
    )
    has_part = models.ManyToManyField(
        "GraffitiWall",
        blank=True,
        help_text="A related resource that is included either physically or logically in the described resource.",
        related_name="graffiti_has_part",
    )
    is_part_of = models.ManyToManyField(
        "GraffitiWall",
        blank=True,
        help_text="A related resource in which the described resource is physically or logically included.",
        related_name="graffiti_is_part_of",
    )
    tags = TaggableManager(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    canvas = models.TextField(null=True, blank=True)
    coordinates = models.JSONField(null=True)
    canvas_coords = models.TextField(null=True, blank=True, default="[]")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# Ancellary sources include maps, deeds, service records, letters, and other primary
# documents related to a specific image. These are connected to specific
# metadata for individual object types. These can be associated with specific
# pieces of graffiti or people.
class AncillarySource(models.Model):
    DOCUMENT_TYPES = (
        ("image", "Image"),
        ("newsprint", "Newsprint"),
        ("wall", "Wall"),
        ("letter", "Letter"),
        ("photograph", "Photograph"),
        ("drawing", "Drawing"),
        ("artwork", "Artwork"),
        ("game", "Game"),
        ("poem", "Poem"),
        ("other", "Other"),
    )

    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to="images/", null=True)
    item_type = models.CharField(max_length=100, choices=DOCUMENT_TYPES)
    creator = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="An entity primarily responsible for making the resource.",
    )
    description = models.TextField(blank=True, null=True)
    contributor = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="An entity responsible for making contributions to the resource.",
    )
    date = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="The date of the source, if known.",
    )
    language = models.CharField(max_length=100, null=True, blank=True)
    site = models.ForeignKey("Site", on_delete=models.CASCADE, null=True)
    archive = models.ForeignKey("Archive", on_delete=models.CASCADE, null=True)
    box = models.CharField(max_length=225, null=True, blank=True)
    folder = models.CharField(max_length=225, null=True, blank=True)
    access_rights = models.CharField(max_length=100, null=True, blank=True)
    graffiti_id = models.ForeignKey(
        "GraffitiWall",
        on_delete=models.CASCADE,
        null=True,
        verbose_name="Associated wall",
    )
    people = models.ManyToManyField("Person", through="DocumentPersonRole")
    tags = TaggableManager(blank=True)
    location = models.ForeignKey("Location", on_delete=models.CASCADE, null=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    transcription = models.TextField(null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("detail", kwargs={"ancillary_id": self.id})


# Person is a specific person who is mentioned in a primary source.
class Person(models.Model):
    id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(blank=True, max_length=255)
    middle_name_or_initial = models.CharField(blank=True, max_length=255)
    last_name = models.CharField(max_length=255, default="Unknown")
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="images/", blank=True, null=True)
    date_of_birth = models.DateField(
        blank=True, null=True, help_text="Enter the date as YYYY-MM-DD."
    )
    date_of_death = models.DateField(
        blank=True, null=True, help_text="Enter the date as YYYY-MM-DD."
    )
    tags = TaggableManager(blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("detail", kwargs={"person_id": self.id})

    class Meta:
        verbose_name = "Person"
        verbose_name_plural = "People"


class DocumentPersonRole(models.Model):
    ROLE_CHOICES = (
        ("SENDER", "Sender"),
        ("RECIPIENT", "Recipient"),
        ("GRANTEE", "Grantee"),
        ("GRANTOR", "Grantor"),
    )

    person = models.ForeignKey(Person, on_delete=models.CASCADE)
    document = models.ForeignKey(AncillarySource, on_delete=models.CASCADE)
    role = models.CharField(max_length=100, choices=ROLE_CHOICES)

    class Meta:
        indexes = [
            models.Index(fields=["person", "document", "role"]),
        ]
        verbose_name = "People"
        verbose_name_plural = "People"

    def __str__(self):
        return f"{self.person} - {self.get_role_display()} for {self.document}"


class Alias(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = "Alias"
        verbose_name_plural = "Aliases"


class Organization(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(blank=True, max_length=255)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return self.name


class Service(models.Model):
    id = models.BigAutoField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, default=None)
    military_rank = models.CharField(blank=True, max_length=255)
    military_unit = models.CharField(blank=True, max_length=255)
    military_branch = models.CharField(blank=True, max_length=255)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.person} - {self.military_rank}"


class Archive(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    location = models.ForeignKey("Location", on_delete=models.CASCADE)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("detail", kwargs={"archive_id": self.id})


# Site is a specific structure or space with multiple walls.
class Site(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    location = models.ForeignKey(
        "Location", on_delete=models.CASCADE, blank=True, null=True
    )
    image = models.ImageField(upload_to="images/", blank=True, null=True)
    tags = TaggableManager(blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("detail", kwargs={"site_id": self.id})


class Location(models.Model):
    id = models.BigAutoField(primary_key=True)
    place = models.CharField(max_length=255, verbose_name="Display name")
    address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=4,
        blank=True,
        null=True,
        help_text="If left blank, the system will attempt to geocode the information if address and state information are provided.",
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=4,
        blank=True,
        null=True,
        help_text="If left blank, the system will attempt to geocode the information if address and state information are provided.",
    )

    def save(self, *args, **kwargs):
        # Only geocode if we don’t have lat/lon and enough address info is provided
        if not self.latitude or not self.longitude:
            self.set_lat_lon_from_address()
        super().save(*args, **kwargs)

    def set_lat_lon_from_address(self):
        # Build full address string from data fields
        full_address = ", ".join(
            part for part in [self.address, self.city, self.state] if part
        )
        geolocator = Nominatim(user_agent="graffitihouse")
        try:
            location = geolocator.geocode(full_address)
            if location:
                self.latitude = location.latitude
                self.longitude = location.longitude
            else:
                raise ValidationError(f"Could not geocode address: {full_address}")
        except Exception as e:
            raise ValidationError(f"Geocoding error: {e}")

    def __str__(self) -> str:
        return self.place

    class Meta:
        ordering = ["state", "city", "place"]
        verbose_name = "Location"
        verbose_name_plural = "Locations"

import logging

logger = logging.getLogger(__name__)

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from geopy.geocoders import Nominatim
from prose.fields import RichTextField
from simple_history.models import HistoricalRecords
from taggit_selectize.managers import TaggableManager


class Location(models.Model):
    """
    The model handles georaphic locations for various models.
    """

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

    history = HistoricalRecords()

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


class Site(models.Model):
    """
    Site is a specific structure or space with multiple walls that contain graffiti.
    """

    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, blank=True, null=True
    )
    image = models.ImageField(upload_to="images/", blank=True, null=True)
    tags = TaggableManager(blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    history = HistoricalRecords()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("detail", kwargs={"site_id": self.id})


# Graffiti is a specific wall from a site.
class GraffitiWall(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = RichTextField(blank=True, null=True)
    image = models.ImageField(upload_to="images/")
    archival_image = models.ImageField(
        blank=True,
        null=True,
        upload_to="images/archival/",
        help_text="An archival quality image. Optional.",
    )
    room = models.CharField(max_length=255, help_text="Record the room name/number.")
    spatial_position = models.CharField(
        max_length=100,
        help_text="Mike's record the region code for this wall (e.g., B1, C3).",
    )
    wall_grid_position = models.CharField(
        max_length=100,
        help_text="General record for the wall grid position. For example, A1 or A1A2. Please consult the grid image reference for more information.",
    )
    identifier = models.CharField(
        max_length=100,
        help_text="Identifier refers to the number produced by the camera/phone. Please ensure these match.",
    )
    date_taken = models.DateField(help_text="Record the date the photograph was taken.")
    site_id = models.ForeignKey(Site, on_delete=models.CASCADE, verbose_name="Site")
    notes = models.TextField(blank=True, null=True, help_text="Internal project notes.")
    conservation_notes = models.TextField(
        blank=True, null=True, help_text="Conservation notes."
    )
    interpretation = models.TextField(blank=True, null=True)
    tags = TaggableManager(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

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


class GraffitiPhoto(models.Model):
    """GraffitiPhoto refers to a specific piece of graffiti on an overall wall."""

    GRAFFITI_TYPES = (
        ("name", "name"),
        ("image", "image"),
        ("unit", "unit"),
        ("other", "other"),
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
        help_text="An auto-generated unique identifier for the photo.",
    )
    is_part_of = models.ManyToManyField(
        GraffitiWall,
        blank=True,
        help_text="A related resource in which the described resource is physically or logically included.",
        related_name="graffiti_is_part_of",
    )
    tags = TaggableManager(blank=True)
    coordinates = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def image_canvas(self):
        if self.image:
            return mark_safe(
                '<img src="%s" style="width:100px; height:100px;" />' % self.image.url
            )
        else:
            return "No Image Found"

    image_canvas.short_description = "Image"

    def save(self, *args, **kwargs):
        print("Saving with coordinates:", self.coordinates)
        super().save(*args, **kwargs)

    def __str__(self):
        graffiti_type = self.graffiti_type or "No type"
        identifier = self.identifier or "No ID"
        return f"{graffiti_type} - {identifier}"

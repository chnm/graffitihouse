import io
import logging

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from geopy.geocoders import Nominatim
from PIL import Image
from prose.fields import RichTextField
from simple_history.models import HistoricalRecords
from taggit_selectize.managers import TaggableManager

logger = logging.getLogger(__name__)


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
        return reverse("graffiti:site_detail", kwargs={"site_id": self.id})


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

    def __str__(self):
        return self.name

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        editable=False,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    def get_absolute_url(self):
        return reverse("graffiti:overall_image", kwargs={"wall_id": self.id})

    def description_as_markdown(self):
        return mark_safe(self.description)


class GraffitiType(models.TextChoices):
    DRAWING = "drawing", "drawing"
    IMAGE = "image", "image"
    NAME = "name", "name"
    POETRY = "poetry", "poetry"
    UNIT = "unit", "unit"
    OTHER_WRITING = "other writing", "other writing"
    OTHER = "other", "other"


class GraffitiPhoto(models.Model):
    """GraffitiPhoto refers to a specific piece of graffiti on an overall wall."""

    id = models.BigAutoField(primary_key=True)
    graffiti_wall = models.ForeignKey(
        GraffitiWall,
        on_delete=models.CASCADE,
        verbose_name="Graffiti wall",
        help_text="Select the graffiti wall this photo belongs to.",
    )
    graffiti_type = models.CharField(
        null=True, max_length=100, choices=GraffitiType.choices
    )
    description = RichTextField(blank=True, null=True)
    image = models.ImageField(upload_to="images/derived/", null=True)
    identifier = models.CharField(
        max_length=100,
        unique=True,
        help_text="An auto-generated unique identifier for the photo.",
    )
    tags = TaggableManager(blank=True)
    # Crop rectangle in pixels of the wall's `image`.
    x = models.PositiveIntegerField(null=True, blank=True)
    y = models.PositiveIntegerField(null=True, blank=True)
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    coordinates = models.JSONField(
        null=True, blank=True, help_text="Raw metadata captured by the crop tool."
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        editable=False,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    @property
    def rectangle(self):
        if None in (self.x, self.y, self.width, self.height):
            return None
        return (self.x, self.y, self.x + self.width, self.y + self.height)

    def derive_image(self):
        """Crop this photo out of its wall image and store it in `image`.

        Uses the archival image when present, scaling the rectangle from the
        web image's dimensions, so the derived crop is as sharp as the source.
        """
        rectangle = self.rectangle
        if rectangle is None:
            return
        wall = self.graffiti_wall
        scale = 1
        if wall.archival_image:
            scale = wall.archival_image.width / wall.image.width
        # Reading `.width` above closes the file, so reopen it explicitly.
        with (
            (wall.archival_image or wall.image).open("rb") as file,
            Image.open(file) as source,
        ):
            crop = source.crop(tuple(round(edge * scale) for edge in rectangle))
            buffer = io.BytesIO()
            crop.save(buffer, format="PNG")
        self.image.save(
            f"derived_{self.identifier}.png", ContentFile(buffer.getvalue()), save=False
        )

    def __str__(self):
        graffiti_type = self.graffiti_type or "No type"
        identifier = self.identifier or "No ID"
        return f"{graffiti_type} - {identifier}"


class MultispectralImage(models.Model):
    """A multispectral capture of a wall, one image per band."""

    graffiti_wall = models.ForeignKey(
        GraffitiWall, on_delete=models.CASCADE, related_name="multispectral_images"
    )
    image = models.ImageField(upload_to="images/multispectral/")
    band = models.CharField(
        max_length=100,
        help_text="Wavelength or band captured, e.g. 'IR 850nm' or 'UV'.",
    )
    captured_on = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.graffiti_wall} - {self.band}"

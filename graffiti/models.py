import logging

logger = logging.getLogger(__name__)

from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from prose.fields import RichTextField
from taggit_selectize.managers import TaggableManager


# Graffiti is a specific wall from a house.
class GraffitiWall(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = RichTextField()
    image = models.ImageField(upload_to="images/")
    identifier = models.CharField(
        max_length=100,
        help_text="Identifier refers to the image filename. Please ensure these match.",
    )
    date = models.DateTimeField(auto_now_add=True)
    house_id = models.ForeignKey(
        "House", on_delete=models.CASCADE, verbose_name="House"
    )
    tags = TaggableManager()

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


# GraffitiPhoto is a specific piece of graffiti from an overall wall.
class GraffitiPhoto(models.Model):
    id = models.BigAutoField(primary_key=True)
    graffiti_id = models.ForeignKey(GraffitiWall, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="Name")
    image = models.ImageField(upload_to="images/", null=True)
    identifier = models.CharField(
        max_length=100, verbose_name="Identifier refers to the image filename."
    )
    # canvas image data
    canvas = models.TextField(null=True, blank=True)
    # canvas image coords
    canvas_coords = models.TextField(null=True, blank=True, default="[]")
    related_graffiti = models.ForeignKey(
        GraffitiWall,
        on_delete=models.CASCADE,
        related_name="related_graffiti",
        null=True,
    )

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
    creator = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField()
    contributor = models.CharField(max_length=100, null=True, blank=True)
    date = models.CharField(max_length=100, null=True, blank=True)
    language = models.CharField(max_length=100, null=True, blank=True)
    house = models.ForeignKey("House", on_delete=models.CASCADE, null=True)
    archive = models.ForeignKey("Archive", on_delete=models.CASCADE, null=True)
    box = models.CharField(max_length=225, null=True, blank=True)
    folder = models.CharField(max_length=225, null=True, blank=True)
    access_rights = models.CharField(max_length=100, null=True, blank=True)
    graffiti_id = models.ForeignKey("GraffitiWall", on_delete=models.CASCADE, null=True)
    tags = TaggableManager()

    # Document type specific metadata
    person = models.ManyToManyField("Person")
    sender = models.ForeignKey(
        "Person", on_delete=models.CASCADE, related_name="sender", null=True
    )
    recipient = models.ForeignKey(
        "Person", on_delete=models.CASCADE, related_name="recipient", null=True
    )
    grantor = models.ForeignKey(
        "Person", on_delete=models.CASCADE, related_name="grantor", null=True
    )
    grantee = models.ForeignKey(
        "Person", on_delete=models.CASCADE, related_name="grantee", null=True
    )
    location = models.CharField(max_length=100, null=True, blank=True)
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
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to="images/")
    date_of_birth = models.DateTimeField(auto_now_add=True)
    date_of_death = models.DateField(auto_now_add=True)
    tags = TaggableManager()

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("detail", kwargs={"person_id": self.id})


class Archive(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("detail", kwargs={"archive_id": self.id})


# House is a specific building with multiple walls.
class House(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    image = models.ImageField(upload_to="images/")
    date = models.DateTimeField(auto_now_add=True)
    tags = TaggableManager()

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("detail", kwargs={"house_id": self.id})

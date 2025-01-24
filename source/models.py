from django.db import models
from django.urls import reverse
from prose.fields import RichTextField
from taggit_selectize.managers import TaggableManager

from graffiti.models import GraffitiWall, Location, Site


class AncillarySource(models.Model):
    """
    Ancellary sources include maps, deeds, service records, letters, and other primary
    documents related to a specific image. These are connected to specific
    metadata for individual object types. These can be associated with specific
    pieces of graffiti or people.
    """

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
    archive = models.ForeignKey("Archive", on_delete=models.CASCADE, null=True)
    box = models.CharField(max_length=225, null=True, blank=True)
    folder = models.CharField(max_length=225, null=True, blank=True)
    access_rights = models.CharField(max_length=100, null=True, blank=True)
    graffiti_id = models.ForeignKey(GraffitiWall, on_delete=models.CASCADE, null=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE, null=True)

    people = models.ManyToManyField("people.Person", through="DocumentPersonRole")
    tags = TaggableManager(blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    transcription = models.TextField(null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("detail", kwargs={"ancillary_id": self.id})


class Archive(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("detail", kwargs={"archive_id": self.id})


class DocumentPersonRole(models.Model):
    ROLE_CHOICES = (
        ("SENDER", "Sender"),
        ("RECIPIENT", "Recipient"),
        ("GRANTEE", "Grantee"),
        ("GRANTOR", "Grantor"),
    )

    person = models.ForeignKey("people.Person", on_delete=models.CASCADE)
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

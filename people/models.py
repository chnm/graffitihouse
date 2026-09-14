from django.conf import settings
from django.db import models
from django.urls import reverse
from simple_history.models import HistoricalRecords
from taggit_selectize.managers import TaggableManager

from graffiti.models import GraffitiPhoto


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
    associated_graffiti_photos = models.ManyToManyField(
        GraffitiPhoto,
        blank=True,
        related_name="associated_people",
        verbose_name="Associated photos",
    )
    tags = TaggableManager(blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.last_name

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        editable=False,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    def get_absolute_url(self):
        return reverse("people:person_detail", kwargs={"person_id": self.id})

    class Meta:
        verbose_name = "Person"
        verbose_name_plural = "People"


class Alias(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, default=None)
    history = HistoricalRecords()

    def __str__(self):
        return str(self.name)

    class Meta:
        verbose_name = "Alias"
        verbose_name_plural = "Aliases"


class Organization(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(blank=True, max_length=255)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, default=None)
    history = HistoricalRecords()

    def __str__(self):
        return self.name


class Governance(models.TextChoices):
    UNION = "union", "Union"
    CONFEDERACY = "confederacy", "Confederacy"


class Branch(models.TextChoices):
    ARMY = "army", "Army"
    NAVY = "navy", "Navy"
    CAVALRY = "cavalry", "Cavalry"
    COAST_GUARD = "coastguard", "Coast Guard"


class Service(models.Model):
    id = models.BigAutoField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, default=None)
    military_rank = models.CharField(blank=True, max_length=255)
    military_unit = models.CharField(blank=True, max_length=255)
    military_branch = models.CharField(
        blank=True, max_length=255, choices=Branch.choices
    )
    military_division = models.CharField(blank=True, max_length=255)
    military_governance = models.CharField(
        blank=True, max_length=11, choices=Governance.choices
    )
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    # Bookkeeping
    history = HistoricalRecords()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.person}"

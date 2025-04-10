from django.db import models
from django.urls import reverse
from prose.fields import RichTextField
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
    associated_graffiti_photo = models.ForeignKey(
        GraffitiPhoto,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="graffiti_associated_person",
        verbose_name="Associated photo",
    )
    tags = TaggableManager(blank=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    def __str__(self):
        return self.last_name

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


class Service(models.Model):
    id = models.BigAutoField(primary_key=True)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, default=None)
    military_rank = models.CharField(blank=True, max_length=255)
    military_unit = models.CharField(blank=True, max_length=255)
    military_branch = models.CharField(blank=True, max_length=255)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.person} - {self.military_rank}"

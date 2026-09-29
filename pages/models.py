from django.db import models
from simple_history.models import HistoricalRecords


class TeamGroup(models.TextChoices):
    TEAM = "team", "Project team"
    COLLABORATOR = "collaborator", "Collaborators"


# TeamMember is a person who works on the project, listed on the Team page.
class TeamMember(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    role = models.CharField(
        max_length=255, blank=True, help_text="e.g. Senior Developer and Scholar"
    )
    group = models.CharField(
        max_length=20, choices=TeamGroup.choices, default=TeamGroup.TEAM
    )
    affiliation = models.CharField(
        max_length=255, blank=True, help_text="e.g. George Mason University"
    )
    bio = models.TextField(blank=True, help_text="A sentence or two, plain text.")
    photo = models.ImageField(upload_to="team/", blank=True)
    website = models.URLField(blank=True)
    order = models.IntegerField(
        default=0, help_text="Lower numbers are listed first within a group."
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
        help_text="Uncheck to hide this person from the public Team page.",
    )

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ["group", "order", "name"]
        verbose_name = "Team member"
        verbose_name_plural = "Team members"

    def __str__(self):
        return self.name

    @property
    def initials(self):
        words = self.name.split()
        if not words:
            return ""
        if len(words) == 1:
            return words[0][:1].upper()
        return (words[0][:1] + words[-1][:1]).upper()

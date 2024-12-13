from django.db import models

from graffiti.models import GraffitiWall


class Image(models.Model):
    related_image = models.ForeignKey(GraffitiWall, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="images/", null=True)

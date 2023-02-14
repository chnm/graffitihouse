from django.db import models
from django.urls import reverse 

class Graffiti(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='images/')
    date = models.DateTimeField(auto_now_add=True)
    house_id = models.ForeignKey('House', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('detail', kwargs={'graffiti_id': self.id})

class GraffitiHasPart(models.Model):
    graffiti_id = models.ForeignKey(Graffiti, on_delete=models.CASCADE)
    part_id = models.IntegerField()

    def __str__(self):
        return self.graffiti_id

class House(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    image = models.ImageField(upload_to='images/')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('detail', kwargs={'house_id': self.id})

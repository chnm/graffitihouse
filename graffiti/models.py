from django.db import models
from django.urls import reverse 

class Graffiti(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='images/')
    date = models.DateTimeField(auto_now_add=True)
    house_id = models.ForeignKey('House', on_delete=models.CASCADE)

    # When a user draws a selection of graffiti, a new canvas coordinate 
    # is added to the graffiti_has_part table
    def add_canvas(self, canvas):
        self.canvas = canvas
        self.save()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('detail', kwargs={'graffiti_id': self.id})

class GraffitiHasPart(models.Model):
    graffiti_id = models.ForeignKey(Graffiti, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="Name")
    part_id = models.IntegerField()
    image = models.ImageField(upload_to='images/', null=True)
    # Canvas coordinates for the graffiti selection
    canvas = models.TextField(default="0,0,0,0")

    def __str__(self):
        return self.name

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


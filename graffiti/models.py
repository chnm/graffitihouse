from django.db import models
from django.urls import reverse 

# Graffiti is a specific wall from a house.
class Graffiti(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='images/')
    date = models.DateTimeField(auto_now_add=True)
    house_id = models.ForeignKey('House', on_delete=models.CASCADE)
    tags = models.ManyToManyField('Tag')

    # When a user draws a selection of graffiti, a new canvas coordinate 
    # is added to the graffiti_has_part table
    def add_canvas(self, canvas):
        self.canvas = canvas
        self.save()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('detail', kwargs={'graffiti_id': self.id})

# GraffitiHasPart is a specific piece of graffiti from an overall wall.
class GraffitiHasPart(models.Model):
    id = models.AutoField(primary_key=True)
    graffiti_id = models.ForeignKey(Graffiti, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="Name")
    image = models.ImageField(upload_to='images/', null=True)
    # Canvas coordinates for the graffiti selection
    canvas = models.TextField(default="0,0,0,0")
    related_graffiti = models.ForeignKey(Graffiti, on_delete=models.CASCADE, related_name='related_graffiti', null=True)

    def __str__(self):
        return self.name

# Ancellary sources include maps, deeds, service records, letters, and other primary
# documents related to a specific image. These are connected to specific 
# metadata for individual object types.
class AncillarySource(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    tags = models.ManyToManyField('Tag')
    archive = models.ForeignKey('Archive', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='sources/')
    access_rights = models.CharField(max_length=100)
    graffiti_id = models.ForeignKey(Graffiti, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('detail', kwargs={'ancillary_id': self.id})

class MetadataForLetters(models.Model):
    id = models.AutoField(primary_key=True)
    ancillary_id = models.ForeignKey(AncillarySource, on_delete=models.CASCADE)
    date = models.CharField(max_length=100)
    sender = models.ForeignKey('Person', on_delete=models.CASCADE)
    recipient = models.ForeignKey('Person', on_delete=models.CASCADE, related_name='recipient')
    location = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    description = models.TextField()
    summary = models.TextField()
    transcription = models.TextField()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('detail', kwargs={'ancillary_id': self.id})

class MetadataForDeeds(models.Model):
    id = models.AutoField(primary_key=True)
    ancillary_id = models.ForeignKey(AncillarySource, on_delete=models.CASCADE)
    date = models.CharField(max_length=100)
    grantor = models.ForeignKey('Person', on_delete=models.CASCADE)
    grantee = models.ForeignKey('Person', on_delete=models.CASCADE, related_name='grantee')
    location = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    description = models.TextField()
    summary = models.TextField()
    transcription = models.TextField()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('detail', kwargs={'ancillary_id': self.id})

class MetadataForMaps(models.Model):
    id = models.AutoField(primary_key=True)
    ancillary_id = models.ForeignKey(AncillarySource, on_delete=models.CASCADE)
    date = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    description = models.TextField()
    summary = models.TextField()
    transcription = models.TextField()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('detail', kwargs={'ancillary_id': self.id})
    
class MetadataForServiceRecords(models.Model):
    id = models.AutoField(primary_key=True)
    ancillary_id = models.ForeignKey(AncillarySource, on_delete=models.CASCADE)
    date = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    description = models.TextField()
    summary = models.TextField()
    transcription = models.TextField()
    person = models.ForeignKey('Person', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('detail', kwargs={'ancillary_id': self.id})

class MetadataForOther(models.Model):
    id = models.AutoField(primary_key=True)
    ancillary_id = models.ForeignKey(AncillarySource, on_delete=models.CASCADE)
    date = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    description = models.TextField()
    summary = models.TextField()
    transcription = models.TextField()
    people = models.ManyToManyField('Person')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('detail', kwargs={'ancillary_id': self.id})

# Person is a specific person who is mentioned in a primary source.
class Person(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='images/')
    date_of_birth = models.DateTimeField(auto_now_add=True)
    date_of_death = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('detail', kwargs={'person_id': self.id})

class Archive(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100)
    box = models.CharField(max_length=255, default = '')
    folder = models.CharField(max_length=255, default = '')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('detail', kwargs={'archive_id': self.id})

# House is a specific building with multiple walls.
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

# Tags are used to categorize graffiti.
class Tag(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tags_detail', kwargs={'pk': self.id})
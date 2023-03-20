import logging
logger = logging.getLogger(__name__)

import xml.sax.saxutils as saxutils
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils.safestring import mark_safe
from django.db import models
from django.urls import reverse

class AbstractDublinCore(models.Model):
    '''Abstract class for Dublin Core metadata.
    '''
    class Meta:
        abstract = True
        ordering = ['term',]

    DCTERMS = (\
                ('AB', 'Abstract'),
                ('AR', 'AccessRights'),
                ('AM', 'AccrualMethod'),
                ('AP', 'AccrualPeriodicity'),
                ('APL', 'AccrualPolicy'),
                ('ALT', 'Alternative'),
                ('AUD', 'Audience'),
                ('AVL', 'Available'),
                ('BIB', 'BibliographicCitation'),
                ('COT', 'ConformsTo'),
                ('CN', 'Contributor'),
                ('CVR', 'Coverage'),
                ('CRD', 'Created'),
                ('CR', 'Creator'),
                ('DT', 'Date'),
                ('DTA', 'DateAccepted'),
                ('DTC', 'DateCopyrighted'),
                ('DTS', 'DateSubmitted'),
                ('DSC', 'Description'),
                ('EL', 'EducationLevel'),
                ('EXT', 'Extent'),
                ('FMT', 'Format'),
                ('HFMT', 'HasFormat'),
                ('HPT', 'HasPart'),
                ('HVS', 'HasVersion'),
                ('ID', 'Identifier'),
                ('IM', 'InstructionalMethod'),
                ('IFMT', 'IsFormatOf'),
                ('IPT', 'IsPartOf'),
                ('IREF', 'IsReferencedBy'),
                ('IREP', 'IsReplacedBy'),
                ('IREQ', 'IsRequiredBy'),
                ('IS', 'Issued'),
                ('IVSN', 'IsVersionOf'),
                ('LG', 'Language'),
                ('LI', 'License'),
                ('ME', 'Mediator'),
                ('MED', 'Medium'),
                ('MOD', 'Modified'),
                ('PRV', 'Provenance'),
                ('PBL', 'Publisher'),
                ('REF', 'References'),
                ('REL', 'Relation'),
                ('REP', 'Replaces'),
                ('REQ', 'Requires'),
                ('RT', 'Rights'),
                ('RH', 'RightsHolder'),
                ('SRC', 'Source'),
                ('SP', 'Spatial'),
                ('SUB', 'Subject'),
                ('TOC', 'TableOfContents'),
                ('TE', 'Temporal'),
                ('T', 'Title'),
                ('TYP', 'Type'),
                ('VA', 'Valid'),
    )
    DCTERM_MAP = dict([(x[1].lower(), x[0]) for x in DCTERMS])
    DCTERM_CODE_MAP = dict([(x[0], x[1].lower()) for x in DCTERMS])
    DCTERM_LIST = [x[1].lower() for x in DCTERMS]

    object_id = models.CharField(max_length=255)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    # Don't want this constraint here. The history terms can't be related directly
    #content_object = generic.GenericForeignKey('content_type', 'object_id')
    term = models.CharField(max_length=4, choices=DCTERMS)
    qualifier = models.CharField(max_length=40, null=True, blank=True)
    content = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return ''.join([self.get_term_display(), ':', self.qualifier, ' = ', self.content[0:50], '...' if len(self.content)>50 else '' ]) if self.qualifier else ''.join([self.get_term_display(), ' = ', self.content[0:50], '...' if len(self.content) > 50 else '' ])

    def DCELEMENTS(DCTERMS=DCTERMS):
        element_codes = ('T', 'CR', 'SUB', 'DSC', 'PBL', 'CN', 'DT', 'TYP', 'FMT', 'ID', 'SRC', 'LG', 'REL', 'CVR', 'RT', )
        dce_ordered = []
        for code in element_codes:
            for ttuple in DCTERMS:
                if ttuple[0] == code:
                    dce_ordered.append(ttuple)
        return tuple(dce_ordered)
    DCELEMENTS = DCELEMENTS()
    DCELEMENT_MAP = dict([(x[1].lower(), x[0]) for x in DCELEMENTS])
    DCELEMENT_CODE_MAP = dict([(x[0], x[1].lower()) for x in DCELEMENTS])
    DCELEMENT_LIST = [x[1].lower() for x in DCELEMENTS]

    @property
    def qdc(self):
        '''Return the qdc tag for the term
        '''
        start_tag = ''.join(('<', self.get_term_display().lower(), ' q="',
            self.qualifier, '">',)) if self.qualifier else ''.join(('<', self.get_term_display().lower(), '>', ))
        qdc = ''.join((start_tag, saxutils.escape(self.content), '</', self.get_term_display().lower(), '>',))
        return mark_safe(qdc)

    @property
    def objset_data(self):
        if not self.qualifier:
            return unicode(self.content)
        else:
            return dict(q=unicode(self.qualifier), v=unicode(self.content))

# Graffiti is a specific wall from a house.
class GraffitiWall(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='images/')
    identifier = models.CharField(max_length=100, verbose_name="Identifier refers to the image filename.")
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
class GraffitiPhoto(models.Model):
    id = models.BigAutoField(primary_key=True)
    graffiti_id = models.ForeignKey(GraffitiWall, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="Name")
    image = models.ImageField(upload_to='images/', null=True)
    identifier = models.CharField(max_length=100, verbose_name="Identifier refers to the image filename.")
    # Canvas coordinates for the graffiti selection
    canvas = models.TextField(default="0,0,0,0")
    related_graffiti = models.ForeignKey(GraffitiWall, on_delete=models.CASCADE, related_name='related_graffiti', null=True)

    def __str__(self):
        return self.name

# Ancellary sources include maps, deeds, service records, letters, and other primary
# documents related to a specific image. These are connected to specific 
# metadata for individual object types. These can be associated with specific 
# pieces of graffiti or people.
class AncillarySource(models.Model):

    DOCUMENT_TYPES = (
        ('image', 'Image'),
        ('newsprint', 'Newsprint'),
        ('wall', 'Wall'),
        ('letter', 'Letter'),
        ('photograph', 'Photograph'),
        ('drawing', 'Drawing'),
        ('artwork', 'Artwork'),
        ('game', 'Game'),
        ('poem', 'Poem'),
        ('other', 'Other'),
    )

    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=100)
    item_type = models.CharField(max_length=100, choices=DOCUMENT_TYPES)
    creator = models.CharField(max_length=100)
    description = models.TextField()
    contributor = models.CharField(max_length=100, null=True, blank=True)
    date = models.CharField(max_length=100, null=True, blank=True)
    language = models.CharField(max_length=100)
    house = models.ForeignKey('House', on_delete=models.CASCADE, null=True)
    archive = models.ForeignKey('Archive', on_delete=models.CASCADE, null=True)
    box = models.CharField(max_length = 225, null=True)
    folder = models.CharField(max_length = 225, null=True)
    access_rights = models.CharField(max_length=100)
    graffiti_id = models.ForeignKey('GraffitiWall', on_delete=models.CASCADE, null=True)
    tags = models.ManyToManyField('Tag')

    # Document type specific metadata
    person = models.ManyToManyField('Person')
    sender = models.ForeignKey('Person', on_delete=models.CASCADE, related_name='sender', null=True)
    recipient = models.ForeignKey('Person', on_delete=models.CASCADE, related_name='recipient', null=True)
    grantor = models.ForeignKey('Person', on_delete=models.CASCADE, related_name='grantor', null=True)
    grantee = models.ForeignKey('Person', on_delete=models.CASCADE, related_name='grantee', null=True)
    location = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    transcription = models.TextField()

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('detail', kwargs={'ancillary_id': self.id})

# Person is a specific person who is mentioned in a primary source.
class Person(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='images/')
    date_of_birth = models.DateTimeField(auto_now_add=True)
    date_of_death = models.DateField(auto_now_add=True)
    tags = models.ManyToManyField('Tag')

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('detail', kwargs={'person_id': self.id})


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
        return reverse('detail', kwargs={'archive_id': self.id})


# House is a specific building with multiple walls.
class House(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100)
    latitude = models.FloatField()
    longitude = models.FloatField()
    image = models.ImageField(upload_to='images/')
    date = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField('Tag')

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('detail', kwargs={'house_id': self.id})

# Tags are used to categorize graffiti.
class Tag(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=100)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tags_detail', kwargs={'pk': self.id})
from django.contrib import admin
from .models import Graffiti, GraffitiHasPart, House, Person, AncillarySource, MetadataForDeed, MetadataForLetter, MetadataForMap, MetadataForOther, MetadataForServiceRecord, Tag, Archive

# Register your models here.
admin.site.register(Graffiti)
admin.site.register(GraffitiHasPart)
admin.site.register(House)
admin.site.register(Person)
admin.site.register(AncillarySource)
admin.site.register(MetadataForDeed)
admin.site.register(MetadataForLetter)
admin.site.register(MetadataForMap)
admin.site.register(MetadataForOther)
admin.site.register(MetadataForServiceRecord)
admin.site.register(Tag)
admin.site.register(Archive)
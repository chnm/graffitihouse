from django.contrib import admin
from .models import Graffiti, GraffitiHasPart, House

# Register your models here.
admin.site.register(Graffiti)
admin.site.register(GraffitiHasPart)
admin.site.register(House)
from django.contrib import admin
from django.contrib.admin.widgets import AdminFileWidget
from django.db import models
from django.utils.html import format_html

from .models import (
    AncillarySource,
    Archive,
    GraffitiPhoto,
    GraffitiWall,
    House,
    Person,
    Tag,
)

admin.site.register(GraffitiPhoto)
admin.site.register(House)
admin.site.register(Person)
admin.site.register(Tag)
admin.site.register(Archive)
admin.site.register(AncillarySource)


class CustomAdminFileWidget(AdminFileWidget):
    def render(self, name, value, attrs=None, renderer=None):
        result = []
        if hasattr(value, "url"):
            result.append(
                f"""<a href="{value.url}" target="_blank">
                      <img 
                        src="{value.url}" alt="{value}" 
                        width="100" height="100"
                        style="object-fit: cover;"
                      />
                    </a>"""
            )
        result.append(super().render(name, value, attrs, renderer))
        return format_html("".join(result))


class GraffitiWallAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "description_as_markdown",
        "image_canvas",
    )

    formfield_overrides = {models.ImageField: {"widget": CustomAdminFileWidget}}


admin.site.register(GraffitiWall, GraffitiWallAdmin)

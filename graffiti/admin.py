from django.contrib import admin
from django.contrib.admin.widgets import AdminFileWidget
from django.db import models
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin

from .models import AncillarySource, Archive, GraffitiPhoto, GraffitiWall, House, Person

admin.site.register(Archive)


class CustomAdminFileWidget(AdminFileWidget):
    def render(self, name, value, attrs=None, renderer=None):
        result = []
        if hasattr(value, "url"):
            result.append(
                f"""<a href="{value.url}" target="_blank">
                      <img 
                        src="{value.url}" alt="{value}" 
                        width="500" height="500"
                        style="object-fit: cover;"
                      />
                    </a>"""
            )
        result.append(super().render(name, value, attrs, renderer))
        return format_html("".join(result))


class GraffitiWallAdmin(ImportExportModelAdmin):
    list_display = (
        "name",
        "description_as_markdown",
        "image_canvas",
    )

    formfield_overrides = {models.ImageField: {"widget": CustomAdminFileWidget}}


admin.site.register(GraffitiWall, GraffitiWallAdmin)


class GraffitiPhotoAdmin(ImportExportModelAdmin):
    list_display = ("name",)


admin.site.register(GraffitiPhoto, GraffitiPhotoAdmin)


class AncillarySourceAdmin(ImportExportModelAdmin):
    list_display = ("title", "date")


admin.site.register(AncillarySource, AncillarySourceAdmin)


class HouseAdmin(ImportExportModelAdmin):
    list_display = ("name", "description")


admin.site.register(House, HouseAdmin)


class PersonAdmin(ImportExportModelAdmin):
    list_display = ("name",)


admin.site.register(Person, PersonAdmin)

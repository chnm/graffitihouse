from django.contrib import admin
from django.contrib.admin.widgets import AdminFileWidget
from django.db import models
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin

from .models import (
    Alias,
    AncillarySource,
    Archive,
    DocumentPersonRole,
    GraffitiPhoto,
    GraffitiWall,
    Location,
    Person,
    Site,
    WallRecordHistory,
)

admin.site.register(Archive)


class GraffitiWallHistoryInline(admin.TabularInline):
    model = WallRecordHistory
    readonly_fields = ("action", "data", "created_at", "user")
    extra = 0
    can_delete = False

    def has_add_permission(self, request, obj):
        return False


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


@admin.register(GraffitiWall)
class GraffitiWallAdmin(ImportExportModelAdmin):
    list_display = (
        "name",
        "description_as_markdown",
        "image_canvas",
        "created_at",
    )
    formfield_overrides = {models.ImageField: {"widget": CustomAdminFileWidget}}
    inlines = [GraffitiWallHistoryInline]
    actions = ["rollback_to_previous"]

    def rollback_to_previous(self, request, queryset):
        for photo_record in queryset:
            previous_version = photo_record.history.order_by("-id")[1]
            photo_record.rollback(previous_version.id)
        self.message_user(
            request, "Selected records rolled back to their previous versions"
        )

    rollback_to_previous.short_description = "Rollback to previous versions."


@admin.register(WallRecordHistory)
class WallRecordHistoryAdmin(admin.ModelAdmin):
    list_display = ("photo_record", "action", "created_at", "user")
    list_filter = ("action", "created_at", "user")
    readonly_fields = ("photo_record", "action", "created_at", "user")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, rquest, obj=None):
        return False


class GraffitiPhotoAdmin(ImportExportModelAdmin):
    list_display = ("name",)
    readonly_fields = ("canvas", "canvas_coords")


admin.site.register(GraffitiPhoto, GraffitiPhotoAdmin)


class SourcePersonRoleInline(admin.TabularInline):
    model = DocumentPersonRole
    extra = 1


class AncillarySourceAdmin(ImportExportModelAdmin):
    list_display = ("title", "date")
    inlines = [SourcePersonRoleInline]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "image",
                    "item_type",
                    "creator",
                    "description",
                    "contributor",
                    "date",
                    "language",
                    "tags",
                )
            },
        ),
        ("Archive", {"fields": ("archive", "box", "folder", "access_rights")}),
        (
            "Site",
            {
                "fields": (
                    "site",
                    "graffiti_id",
                )
            },
        ),
        # ("Associations", {"fields": ("graffiti_id" "tags")}),
    )


admin.site.register(AncillarySource, AncillarySourceAdmin)


class SiteAdmin(ImportExportModelAdmin):
    list_display = ("name", "description")


admin.site.register(Site, SiteAdmin)


class AliasInline(admin.TabularInline):
    model = Alias
    extra = 1


class PersonAdmin(ImportExportModelAdmin):
    list_display = ("name",)
    inlines = [AliasInline]


admin.site.register(Person, PersonAdmin)


class LocationAdmin(ImportExportModelAdmin):
    list_display = ("place", "state")


admin.site.register(Location, LocationAdmin)

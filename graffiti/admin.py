import base64
import json
import os
from io import BytesIO

from django.contrib import admin
from django.contrib.admin.widgets import AdminFileWidget
from django.core.files.base import ContentFile
from django.db import models
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.response import TemplateResponse
from django.urls import path
from django.utils.html import format_html
from django.views.decorators.csrf import csrf_exempt
from import_export.admin import ImportExportModelAdmin
from PIL import Image

from .models import (
    Alias,
    AncillarySource,
    Archive,
    DocumentPersonRole,
    GraffitiPhoto,
    GraffitiWall,
    Location,
    Organization,
    Person,
    Service,
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
        "description_as_markdown",
        "get_derive_button",
        "created_at",
    )
    formfield_overrides = {models.ImageField: {"widget": CustomAdminFileWidget}}
    inlines = [GraffitiWallHistoryInline]
    actions = ["rollback_to_previous"]

    def get_derive_button(self, obj):
        return format_html(
            '<a class="button" href="{}derive/" '
            'style="background: #79aec8; color: white; padding: 5px 10px; '
            'border-radius: 4px; text-decoration: none;">'
            "Derive Photo</a>",
            f"{obj.pk}/",
        )

    get_derive_button.short_description = "Actions"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "<int:wall_id>/derive/",
                self.admin_site.admin_view(self.derive_graffiti_view),
                name="derive-graffiti",
            ),
            path(
                "save-derived/",
                self.admin_site.admin_view(self.save_derived_graffiti),
                name="save-derived-graffiti",
            ),
        ]
        return custom_urls + urls

    def derive_graffiti_view(self, request, wall_id):
        graffiti_wall = get_object_or_404(GraffitiWall, id=wall_id)
        context = {
            "graffiti_wall": graffiti_wall,
            "is_popup": "_popup" in request.GET,
            "opts": self.model._meta,
            "graffiti_types": GraffitiPhoto.GRAFFITI_TYPES,
            "wall_image_url": graffiti_wall.image.url,
        }
        return TemplateResponse(
            request,
            "admin/image_crop.html",
            context,
        )

    @csrf_exempt
    def save_derived_graffiti(self, request):
        if request.method == "POST":
            data = json.loads(request.body)
            image_data = data["image"].split(",")[1]
            wall_id = data["wall_id"]
            graffiti_wall = GraffitiWall.objects.get(id=wall_id)

            # Create the GraffitiPhoto instance
            graffiti_photo = GraffitiPhoto(
                graffiti_wall=graffiti_wall,
                graffiti_type=data.get("graffiti_type"),
                description=data.get("description", ""),
                identifier=data.get("identifier", ""),
                coordinates=data["coordinates"],
                canvas=data.get("canvas", ""),
                canvas_coords=json.dumps(data["coordinates"]),
            )

            # Handle the cropped image
            image_data = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_data))
            output = BytesIO()
            image.save(output, format="PNG")

            graffiti_photo.image.save(
                f'derived_{wall_id}_{data.get("identifier", "unnamed")}.png',
                BytesIO(output.getvalue()),
                save=False,
            )
            graffiti_photo.save()

            # Handle relationships
            if data.get("is_part_of"):
                graffiti_photo.is_part_of.add(graffiti_wall)

            # Handle tags if provided
            if data.get("tags"):
                graffiti_photo.tags.add(*data["tags"].split(","))

            return JsonResponse(
                {
                    "success": True,
                    "id": graffiti_photo.id,
                    "message": "Graffiti photo saved successfully",
                }
            )
        return JsonResponse({"success": False}, status=400)

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

    def has_change_permission(self, request, obj=None):
        return False


class GraffitiPhotoAdmin(ImportExportModelAdmin):
    list_display = ("graffiti_type",)
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
    )


admin.site.register(AncillarySource, AncillarySourceAdmin)


class SiteAdmin(ImportExportModelAdmin):
    list_display = ("name", "description")


admin.site.register(Site, SiteAdmin)


class AliasInline(admin.StackedInline):
    model = Alias
    extra = 1


class ServiceInline(admin.TabularInline):
    model = Service
    extra = 1


class OrganizationInline(admin.StackedInline):
    model = Organization
    extra = 1


class PersonAdmin(ImportExportModelAdmin):
    list_display = (
        "last_name",
        "first_name",
    )
    inlines = [AliasInline, ServiceInline, OrganizationInline]


admin.site.register(Person, PersonAdmin)


class LocationAdmin(ImportExportModelAdmin):
    list_display = ("place", "state")


admin.site.register(Location, LocationAdmin)

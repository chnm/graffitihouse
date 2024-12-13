import base64
import json
import os
import traceback
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

from graffiti.models import (
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
        "name",
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

    # In your admin.py derive_graffiti_view
    def derive_graffiti_view(self, request, wall_id):
        graffiti_wall = get_object_or_404(GraffitiWall, id=wall_id)
        derived_photos = GraffitiPhoto.objects.filter(graffiti_wall=graffiti_wall)

        # Prepare a simpler data structure
        derived_data = []
        for photo in derived_photos:
            if photo.coordinates and "canvas" in photo.coordinates:
                derived_data.append(
                    {"identifier": photo.identifier, "coords": photo.coordinates}
                )

        context = {
            "graffiti_wall": graffiti_wall,
            "is_popup": "_popup" in request.GET,
            "opts": self.model._meta,
            "graffiti_types": GraffitiPhoto.GRAFFITI_TYPES,
            "wall_image_url": graffiti_wall.image.url,
            "derived_photos": json.dumps(derived_data),  # Pass to template as JSON
        }
        return TemplateResponse(request, "admin/image_crop.html", context)

    @csrf_exempt
    def save_derived_graffiti(self, request):
        try:
            data = json.loads(request.body)

            # Log the received metadata
            print("Received metadata:", json.dumps(data["metadata"], indent=2))

            # Extract base64 image data
            image_data = data["image"].split(",")[1]
            image_binary = base64.b64decode(image_data)

            # Create new GraffitiPhoto instance
            graffiti_photo = GraffitiPhoto(
                # Get wall_id from the nested structure
                graffiti_wall_id=data["metadata"]["coordinates"]["metadata"]["wall_id"],
                identifier=data["metadata"]["coordinates"]["metadata"]["identifier"],
                graffiti_type=data["metadata"]["coordinates"]["metadata"][
                    "graffiti_type"
                ],
                description=data["metadata"]["coordinates"]["metadata"]["description"],
                coordinates=data["metadata"][
                    "coordinates"
                ],  # Store all coordinates metadata
            )

            # Save the image
            image_name = f"derived_{graffiti_photo.identifier}.png"
            graffiti_photo.image.save(image_name, ContentFile(image_binary), save=False)

            # Save the instance first to get primary key
            graffiti_photo.save()

            # Now that we have a primary key, we can add tags
            if data["metadata"]["coordinates"]["metadata"].get("tags"):
                graffiti_photo.tags.add(
                    *data["metadata"]["coordinates"]["metadata"]["tags"]
                )

            # Handle is_part_of relationship
            if data["metadata"]["coordinates"]["metadata"].get("is_part_of"):
                graffiti_photo.is_part_of.add(
                    data["metadata"]["coordinates"]["metadata"]["wall_id"]
                )

            return JsonResponse({"success": True, "photo_id": graffiti_photo.id})

        except KeyError as e:
            print("KeyError accessing metadata:", str(e))
            print("Received data structure:", data)
            return JsonResponse(
                {
                    "success": False,
                    "error": "Missing required metadata field",
                    "details": str(e),
                },
                status=400,
            )

        except Exception as e:
            print("Error saving graffiti photo:", str(e))
            print("Traceback:", traceback.format_exc())
            return JsonResponse(
                {"success": False, "error": "Server error", "details": str(e)},
                status=500,
            )

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


class GraffitiPhotoInline(admin.TabularInline):
    model = Person
    extra = 1


class GraffitiPhotoAdmin(ImportExportModelAdmin):
    list_display = ("graffiti_type", "description", "get_associated_wall")
    readonly_fields = ("coordinates",)
    inlines = [GraffitiPhotoInline]

    def get_associated_wall(self, obj):
        # build hyperlink to the wall using its obj id
        return format_html(
            f'<a style="text-decoration: underline;" href="/admin/graffiti/graffitiwall/{obj.graffiti_wall.id}/change/">{obj.graffiti_wall.name}</a>'
        )


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


class ServiceInline(admin.StackedInline):
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

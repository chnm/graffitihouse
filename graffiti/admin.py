import json
import logging

from django.contrib import admin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import path, reverse
from django.utils.html import format_html
from django.views.generic import TemplateView
from import_export.admin import ImportExportMixin
from simple_history.admin import SimpleHistoryAdmin
from unfold.admin import ModelAdmin, StackedInline, TabularInline
from unfold.contrib.import_export.forms import ExportForm, ImportForm
from unfold.views import UnfoldModelAdminViewMixin

from graffiti.models import (
    GraffitiPhoto,
    GraffitiType,
    GraffitiWall,
    Location,
    MultispectralImage,
    Site,
)
from people.models import Alias, Organization, Person, Service
from source.models import AncillarySource, Archive, DocumentPersonRole

logger = logging.getLogger(__name__)


class HistoryImportExportAdmin(ImportExportMixin, SimpleHistoryAdmin, ModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm


class OwnedAdminMixin:
    """Record who created a row, and let creators delete their own rows.

    Users without the model-level delete permission (e.g. Students) may still
    delete rows they created themselves.
    """

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        if super().has_delete_permission(request, obj):
            return True
        return (
            obj is not None
            and obj.created_by_id == request.user.id
            and self.has_change_permission(request, obj)
        )


@admin.register(Archive)
class ArchiveAdmin(ModelAdmin):
    pass


class DeriveGraffitiView(UnfoldModelAdminViewMixin, TemplateView):
    title = "Derive graffiti photo"
    permission_required = ("graffiti.add_graffitiphoto",)
    template_name = "admin/image_crop.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        graffiti_wall = get_object_or_404(GraffitiWall, id=self.kwargs["wall_id"])
        derived_data = [
            {"identifier": photo.identifier, "coords": photo.coordinates}
            for photo in graffiti_wall.graffitiphoto_set.exclude(x=None)
        ]
        context.update(
            {
                "graffiti_wall": graffiti_wall,
                "opts": self.model_admin.model._meta,
                "graffiti_types": GraffitiType.choices,
                "wall_image_url": graffiti_wall.image.url,
                "derived_photos": json.dumps(derived_data),
            }
        )
        return context


class MultispectralImageInline(TabularInline):
    model = MultispectralImage
    extra = 0


@admin.register(MultispectralImage)
class MultispectralImageAdmin(HistoryImportExportAdmin):
    list_display = ("graffiti_wall", "band", "captured_on")
    list_filter = ("band",)
    autocomplete_fields = ("graffiti_wall",)


@admin.register(GraffitiWall)
class GraffitiWallAdmin(OwnedAdminMixin, HistoryImportExportAdmin):
    search_fields = ("name", "identifier")
    inlines = [MultispectralImageInline]
    list_display = (
        "name",
        "description_as_markdown",
        "get_derive_button",
        "created_at",
    )

    def get_derive_button(self, obj):
        return format_html(
            '<a class="text-primary-600 dark:text-primary-500" href="{}">'
            "Derive photo</a>",
            reverse("admin:derive-graffiti", args=[obj.pk]),
        )

    get_derive_button.short_description = "Actions"

    def get_urls(self):
        urls = super().get_urls()
        derive_view = self.admin_site.admin_view(
            DeriveGraffitiView.as_view(model_admin=self)
        )
        custom_urls = [
            path(
                "<int:wall_id>/derive/",
                derive_view,
                name="derive-graffiti",
            ),
            path(
                "save-derived/",
                self.admin_site.admin_view(self.save_derived_graffiti),
                name="save-derived-graffiti",
            ),
        ]
        return custom_urls + urls

    def save_derived_graffiti(self, request):
        try:
            coordinates = json.loads(request.body)["metadata"]["coordinates"]
            metadata = coordinates["metadata"]
            rectangle = coordinates["canvas"]
            graffiti_photo = GraffitiPhoto(
                graffiti_wall_id=metadata["wall_id"],
                identifier=metadata["identifier"],
                graffiti_type=metadata["graffiti_type"],
                description=metadata["description"],
                x=rectangle["x"],
                y=rectangle["y"],
                width=rectangle["width"],
                height=rectangle["height"],
                coordinates=coordinates,
                created_by=request.user,
            )
            graffiti_photo.derive_image()
            graffiti_photo.save()
            graffiti_photo.tags.add(*metadata.get("tags", []))
            return JsonResponse({"success": True, "photo_id": graffiti_photo.id})
        except KeyError as e:
            logger.warning("Derived photo payload missing %s", e)
            return JsonResponse(
                {
                    "success": False,
                    "error": "Missing required metadata field",
                    "details": str(e),
                },
                status=400,
            )
        except Exception as e:
            logger.exception("Error saving derived graffiti photo")
            return JsonResponse(
                {"success": False, "error": "Server error", "details": str(e)},
                status=500,
            )

    # Add history view
    history_list_display = ["changed_fields"]


class GraffitiPhotoAdmin(OwnedAdminMixin, HistoryImportExportAdmin):
    list_display = ("graffiti_type", "identifier", "description", "get_associated_wall")
    search_fields = ("identifier",)
    readonly_fields = ("coordinates",)

    def get_associated_wall(self, obj):
        return format_html(
            '<a style="text-decoration: underline;" href="{}">{}</a>',
            reverse(
                "admin:graffiti_graffitiwall_change",
                args=[obj.graffiti_wall_id],
            ),
            obj.graffiti_wall.name,
        )

    # Add history view
    history_list_display = ["changed_fields"]


admin.site.register(GraffitiPhoto, GraffitiPhotoAdmin)


class SourcePersonRoleInline(TabularInline):
    model = DocumentPersonRole
    extra = 1


class AncillarySourceAdmin(OwnedAdminMixin, HistoryImportExportAdmin):
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

    # Add history view
    history_list_display = ["changed_fields"]


admin.site.register(AncillarySource, AncillarySourceAdmin)


class SiteAdmin(HistoryImportExportAdmin):
    list_display = ("name", "description")

    # Add history view
    history_list_display = ["changed_fields"]


admin.site.register(Site, SiteAdmin)


class AliasInline(StackedInline):
    model = Alias
    extra = 1


class ServiceInline(StackedInline):
    model = Service
    extra = 1


class OrganizationInline(StackedInline):
    model = Organization
    extra = 1


class PersonAdmin(OwnedAdminMixin, HistoryImportExportAdmin):
    list_display = (
        "last_name",
        "first_name",
    )
    inlines = [AliasInline, ServiceInline]
    autocomplete_fields = ("associated_graffiti_photos",)


admin.site.register(Person, PersonAdmin)


class LocationAdmin(ImportExportMixin, ModelAdmin):
    import_form_class = ImportForm
    export_form_class = ExportForm
    list_display = ("place", "state")


admin.site.register(Location, LocationAdmin)

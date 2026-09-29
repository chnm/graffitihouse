from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from unfold.admin import ModelAdmin

from pages.models import TeamMember


@admin.register(TeamMember)
class TeamMemberAdmin(SimpleHistoryAdmin, ModelAdmin):
    list_display = ("name", "role", "group", "order", "is_active")
    list_editable = ("order", "is_active")
    list_filter = ("group", "is_active")
    search_fields = ("name", "role")
    fields = (
        "name",
        "role",
        "group",
        "affiliation",
        "bio",
        "photo",
        "website",
        "order",
        "is_active",
    )

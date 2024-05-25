from django.contrib import admin
from import_export.admin import ImportExportMixin

from admin_dashboard.models import Stat


@admin.register(Stat)
class StatAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = (
        "metrics",
        "created_at",
        "updated_at",
        "id",
        )
    search_fields = (
        "created_at",
        "updated_at",
        "id",
        )
    ordering = ("-created_at",)

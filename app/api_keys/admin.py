from django.contrib import admin
from import_export.admin import ImportExportMixin

from api_keys.models import APIKey


@admin.register(APIKey)
class APIKeyAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = (
        "api_key",
        "user",
        "attempts",
        "usage_times_web",
        "premium_limit",
        "usage_free_times_daily",
        "usage_free_times_total",
        "country_flag",
        "user_country",
        "is_blocked",
        "created_at",
        "updated_at",
        "id",
        )
    search_fields = (
        "api_key",
        "user__email",
        "attempts",
        "usage_times_web",
        "is_blocked",
        "premium_limit",
        "created_at",
        "updated_at",
        "id",
        )
    ordering = ("-created_at",)

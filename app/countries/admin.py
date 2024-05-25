from django.contrib import admin
from import_export.admin import ImportExportMixin

from countries.models import CountryExt


# Register your models here.
@admin.register(CountryExt)
class CountryAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = (
        "country",
        "is_priority",
        "denonym",
        "is_porn_legal",
        "created_at",
        "updated_at",
        "id",
        )
    search_fields = (
        "country",
        "is_priority",
        "denonym",
        "is_porn_legal",
        "created_at",
        "updated_at",
        "id",
        )
    ordering = ("-created_at",)

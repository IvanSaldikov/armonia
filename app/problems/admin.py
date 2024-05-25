from django.contrib import admin
from import_export.admin import ImportExportMixin

from problems.models import Problem


@admin.register(Problem)
class ProblemAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = (
        "problem_type",
        "is_public",
        "user_age",
        "therapist_name",
        "therapist_gender",
        "country_flag",
        "author",
        "problem_description",
        "created_at",
        "updated_at",
        "id",
        )
    search_fields = (
        "slug",
        "created_at",
        "updated_at",
        "id",
        )
    ordering = ("-created_at",)
    prepopulated_fields = {"slug": ("therapist_name",)}
    list_filter = ("therapist_country",
                   "is_public",
                   "is_active",
                   "is_solved",
                   )

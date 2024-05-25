from django.contrib import admin
from import_export.admin import ImportExportMixin

from emails.models import EmailMessage


@admin.register(EmailMessage)
class EmailMessageAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "email_provider",
        "pre_sent_data",
        "date_sent",
        )
    search_fields = (
        "pre_sent_data",
        "post_sent_data",
        )
    ordering = ("-created_at",)

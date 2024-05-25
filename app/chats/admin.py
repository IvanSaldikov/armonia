from django.contrib import admin
from import_export.admin import ImportExportMixin

from chats.models import Room, Message


@admin.register(Room)
class RoomAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = (
        "slug",
        "user",
        "problem",
        "created_at",
        "updated_at",
        "id",
        )
    search_fields = (
        "name",
        "slug",
        "user__email",
        )
    ordering = ("-created_at",)


@admin.register(Message)
class MessageAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = (
        "room",
        "role",
        "message",
        "tries_to_get_the_answer",
        "photo_src",
        "date_time_read",
        "created_at",
        "id",
        )
    search_fields = (
        "room__user__email",
        "message",
        )
    ordering = ("-created_at",)

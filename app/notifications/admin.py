from django.contrib import admin
from django.contrib import messages
from import_export.admin import ImportExportMixin

from config.logger import get_module_logger
from notifications.utils.notification_manager import NotificationManager

logger = get_module_logger("admin notification")

from notifications.models import ServiceProvider, Notification, NotificationConnection


@admin.register(ServiceProvider)
class ServiceProviderAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = (
        "name",
        "is_active",
        "created_at",
        "updated_at",
        "id",
        )
    search_fields = (
        "name",
        "created_at",
        "updated_at",
        )
    ordering = ("-created_at",)
    list_filter = ("is_active",
                   )


@admin.action(description="Resend notification")
def resend_notification(modeladmin, request, queryset):
    notification_ids = []
    for notification in queryset:
        notification: Notification = notification
        if not notification.is_sent:
            logger.info(f"Trying to resend notification with ID: {notification.id}")
            NotificationManager.notify_all_connections(message_id=notification.message.id)
            notification_ids.append(notification.id)
    messages.add_message(request,
                         messages.SUCCESS,
                         f"Notifications {notification_ids} has been resent successfully"
                         )


@admin.register(Notification)
class NotificationAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = (
        "created_at",
        "date_sent",
        "is_sent",
        "service_provider",
        "updated_at",
        "internal_message_id",
        "is_sent_by_user",
        "message_id",
        "id",
        )
    search_fields = (
        "internal_message_id",
        "id",
        "created_at",
        "updated_at",
        )
    ordering = ("-created_at",)
    list_filter = ("is_sent",
                   "service_provider",
                   "is_sent_by_user",
                   )
    autocomplete_fields = ("message",
                           )
    actions = (resend_notification,)


@admin.register(NotificationConnection)
class ConnectionsAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = (
        "uuid",
        "user",
        "service_provider",
        "connection_number",
        "is_active",
        "created_at",
        "updated_at",
        "id",
        )
    search_fields = (
        "uuid",
        "connection_number",
        "created_at",
        "updated_at",
        )
    ordering = ("-created_at",
                )
    list_filter = ("service_provider",
                   "is_active",
                   )

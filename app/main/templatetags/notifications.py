from django import template

from notifications.models import ServiceProvider, NotificationConnection
from notifications.utils.connection_manager import ConnectionManager
from users.models import User

register = template.Library()


@register.filter('get_notification_connection')
def get_notification_connection(service_provider_obj: ServiceProvider, user: User) -> NotificationConnection:
    return ConnectionManager.get_is_connected(service_provider_obj=service_provider_obj,
                                              user=user,
                                              )

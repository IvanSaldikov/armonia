import uuid

from asgiref.sync import sync_to_async
from django.db.models import QuerySet
from django.urls import reverse

from notifications.models import ServiceProvider, NotificationConnection
from users.models import User


class ConnectionManager:

    @classmethod
    async def init_connection_and_get_uri(cls, service_provider_name: str, data: dict) -> str:
        service_provider_obj = await sync_to_async(cls.get_service_provider_by_name)(name=service_provider_name)
        connection_obj = await sync_to_async(cls.create_notification_connection)(
            service_provider=service_provider_obj,
            data=data,
            )
        return cls._get_url(connection_obj=connection_obj)

    @classmethod
    def create_notification_connection(cls,
                                       service_provider: ServiceProvider,
                                       data: dict,
                                       ) -> NotificationConnection:
        new_connection = NotificationConnection()
        new_connection.service_provider = service_provider
        new_connection.data = data
        new_connection.save()
        return new_connection

    @staticmethod
    def _get_url(connection_obj: NotificationConnection) -> str:
        return reverse("confirm_notification_connection",
                       args=[connection_obj.uuid],
                       )

    @classmethod
    def get_service_provider_by_name(cls, name: str) -> ServiceProvider:
        return cls.get_active_service_providers().filter(name=name).first()

    @classmethod
    def get_active_service_providers(cls) -> QuerySet[ServiceProvider]:
        return ServiceProvider.objects.filter(is_active=True).all()

    @classmethod
    def get_is_connected(cls,
                         service_provider_obj: ServiceProvider,
                         user: User,
                         ) -> NotificationConnection | None:
        qs = cls._get_all_active_notification_connections()
        return qs.filter(service_provider=service_provider_obj,
                         user=user,
                         ).first()

    @classmethod
    def _get_all_active_notification_connections(cls) -> QuerySet[NotificationConnection]:
        return NotificationConnection.objects.filter(is_active=True).prefetch_related("service_provider")

    @classmethod
    def confirm_notification_connection_by_uuid(cls,
                                                uuid_id: uuid.UUID,
                                                user: User,
                                                ) -> NotificationConnection | None:
        qs = cls._get_all_active_notification_connections()
        connection = qs.get(uuid=uuid_id)
        connection.user = user
        connection.save(update_fields=["user",
                                       ]
                        )
        user.is_connected_notifications = True
        user.save(update_fields=["is_connected_notifications",
                                 ]
                  )
        return connection

    @classmethod
    def remove_notification_connection(cls,
                                       service_provider_name: str,
                                       user: User,
                                       ) -> NotificationConnection | None:
        qs = cls._get_all_active_notification_connections()
        connection = qs.get(service_provider__name__iexact=service_provider_name,
                            user=user,
                            )
        connection.is_active = False
        connection.save(update_fields=["is_active"])
        return connection

    @classmethod
    def get_user_notification_connections(cls, user: User) -> QuerySet[NotificationConnection] | None:
        qs = cls._get_all_active_notification_connections()
        return qs.filter(user=user).all()

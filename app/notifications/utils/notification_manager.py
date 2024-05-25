import asyncio
from datetime import datetime

from asgiref.sync import sync_to_async
from django.db.models import QuerySet

from chats.consts import MessageRole
from chats.models import Message
from chats.utils.room import RoomUtils
from common.utils.rabbit_mq import RabbitMQ
from config.logger import get_module_logger
from notifications.models import NotificationConnection, Notification, ServiceProvider
from notifications.utils.builder import NotificatorInterfaceBuilder
from users.models import User

logger = get_module_logger("notification_manager")


class NotificationManager:
    RABBIT_MQ_QUEUE_NAME = "notifications"

    @classmethod
    def add_task_to_send_notification_from_rabbit_mq(cls, message: Message):
        RabbitMQ.send_message_to_rabbit_mq(queue_name=cls.RABBIT_MQ_QUEUE_NAME,
                                           data=message.id,
                                           )

    @classmethod
    def notify_all_connections(cls, message_id: int) -> None:
        logger.info(f"Starting notification sending for Message ID {message_id=}...")
        message_obj = RoomUtils.get_message_obj_based_on_message_id(message_id=message_id)
        if not message_obj:
            logger.error(f"NO MESSAGE FOUND WITH ID: {message_id=}")
            return None
        if message_obj.role not in [MessageRole.USER.value, MessageRole.ASSISTANT.value]:
            logger.warning(f"{message_obj.role=} is NOT User OR Assistant -> Exiting from Notifications")
            return None
        user = message_obj.room.user
        logger.info(f"Got user from {message_obj.id=}. Sending notifications...")
        asyncio.run(cls._send_notifications(user=user,
                                            message_obj=message_obj,
                                            )
                    )

    @classmethod
    async def _send_notifications(cls,
                                  user: User,
                                  message_obj: Message,
                                  ) -> None:
        if message_obj.role not in [MessageRole.USER.value, MessageRole.ASSISTANT.value]:
            logger.warning(f"{message_obj.role=} is NOT User OR Assistant -> Exiting from Notifications")
            return
        conns = await sync_to_async(cls._get_user_notification_connections_list)(user=user)
        for conn in conns:
            service_provider_name = conn.service_provider.name
            notification_obj = await sync_to_async(cls._add_notification_to_db)(
                service_provider=conn.service_provider,
                message_obj=message_obj,
                )
            notificator = NotificatorInterfaceBuilder.get_interface_based_on_service_provider_name(
                name=service_provider_name
                )
            if not notificator:
                logger.warning(f"No notificator was found for {service_provider_name=}")
                continue
            logger.info(f"Sending {service_provider_name=} Notification for user {user=} with {conn.data=}."
                        f"MessageID: {message_obj.id=}."
                        )
            message_data = await notificator.notify_user(message_obj=message_obj,
                                                         data=conn.data,
                                                         )
            if not message_data:
                return
            internal_message_id = message_data.get("message_id")
            await sync_to_async(cls._set_notification_is_sent_successfully)(notification_obj=notification_obj,
                                                                            data=message_data,
                                                                            internal_message_id=internal_message_id,
                                                                            )

    @classmethod
    def _add_notification_to_db(cls,
                                service_provider: ServiceProvider,
                                message_obj: Message,
                                ) -> Notification:
        new_notification, _ = Notification.objects.get_or_create(service_provider=service_provider,
                                                                 message=message_obj,
                                                                 )
        return new_notification

    @classmethod
    def _set_notification_is_sent_successfully(cls,
                                               notification_obj: Notification,
                                               internal_message_id: int,
                                               data: dict,
                                               ) -> None:
        notification_obj.is_sent = True
        notification_obj.data = data
        notification_obj.internal_message_id = internal_message_id
        notification_obj.date_sent = datetime.utcnow()
        notification_obj.save(update_fields=["is_sent",
                                             "data",
                                             "date_sent",
                                             "updated_at",
                                             "internal_message_id",
                                             ]
                              )

    @classmethod
    def _get_user_notification_connections(cls, user: User) -> QuerySet[NotificationConnection]:
        from notifications.utils.connection_manager import ConnectionManager
        return ConnectionManager.get_user_notification_connections(user=user)

    @classmethod
    def _get_user_notification_connections_list(cls, user: User) -> list[NotificationConnection]:
        return list(cls._get_user_notification_connections(user=user))

    @classmethod
    def get_previous_notification(cls, message: Message) -> Notification | None:
        prev_message = RoomUtils.get_message_before_message(message=message)
        logger.info(f"{prev_message=}")
        return Notification.objects.filter(message=prev_message).first()

    @classmethod
    def add_notification_by_user(cls,
                                 data: dict,
                                 internal_message_id: int,
                                 service_provider: ServiceProvider = None,
                                 ) -> Notification:
        notification = Notification()
        notification.internal_message_id = internal_message_id
        notification.data = data
        notification.is_sent = True
        notification.date_sent = datetime.utcnow()
        notification.is_sent_by_user = True
        if not service_provider:
            service_provider = cls.get_default_service_provider()
        notification.service_provider = service_provider
        notification.save()
        return notification

    @classmethod
    def get_default_service_provider(cls) -> ServiceProvider:
        return ServiceProvider.objects.first()

    @classmethod
    def set_up_message_obj_for_notification(cls, notification_id: int, message: Message) -> Notification:
        notification = Notification.objects.get(id=notification_id)
        notification.message = message
        notification.save(update_fields=["updated_at",
                                         "message",
                                         ]
                          )
        return notification

from abc import ABC, abstractmethod

from chats.models import Message
from notifications.models import Notification


class BasicNotificationInterface(ABC):

    @classmethod
    @abstractmethod
    async def notify_user(cls,
                          message_obj: Message,
                          data: dict,
                          ) -> dict:
        pass

    #
    # @classmethod
    # @abstractmethod
    # async def send_photo(cls,
    #                      notification_obj: Notification,
    #                      ) -> dict:
    #     pass

    @classmethod
    def get_message_obj_from_internal_message_id(cls, internal_message_id: int) -> Message | None:
        notification: Notification = Notification.objects.filter(internal_message_id=internal_message_id).first()
        if not notification:
            return None
        return notification.message

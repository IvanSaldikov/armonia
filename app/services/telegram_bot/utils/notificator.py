from asgiref.sync import sync_to_async
from telegram.helpers import escape_markdown

from chats.consts import MessageRole
from chats.models import Message
from chats.utils.room import RoomUtils
from config.logger import get_module_logger
from notifications.interfaces import BasicNotificationInterface
from services.telegram_bot.utils.main import MainStdiffIOBot

logger = get_module_logger("TelegramNotificator")


class TelegramNotificator(BasicNotificationInterface):

    @classmethod
    async def notify_user(cls,
                          message_obj: Message,
                          data: dict,
                          ) -> dict | None:
        from notifications.utils.notification_manager import NotificationManager
        if message_obj.role not in [MessageRole.USER.value, MessageRole.ASSISTANT.value]:
            logger.warning(f"{message_obj.role=} is NOT User OR Assistant -> Exiting from Notifications")
            return
        logger.info(f"Sending Telegram notification about Message id: {message_obj.id}...")
        chat_id = cls._get_chat_id_from_json(data=data)
        previous_notification_obj = await sync_to_async(NotificationManager.get_previous_notification)(message=message_obj)
        reply_to_message_id = None
        if previous_notification_obj:
            logger.info(f"{previous_notification_obj.id=}")
            logger.info(f"{previous_notification_obj.data=}")
            data = previous_notification_obj.data
            if data:
                reply_to_message_id = await sync_to_async(cls._get_message_id)(data=previous_notification_obj.data)
        else:
            logger.info(f"No previous notification was found. Its a first message in the room ID: {message_obj.room.id}")
        caption_from = await sync_to_async(cls._get_caption_from)(message_obj=message_obj)
        if message_obj.photo:
            full_path = message_obj.photo.path
            message = await MainStdiffIOBot.send_photo(chat_id=chat_id,
                                                       full_path=full_path,
                                                       reply_to_message_id=reply_to_message_id,
                                                       )
        else:
            text = cls._make_message_safe_for_telegram(text=message_obj.message)
            text = f"""`{caption_from}`: {text}"""
            message = await MainStdiffIOBot.send_message(text=text,
                                                         chat_id=chat_id,
                                                         reply_to_message_id=reply_to_message_id,
                                                         )
        logger.info(f"...Notification about Message id: {message_obj.id} has been sent")
        return message.to_dict()

    @classmethod
    def _get_caption_from(cls, message_obj: Message) -> str:
        return RoomUtils.ME if message_obj.role == MessageRole.USER.value else message_obj.room.problem.name

    @staticmethod
    def _make_message_safe_for_telegram(text: str) -> str:
        text = escape_markdown(text)
        text = text.replace("!", "\\!")
        text = text.replace(".", "\\.")
        text = text.replace(",", "\\,")
        text = text.replace("'", "\\'")
        text = text.replace("-", "\\-")
        text = text.replace("#", "\\#")
        text = text.replace("(", "\\(")
        text = text.replace(")", "\\)")
        text = text.replace(":", "\\:")
        text = text.replace("<", "")
        text = text.replace(">", "")
        return text

    # @classmethod
    # async def send_photo(cls,
    #                      notification_obj: Notification | None,
    #                      ) -> dict | None:
    #     logger.info(f"Sending to Telegram Photo from message with id {notification_obj.message.id}...")
    #     chat_id = cls._get_chat_id_from_notification_data(data=notification_obj.data)
    #     reply_to_message_id = cls._get_message_id(data=notification_obj.data)
    #     if notification_obj.message.photo:
    #         full_path = notification_obj.message.photo.path
    #         message = await MainStdiffIOBot.send_photo(chat_id=chat_id,
    #                                                    full_path=full_path,
    #                                                    reply_to_message_id=reply_to_message_id,
    #                                                    )
    #         logger.info(f"...Photo of message with id: {notification_obj.message.id} has been sent")
    #         return message.to_dict()
    #     logger.error(f"Photo is empty")
    #     return None

    @staticmethod
    def _get_chat_id_from_json(data: dict) -> int:
        return data["message"]["chat"]["id"]

    @staticmethod
    def _get_message_id(data: dict) -> int:
        return data["message_id"]

    @staticmethod
    def _get_chat_id_from_notification_data(data: dict) -> int:
        return data["chat"]["id"]

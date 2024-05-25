from asgiref.sync import sync_to_async
from telegram import Update
from telegram.ext import ContextTypes

from config.logger import get_module_logger

logger = get_module_logger("telegram_bot_reply_handler")

from services.telegram_bot.handlers.response import send_response
from services.telegram_bot.utils.templates import render_template


async def reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from notifications.utils.notification_manager import NotificationManager
    from services.telegram_bot.utils.notificator import TelegramNotificator
    from chats.utils.room import RoomUtils

    logger.info(f"REPLY {update=}")
    logger.info(f"REPLY {context=}")
    # from typing import cast
    # from telegram import User
    # user_id = cast(User, update.effective_user).id
    user_message = update.message.text
    message_id = update.message.id
    reply_to_message = update.message.reply_to_message
    if not reply_to_message:
        await send_response(
            update, context, response=render_template("error_you_should_reply.j2")
            )
        return
    reply_to_message_id = reply_to_message.message_id
    logger.info(f"{reply_to_message=}")
    logger.info(f"{reply_to_message_id=}")
    # Find in DB the message we want to reply for
    message_obj = await sync_to_async(TelegramNotificator.get_message_obj_from_internal_message_id)(internal_message_id=reply_to_message_id)
    if not message_obj:
        logger.warning(f"Message with Internal Message ID {reply_to_message_id} was not found")
        return
    notification = await sync_to_async(NotificationManager.add_notification_by_user)(internal_message_id=message_id,
                                                                                     data=update.message.to_dict(),
                                                                                     )
    await sync_to_async(RoomUtils.send_user_input_to_celery)(user_input=user_message,
                                                             room_id=message_obj.room_id,
                                                             notification_id=notification.id,
                                                             )

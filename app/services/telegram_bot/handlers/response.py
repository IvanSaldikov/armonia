from typing import cast

from telegram import Chat, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes


async def send_response(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    response: str,
    keyboard: InlineKeyboardMarkup | None = None,
) -> None:
    args = {
        "disable_web_page_preview": True,
        "text": response,
        "reply_to_message_id": update.effective_message.id,
    }
    if keyboard:
        args["reply_markup"] = keyboard

    await update.effective_message.reply_html(**args)


async def send_photo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    photo_url: str,
    keyboard: InlineKeyboardMarkup | None = None,
    caption: str = None,
) -> None:
    caption_in = "Result avatar"
    if caption:
        caption_in = caption
    args = {
        "caption": caption_in,
        "photo": photo_url,
        "reply_to_message_id": update.effective_message.id,
    }
    if keyboard:
        args["reply_markup"] = keyboard

    # await context.bot.send_photo(**args)
    await update.effective_message.reply_photo(**args)


def _get_chat_id(update: Update) -> int:
    return cast(Chat, update.effective_chat).id

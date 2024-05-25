from telegram import Update
from telegram.ext import ContextTypes

from notifications.utils.connection_manager import ConnectionManager
from services.telegram_bot.handlers.response import send_response
from services.telegram_bot.utils.templates import render_template


async def connect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"CONNECT {update=}")
    print(f"CONNECT {context=}")
    # context=<telegram.ext._callbackcontext.CallbackContext object at 0x7fdb90bc6cf0>
    ret = await ConnectionManager.init_connection_and_get_uri(service_provider_name="Telegram", data=update.to_dict())
    await send_response(update, context, response=render_template("connect.j2", data={"url": ret}))

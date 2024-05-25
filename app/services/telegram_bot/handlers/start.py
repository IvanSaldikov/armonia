from telegram import Update
from telegram.ext import ContextTypes

from services.telegram_bot.handlers.response import send_response
from services.telegram_bot.utils.templates import render_template


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"START {update=}")
    print(f"START {context=}")
    await send_response(update, context, response=render_template("start.j2"))

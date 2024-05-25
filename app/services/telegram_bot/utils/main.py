from telegram import Bot, Message
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler, MessageHandler, filters,
    )

from config.logger import get_module_logger
from services.telegram_bot import app_config, handlers

logger = get_module_logger("telegram_bot_utils")


class MainStdiffIOBot:
    COMMAND_HANDLERS = {
        "start": handlers.start,
        "connect": handlers.connect,
        "disconnect": handlers.disconnect,
        }

    @classmethod
    def run_polling(cls):
        cls._verify_api_key_in_env()

        application = ApplicationBuilder().token(app_config.BOT_TELEGRAM_BOT_TOKEN).build()

        for command_name, command_handler in cls.COMMAND_HANDLERS.items():
            application.add_handler(CommandHandler(command_name, command_handler))

        application.add_handler(
            MessageHandler(filters.TEXT & (~filters.COMMAND), handlers.reply)
            )

        application.run_polling()

    @classmethod
    async def send_message(cls,
                           chat_id: int,
                           text: str,
                           reply_to_message_id: int | None,
                           ) -> Message:
        cls._verify_api_key_in_env()
        bot = Bot(token=app_config.BOT_TELEGRAM_BOT_TOKEN)
        return await bot.send_message(chat_id=chat_id,
                                      text=text,
                                      reply_to_message_id=reply_to_message_id,
                                      disable_web_page_preview=False,
                                      parse_mode=ParseMode.MARKDOWN_V2,
                                      )

    @classmethod
    async def send_photo(cls,
                         chat_id: int,
                         full_path: str,
                         reply_to_message_id: int | None,
                         ) -> Message:
        cls._verify_api_key_in_env()
        bot = Bot(token=app_config.BOT_TELEGRAM_BOT_TOKEN)
        photo = open(full_path, 'rb')
        return await bot.send_photo(chat_id=chat_id,
                                    photo=photo,
                                    reply_to_message_id=reply_to_message_id,
                                    )

    @staticmethod
    def _verify_api_key_in_env():
        if not app_config.BOT_TELEGRAM_BOT_TOKEN:
            raise ValueError(
                "TELEGRAM_BOT_TOKEN env variables "
                "wasn't implemented in .env (both should be initialized)."
                )

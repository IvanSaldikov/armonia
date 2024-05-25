from __django_loader import load_django

load_django()

from config.logger import get_module_logger
from services.telegram_bot.utils.main import MainStdiffIOBot

logger = get_module_logger("main_bot_app_runner")

if __name__ == "__main__":
    try:
        MainStdiffIOBot.run_polling()
    except Exception as e:
        logger.error(str(e), exc_info=True)

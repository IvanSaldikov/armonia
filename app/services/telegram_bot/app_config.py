import os
from pathlib import Path

BOT_TELEGRAM_BOT_TOKEN = os.getenv("ARMONIA_TELEGRAM_BOT_API_KEY", None)

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"

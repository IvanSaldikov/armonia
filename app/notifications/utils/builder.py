from notifications.interfaces import BasicNotificationInterface
from services.telegram_bot.utils.notificator import TelegramNotificator


class NotificatorInterfaceBuilder:

    @classmethod
    def get_interface_based_on_service_provider_name(cls, name: str) -> BasicNotificationInterface | None:
        service_providers = {"Telegram": TelegramNotificator}

        return service_providers.get(name)

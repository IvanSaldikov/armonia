import datetime

from django.conf import settings
from django.db.models import F
from django.urls import reverse
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from api_keys.consts import MessagesLimit
from api_keys.exceptions import APIKeyNotFound, APIKeyExceededTotalLimit, APIKeyBlocked, APIKeyExceededAllowedNumberOfKeys, APIKeyExceededDailyLimit
from api_keys.models import APIKey
from config.logger import get_module_logger
from users.models import User

logger = get_module_logger("api_keys_util")


class APIKeysUtils:
    default_length = 32
    max_api_keys_allowed = 1

    @classmethod
    def generate_api_key_and_store_to_db(cls) -> str:
        import secrets
        return secrets.token_urlsafe(cls.default_length)

    @classmethod
    def is_amount_more_than_allowed(cls, user: User) -> bool:
        number_of_keys = len(user.api_keys.all())
        if number_of_keys > cls.max_api_keys_allowed:
            return True
        return False

    @classmethod
    def verify_api_key(cls, api_key: str) -> APIKey:
        api_key_obj: APIKey = APIKey.objects.filter(api_key=api_key).first()
        cls._verify_api_key_is_not_none(api_key_obj=api_key_obj)
        cls._verify_api_key_is_not_out_of_premium_limit(api_key_obj=api_key_obj)
        cls._verify_api_key_is_not_out_of_daily_limit(api_key_obj=api_key_obj)
        cls._verify_api_key_is_not_blocked(api_key_obj=api_key_obj)
        return api_key_obj

    @staticmethod
    def _verify_api_key_is_not_none(api_key_obj: APIKey) -> None:
        if api_key_obj is None:
            raise APIKeyNotFound

    @classmethod
    def _verify_api_key_is_not_out_of_premium_limit(cls, api_key_obj: APIKey) -> None:
        if api_key_obj.usage_times + api_key_obj.usage_times_web >= cls.get_limit_num_by_api_key_obj(api_key_obj):
            raise APIKeyExceededTotalLimit

    @classmethod
    def _verify_api_key_is_not_out_of_daily_limit(cls, api_key_obj: APIKey) -> None:
        if api_key_obj.usage_free_times_daily >= MessagesLimit.DailyFree.value:
            raise APIKeyExceededDailyLimit

    @staticmethod
    def _verify_api_key_is_not_blocked(api_key_obj: APIKey) -> None:
        if api_key_obj.is_blocked:
            raise APIKeyBlocked

    @staticmethod
    def increase_amount_of_usage_for_user_api_key_premium(api_key: "APIKey") -> None:
        logger.info("Increasing amount of usage for API Key: Premium tier")
        api_key.usage_times_web += 1
        api_key.save(update_fields=["usage_times_web",
                                    "updated_at",
                                    ]
                     )

    @staticmethod
    def increase_amount_of_usage_for_user_api_key_free(api_key: "APIKey") -> None:
        logger.info("Increasing amount of usage for API Key: Free tier")
        if not api_key.usage_daily_first_date_time:
            api_key.usage_daily_first_date_time = datetime.datetime.now()
        api_key.usage_free_times_daily += 1
        api_key.usage_free_times_total += 1
        api_key.save(update_fields=["usage_daily_first_date_time",
                                    "usage_free_times_daily",
                                    "usage_free_times_total",
                                    "updated_at",
                                    ]
                     )

    @staticmethod
    def increase_amount_of_attempts_for_user_api_key(api_key: "APIKey") -> None:
        api_key.attempts = F("attempts") + 1
        api_key.save(update_fields=["attempts", "updated_at"])

    @staticmethod
    def get_please_to_website_message() -> str:
        domain_name = settings.DEFAULT_DOMAIN_NAME
        url = reverse("api-keys-list")
        return f"Please go to {domain_name}{url} to obtain the API key."

    @staticmethod
    def get_contact_us_message() -> str:
        domain_name = settings.DEFAULT_DOMAIN_NAME
        url = reverse("contact-us")
        return f"Please contact us at {domain_name}{url} to solve the problem if it will take long for you."

    @classmethod
    def get_user_latest_api_key_str(cls, user: User) -> str:
        api_key = cls.get_user_latest_api_key_obj(user=user)
        if api_key:
            return api_key.api_key
        return "<YOUR_API_KEY>"

    @staticmethod
    def get_user_latest_api_key_obj(user: User) -> APIKey | None:
        if user.is_authenticated:
            api_key: APIKey = user.api_keys.filter(is_blocked=False).first()
            if api_key:
                return api_key
        return None

    @classmethod
    def get_and_validate_api_key_from_headers(cls, request) -> APIKey:
        api_key = request.META.get('HTTP_TOKEN')
        please_go_msg = APIKeysUtils.get_please_to_website_message()
        if not api_key:
            raise ValidationError({"token": f"API Key is not set in the request header. Please set up a header "
                                            f"`HTTP_TOKEN` with your API key included in it. {please_go_msg}"}
                                  )
        try:
            api_key_obj = APIKeysUtils.verify_api_key(api_key=api_key)
        except APIKeyNotFound:
            raise ValidationError({"token": f"The API Key that you included in the `HTTP_TOKEN` header was not found."
                                            f" {please_go_msg}"}
                                  )
        except APIKeyExceededTotalLimit:
            raise ValidationError({"token": f"This API Key has exceeded total limit of requests. {please_go_msg}"})
        except APIKeyExceededDailyLimit:
            raise ValidationError({"token": f"This API Key has exceeded daily limit of requests. {please_go_msg}"})
        except APIKeyBlocked:
            raise ValidationError({"token": "Token is blocked"})
        return api_key_obj

    @classmethod
    def generate_api_key_for_user(cls, user: User) -> APIKey:
        if cls.is_amount_more_than_allowed(user=user):
            raise APIKeyExceededAllowedNumberOfKeys
        new_api_key = APIKey()
        new_api_key.user = user
        new_api_key.api_key = cls.generate_api_key_and_store_to_db()
        new_api_key.save()
        return new_api_key

    @classmethod
    def get_limit_num_by_api_key_obj(cls, api_key_obj: APIKey) -> int:
        return api_key_obj.premium_limit

    @classmethod
    def set_daily_usage_to_zero(cls) -> int:
        total_records_to_zero = 0
        api_key_objs_to_check = APIKey.objects.filter(usage_daily_first_date_time__isnull=False, is_blocked=False).all()
        for api_key in api_key_objs_to_check:
            if not api_key.usage_daily_first_date_time:
                continue
            if timezone.now() - datetime.timedelta(days=1) >= api_key.usage_daily_first_date_time:
                api_key.usage_daily_first_date_time = None
                api_key.usage_free_times_daily = 0
                total_records_to_zero += 1
                api_key.save(update_fields=["usage_daily_first_date_time",
                                            "usage_free_times_daily",
                                            "updated_at",
                                            ]
                             )
        return total_records_to_zero

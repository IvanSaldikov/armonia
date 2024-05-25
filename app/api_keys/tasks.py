from celery import shared_task

from api_keys.utils import APIKeysUtils


@shared_task
def set_daily_usage_to_zero() -> int:
    return APIKeysUtils.set_daily_usage_to_zero()

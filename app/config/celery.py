import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config",
             backend=settings.CELERY_BACKEND_URL,
             broker=settings.BROKER_URL,
             )

# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.config_from_object("django.conf:settings")
app.autodiscover_tasks(settings.INSTALLED_APPS)
# Configure Celery to use threads for concurrency
app.conf.update(
    task_concurrency=4,  # Use n threads for concurrency
    worker_prefetch_multiplier=2  # Prefetch tasks at a time into the memory
    )

# Discover all module inside tasks
for app_name in settings.INSTALLED_APPS:
    if app_name.startswith("django"):
        continue
    for root, dirs, files in os.walk(app_name + "/tasks"):
        for file in files:
            if (
                file.startswith("__")
                or file.endswith(".pyc")
                or not file.endswith(".py")
            ):
                continue
            file = file[:-3]
            app.autodiscover_tasks([app_name + ".tasks"], related_name=file)

# Celery beat schedule
# http://docs.celeryproject.org/en/latest/reference/celery.schedules.html#celery.schedules.crontab
common_beat_schedule = {
    "update_metrics_in_admin_dashboard": {
        "task": "admin_dashboard.tasks.save_metrics_to_db",
        "schedule": crontab(minute="0", hour="3"),
        },
    "set_daily_usage_to_zero": {
        "task": "api_keys.tasks.set_daily_usage_to_zero",
        "schedule": crontab(minute="*/5"),
        },
    }

app.conf.beat_schedule = {}

app.conf.beat_schedule.update(common_beat_schedule)

from celery import shared_task

from admin_dashboard.utils.metrics import MetricsUtils


@shared_task
def save_metrics_to_db() -> str:
    return MetricsUtils.save_metrics_to_db()

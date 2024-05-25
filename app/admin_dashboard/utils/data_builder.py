import datetime

from django.db.models import QuerySet

from admin_dashboard.models import Stat


class DataBuilder:

    @classmethod
    def get_metrics_from_db(cls, max_time_window=None) -> QuerySet[Stat]:
        if not max_time_window:
            max_time_window = datetime.datetime.now() - datetime.timedelta(days=90)
        stats = Stat.objects.order_by("-created_at").filter(created_at__gt=max_time_window).all()
        return stats

from django.urls import path

from admin_dashboard.views import (
    service_metrics,
    )

app_name = "admin_dashboard"

urlpatterns = [
    path("service_metrics", service_metrics, name="service_metrics"),
    ]

from django.contrib import admin
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render

from admin_dashboard.utils.metrics import MetricsUtils


def is_allowed_to_view(user):
    return user.is_staff or user.is_superuser


@user_passes_test(is_allowed_to_view)
def service_metrics(request):
    context = admin.site.each_context(request)
    context["metrics"] = MetricsUtils.calculate_metrics()
    context["chart_metrics"] = MetricsUtils.get_chart_metrics()
    return render(request=request, context=context, template_name="service_metrics.html")

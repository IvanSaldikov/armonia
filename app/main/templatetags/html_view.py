from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def status_html_view(status_name: str) -> str:
    default_style = "light"
    status_name_style = {"GENERATED": "success",
                         "ERROR": "danger",
                         "API_KEY_BLOCKED": "danger",
                         "API_KEY_EXCEEDED_THE_LIMIT": "danger",
                         "GENERATING": "warning",
                         "PENDING": "info",
                         "QUEUE": "info",
                         }
    style = status_name_style.get(status_name) or default_style

    ret = f'<span class="badge text-bg-{style}">{status_name}</span>'
    if status_name == "API_KEY_EXCEEDED_THE_LIMIT":
        url_pricing = reverse("pricing")
        ret = f'{ret} <a href="{url_pricing}">Purchase API Key</a>'
    return mark_safe(ret)

# https://stackoverflow.com/questions/433162/can-i-access-constants-in-settings-py-from-templates-in-django
from django.conf import settings


def my_settings(request):
    return {"DEBUG": settings.DEBUG,
            "TESTING": settings.TESTING,
            "MEDIA_URL": settings.MEDIA_URL,
            }

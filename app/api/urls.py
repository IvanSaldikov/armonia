from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.endpoints_urls import PING_URL
from api.views.ping import PingView
from chats.views_api import ChatReadMessagesView

urlpatterns = [
    # Hello
    path(f"{PING_URL}", PingView.as_view(), name="ping"),
    # Django Allauth - Social Accounts Control Module for User Auth - needs for callbacks
    path(f"accounts/", include("allauth.urls")),
    ]


# https://www.django-rest-framework.org/api-guide/viewsets/
router = DefaultRouter()
router.register("chats", ChatReadMessagesView, basename="chats")
urlpatterns += router.urls

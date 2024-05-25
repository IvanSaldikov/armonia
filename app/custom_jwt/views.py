import requests
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from custom_jwt.providers import OAuth2ClientExtended
from custom_jwt.serializers import CustomSocialAccountSerializer
from dj_rest_auth.registration.views import (
    SocialAccountListView,
    SocialConnectView,
    SocialLoginView,
)
from django.conf import settings
from rest_framework.permissions import IsAuthenticated
from users.utils.auth import AuthUtils


class GoogleConnect(SocialConnectView):
    adapter_class = GoogleOAuth2Adapter


class GoogleOAuth2AdapterExt(GoogleOAuth2Adapter):
    """Needed to control authentication via Social App"""

    def complete_login(self, request, app, token, **kwargs):
        resp = requests.get(
            self.profile_url,
            params={"access_token": token.token, "alt": "json"},
        )
        resp.raise_for_status()
        extra_data = resp.json()
        email = extra_data.get("email")
        AuthUtils.check_allowance_to_login(provider_id=self.provider_id, email=email)
        login = self.get_provider().sociallogin_from_response(request, extra_data)
        return login


class GoogleLogin(SocialLoginView):
    authentication_classes = []  # disable authentication
    adapter_class = GoogleOAuth2AdapterExt
    callback_url = settings.SOCIAL_LOGIN_CALLBACK_URL_GOOGLE
    client_class = OAuth2ClientExtended


class CustomAccountAdapter(DefaultAccountAdapter):
    """This adapter is used in AllAuth lib when registering a user in db"""

    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit=False)
        if commit:
            user.save()
        return user


class CustomSocialAccountListView(SocialAccountListView):
    serializer_class = CustomSocialAccountSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return SocialAccount.objects.filter(user=self.request.user)

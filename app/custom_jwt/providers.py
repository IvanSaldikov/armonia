from allauth.socialaccount.providers.oauth2.client import OAuth2Client, OAuth2Error
from rest_framework.exceptions import ValidationError


class OAuth2ClientExtended(OAuth2Client):
    """Extended class of OAuth2 Client for supporting 400-codes errors (instead of 500) in JSON-responses"""

    def get_access_token(self, code):
        try:
            super().get_access_token(code)
        except OAuth2Error:
            raise ValidationError({"code": "Wrong code"})

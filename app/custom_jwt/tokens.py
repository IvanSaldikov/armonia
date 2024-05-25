from datetime import timedelta

from rest_framework_simplejwt.tokens import AccessToken, BlacklistMixin


class JWTAccessToken(BlacklistMixin, AccessToken):
    pass

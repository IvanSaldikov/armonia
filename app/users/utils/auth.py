from allauth.socialaccount.models import SocialAccount
from rest_framework.exceptions import ValidationError


class AuthUtils:
    @staticmethod
    def check_allowance_to_login(provider_id: str, email: str) -> None:
        """If a user has not previously connected a Social account he cannot sign in to the Platform"""
        allowance = SocialAccount.objects.filter(
            provider=provider_id, extra_data__contains=email
        ).first()
        if allowance is None:
            raise ValidationError(
                {
                    "email": "You have not allowed access with this Social account. "
                    "Please use email and password authentication as usual first and then "
                    "connect your Social account first to your Account on the Settings"
                    "page at your personal page of the website"
                }
            )

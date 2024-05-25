from allauth.utils import build_absolute_uri

from users.models import User


class UserProfileUtils:
    @classmethod
    def get_user_profile_page(cls, user: "User"):
        return build_absolute_uri(None, f"/user/{user.uuid}", protocol="https")

    @classmethod
    def get_first_admin(cls) -> User:
        return User.objects.filter(is_superuser=True).order_by("date_joined").first()

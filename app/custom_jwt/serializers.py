import datetime

import pytz
from allauth.socialaccount.models import SocialAccount
from dj_rest_auth.registration.serializers import (
    RegisterSerializer,
    SocialAccountSerializer,
    )
from dj_rest_auth.serializers import LoginSerializer, UserDetailsSerializer
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.validators import ValidationError

from common.consts import LevelOfKnowledge
from common.utils.helpers import HelperUtils
from users.models import User


class LoginSerializerWithoutUserName(LoginSerializer):
    """Returns Login serializer without username field"""

    username = None

    def validate(self, attrs):
        super().validate(attrs)
        return attrs


class RegistrationSerializerWithoutUserName(RegisterSerializer):
    """Returns Registration serializer without username field"""

    username = None
    first_name = serializers.CharField(
        label="First Name", max_length=150, write_only=True, required=False
        )
    last_name = serializers.CharField(
        label="Last Name", max_length=150, write_only=True, required=False
        )

    def validate(self, attrs):
        self._check_is_registration_on()
        return super().validate(attrs)

    def get_cleaned_data(self):
        cleaned_data = super().get_cleaned_data()
        return {
            **cleaned_data,
            "first_name": self.validated_data.get("first_name", ""),
            "last_name": self.validated_data.get("last_name", ""),
            }

    @staticmethod
    def _check_is_registration_on():
        if not settings.IS_REGISTRATION_ON:
            raise ValidationError(
                {
                    "details": "Registration process is in manual mode. Please contact us if you "
                               "want to be a part of our users"
                    }
                )

    def custom_signup(self, request, user):
        """Postprocessing after user has been registered"""
        validated_data = self.get_cleaned_data()
        user.first_name = validated_data.get("first_name")
        user.last_name = validated_data.get("last_name")
        user.save(
            update_fields=[
                "first_name",
                "last_name",
                "updated_at",
                ]
            )
        return user


UserModel = get_user_model()


class NewInterestSerializer(serializers.Serializer):
    section_id = serializers.IntegerField(
        min_value=1, help_text="Section ID (see the /sections endpoint)"
        )
    level = serializers.ChoiceField(choices=LevelOfKnowledge.choices())


class UserDetailsWithoutPkSerializer(UserDetailsSerializer):
    """User Private Information"""

    new_languages = serializers.ListField(
        child=serializers.IntegerField(label="Id of a language object"),
        write_only=True,
        help_text="Array of Languages IDs (see the languages endpoint)",
        )
    new_interests = serializers.ListField(
        child=NewInterestSerializer(label="Id of a section object"),
        write_only=True,
        help_text="Array of Section/Interest IDs (see the sections endpoint)",
        )
    is_active_subscription = serializers.SerializerMethodField(
        help_text="Does user have an active subscription at the moment?"
        )

    __metaclass__ = None

    def __new__(cls, *args, **kwargs):
        cls.__metaclass__ = super().Meta
        # Remove pk from the response, because it must be a hidden field
        cls.__metaclass__.fields = super().Meta.fields[1:]
        # Add additional user data
        cls.__metaclass__.fields = (
            "uuid",
            "email",
            "is_terms_of_use_accepted",
            "phone_number",
            "is_verified",
            "first_name",
            "last_name",
            "avatar_big",
            "avatar_small",
            "birth_date",
            "position",
            "company",
            "my_introduction",
            "education",
            "gender",
            "contact_telegram",
            "contact_linkedin",
            "contact_instagram",
            "contact_tiktok",
            "contact_twitter",
            "contact_facebook",
            "contact_additional_1",
            "contact_additional_2",
            "contact_additional_3",
            "subscription_ends",
            "new_languages",
            "new_interests",
            "is_active_subscription",
            )
        cls.__metaclass__.read_only_fields = (
            "uuid",
            "email",
            "is_verified",
            "avatar_big",
            "avatar_small",
            "is_active_subscription",
            )
        return UserDetailsSerializer.__new__(cls, *args, **kwargs)

    @staticmethod
    def get_is_active_subscription(obj: User):
        if obj.subscription_ends:
            return obj.subscription_ends > datetime.datetime.now(tz=pytz.UTC)
        else:
            return False

    @staticmethod
    def validate_birth_date(birth_date: datetime) -> datetime:
        year_min_int = settings.TEACH_ME_CLUB_AGE_MIN
        year_max_int = settings.TEACH_ME_CLUB_AGE_MAX
        year_min = datetime.timedelta(days=365 * year_min_int)
        year_max = datetime.timedelta(days=365 * year_max_int)
        if birth_date > HelperUtils.get_datetime_now().date() - year_min:
            err_str = (
                f"You should be more than {year_min_int} years old to use our service"
            )
            raise ValidationError(err_str)
        if birth_date < HelperUtils.get_datetime_now().now().date() - year_max:
            err_str = f"Are you more than {year_max_int} years old?"
            raise ValidationError(err_str)
        return birth_date


class CustomSocialAccountSerializer(SocialAccountSerializer):
    """
    serialize allauth SocialAccounts for use with a REST API
    """

    user_email = serializers.SerializerMethodField(
        label="User email",
        read_only=True,
        )

    class Meta:
        model = SocialAccount
        fields = (
            "id",
            "provider",
            "uid",
            "last_login",
            "date_joined",
            "user_email",
            )

    @staticmethod
    def get_user_email(obj: SocialAccount) -> str:
        # you have access to self.context['my_value']
        # you have access to obj.some_property
        return obj.extra_data.get("email")

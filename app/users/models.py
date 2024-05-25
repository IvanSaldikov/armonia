import random
import uuid

from django.contrib.auth import models as auth_models
from django.contrib.auth.models import UserManager
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.html import format_html
from django_countries.fields import CountryField

from common.utils.files import UploadUtils
from users.consts import Gender
from users.validators import ContactLinksValidator


class UserManagerExt(UserManager):

    def create_user(self, username=None, email=None, password=None, **extra_fields):
        if not username:
            username = self._create_username_based_on_email(email=email)
        return super().create_user(username=username, email=email, password=password, **extra_fields)

    def create_superuser(self, username=None, email=None, password=None, **extra_fields):
        if not username:
            username = self._create_username_based_on_email(email=email)
        return super().create_superuser(username=username, email=email, password=password, **extra_fields)

    @staticmethod
    def _create_username_based_on_email(email: str) -> str:
        return email.split("@")[0] + str(random.randint(1, 9999999999999))


class User(auth_models.AbstractUser):
    """
    Custom User model that uses the `email` field as unique identifier (instead
    of the default `username` field)
    https://docs.djangoproject.com/en/dev/topics/auth/customizing/#substituting-a-custom-user-model
    https://github.com/django/django/blob/master/django/contrib/auth/models.py
    https://github.com/django/django/blob/master/django/contrib/auth/base_user.py
    """

    id = models.AutoField(primary_key=True)

    username = models.CharField(max_length=110, null=True, default=None)

    # Overload fields
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
        blank=False,
        null=False,
        )
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    is_terms_of_use_accepted = models.BooleanField(default=False)
    preferences = models.JSONField(null=True, default=None)
    phone_number = models.CharField(max_length=20, null=True, default=None)
    is_verified = models.BooleanField(default=False)
    avatar_big = models.ImageField(
        null=True,
        default=None,
        upload_to=UploadUtils.get_image_path_for_user_avatars_big,
        max_length=500,
        # storage=UploadUtils.select_storage,
        validators=[
            FileExtensionValidator(UploadUtils.SUPPORTED_SOLUTION_FILE_EXTENSIONS)
            ],
        )
    avatar_small = models.ImageField(
        null=True,
        default=None,
        upload_to=UploadUtils.get_image_path_for_user_avatars_small,
        max_length=500,
        # storage=UploadUtils.select_storage,
        validators=[
            FileExtensionValidator(UploadUtils.SUPPORTED_SOLUTION_FILE_EXTENSIONS)
            ],
        )
    birth_date = models.DateField(
        null=True,
        default=None,
        blank=True,
        )
    position = models.CharField(
        max_length=150,
        null=True,
        default=None,
        blank=True,
        )
    company = models.CharField(
        max_length=150,
        null=True,
        default=None,
        blank=True,
        )
    my_introduction = models.TextField(
        null=True,
        default=None,
        blank=True,
        )
    education = models.CharField(
        max_length=350,
        null=True,
        default=None,
        blank=True,
        )
    gender = models.CharField(
        choices=Gender.choices(),
        null=True,
        default=None,
        blank=True,
        )
    contact_telegram = models.CharField(
        max_length=150,
        null=True,
        default=None,
        blank=True,
        validators=[ContactLinksValidator.get_telegram_url_validator],
        )
    contact_linkedin = models.CharField(
        max_length=150,
        null=True,
        default=None,
        blank=True,
        validators=[ContactLinksValidator.get_linkedin_url_validator],
        )
    contact_instagram = models.CharField(
        max_length=150,
        null=True,
        default=None,
        blank=True,
        validators=[ContactLinksValidator.get_instagram_url_validator],
        )
    contact_tiktok = models.CharField(
        max_length=150,
        null=True,
        default=None,
        blank=True,
        validators=[ContactLinksValidator.get_tiktok_url_validator],
        )
    contact_twitter = models.CharField(
        max_length=150,
        null=True,
        default=None,
        blank=True,
        validators=[ContactLinksValidator.get_twitter_url_validator],
        )
    contact_facebook = models.CharField(
        max_length=150,
        null=True,
        default=None,
        blank=True,
        validators=[ContactLinksValidator.get_facebook_url_validator],
        )
    contact_additional_1 = models.CharField(
        max_length=150,
        null=True,
        default=None,
        blank=True,
        validators=[ContactLinksValidator.get_url_validator],
        )
    contact_additional_2 = models.CharField(
        max_length=150,
        null=True,
        default=None,
        blank=True,
        validators=[ContactLinksValidator.get_url_validator],
        )
    contact_additional_3 = models.CharField(
        max_length=150,
        null=True,
        default=None,
        blank=True,
        validators=[ContactLinksValidator.get_url_validator],
        )
    subscription_ends = models.DateTimeField(
        default=None,
        null=True,
        blank=True,
        )
    country_code = CountryField(default=None, null=True, verbose_name="Country", help_text="Country")
    is_country_related_content_enabled = models.BooleanField(default=True, null=False, blank=False,
                                                             verbose_name="Enable Country Related Content",
                                                             help_text="The AI content will be related to the country "
                                                                       "which you will select in Preferences. If"
                                                                       " unchecked - a country-neutral content will be "
                                                                       " generated"
                                                             )
    is_connected_notifications = models.BooleanField(default=None, null=True, blank=True)
    is_email_messages_allowed = models.BooleanField(default=True, null=False, blank=False)
    objects = UserManagerExt()

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        abstract = False

    def __str__(self):
        return f"{self.email}"

    @property
    def country_flag(self) -> str | None:
        if self.country_code:
            return format_html(f"<img src='{self.country_code.flag}' alt='{self.country_code.name}' title='{self.country_code.name}'>")
        return '-'

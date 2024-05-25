from unittest.mock import patch, Mock

from django.contrib.auth import get_user_model
from django.db.models import QuerySet
from django.test import TestCase, override_settings
from django.urls import reverse
from django_countries.fields import Country
from rest_framework import status

from common.common_tests_utils import CommonTestCaseMixin, TEST_CACHE_SETTING, UserData
from users.models import User


class UsersTestCase(CommonTestCaseMixin, TestCase):

    fixtures = [
        "common/fixtures/social_app.json",
        ]

    def setUp(self):
        self.pre_populate_couple_users()
        self.prepare_tests_client()

    def test_user_registration_get(self):
        response = self.client.get(reverse("account_signup"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTemplateUsed(response, template_name='account/signup.html')

    @override_settings(CACHES=TEST_CACHE_SETTING)
    @patch("django_recaptcha.fields.ReCaptchaField.validate")
    def test_user_registration_post(self, validate_mock):
        user3: UserData = {"username": "user3",
                           "email": "user3@armonia.day",
                           "password": self.strong_password,
                           "user_obj": None
                           }
        validate_mock.return_value = Mock()

        users = self._get_registered_users()
        initial_amount_of_users = users.count()

        data = {"email": user3["email"],
                "password1": user3["password"],
                "username": user3["password"]
                }
        response = self.client.post(path=reverse("account_signup"), data=data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)
        self.assertEqual(users.count(), initial_amount_of_users + 1)

        user: User = self._get_user(email=user3["email"])
        self.assertEqual(user.email, user3["email"])
        self.assertEqual(user.country_code, Country(code=None))

    @staticmethod
    def _get_registered_users() -> QuerySet[User]:
        return get_user_model().objects.all()

    @staticmethod
    def _get_user(email: str) -> User:
        return get_user_model().objects.filter(email=email).first()

    @override_settings(CACHES=TEST_CACHE_SETTING)
    @patch("django_recaptcha.fields.ReCaptchaField.validate")
    def test_user_login(self, validate_mock):
        users = get_user_model().objects.all()
        self.assertEqual(users.count(), 2)
        validate_mock.return_value = Mock()
        data = {"login": self.user1["email"], "password": self.user1["password"]}
        response = self.client.post(path=reverse("account_login"), data=data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

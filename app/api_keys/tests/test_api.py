from unittest import skip

from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status

from api_keys.consts import MessagesLimit
from api_keys.models import APIKey
from common.common_tests_utils import CommonTestCaseMixin, TEST_CACHE_SETTING


class UsersTestCase(CommonTestCaseMixin, TestCase):

    fixtures = [
        "common/fixtures/social_app.json",
        ]

    def setUp(self):
        self.pre_populate_couple_users()

    def _login_user_1(self):
        self.user_login(email=self.user1["email"], password=self.user1["password"])


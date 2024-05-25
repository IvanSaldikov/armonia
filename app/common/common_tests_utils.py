import datetime
import typing
import unittest.mock as mock
from typing import TypedDict

if typing.TYPE_CHECKING:
    from problems.models import Problem
from django.conf import settings
from django.contrib import messages
from django.db.models import QuerySet
from django.test import Client, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from api_keys.models import APIKey
from api_keys.utils import APIKeysUtils
from chats.models import Room
from chats.utils.room import RoomUtils
from problems.models import Problem
from problems.utils import ProblemManager, ProblemTypeMinimum
from users.models import User

TEST_CACHE_SETTING = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    }


class UserData(TypedDict):
    username: str
    email: str
    password: str
    user_obj: User | None


class CommonTestCaseMixin:
    strong_password = "AddafkjmkDL!"
    DEFAULT_SEED = "123"

    def pre_populate_couple_users(self):
        self.user1: UserData = {"username": "user1",
                                "email": "user1@Armonia.day",
                                "password": self.strong_password,
                                "user_obj": None
                                }
        self.user2: UserData = {"username": "user2",
                                "email": "user2@Armonia.day",
                                "password": self.strong_password,
                                "user_obj": None
                                }
        users = [self.user1,
                 self.user2,
                 ]
        self.prepare_tests_users(user_data=users)

    def user_login(self, email: str, password: str):
        data = {"login": email, "password": password}
        self._make_login_request(data=data)

    @override_settings(CACHES=TEST_CACHE_SETTING)
    @mock.patch("django_recaptcha.fields.ReCaptchaField.validate")
    def _make_login_request(self, validate_mock, data):
        validate_mock.return_value = mock.Mock()
        response = self.client.post(path=reverse("account_login"), data=data)
        self.assertEqual(response.status_code, status.HTTP_302_FOUND)

    def prepare_tests_users(self, user_data: list[UserData]) -> None:
        self.disable_celery_execution()
        for user_info in user_data:
            new_user = self._add_user(username=user_info.get("username"),
                                      email=user_info.get("email"),
                                      password=user_info.get("password"),
                                      )
            user_info.update({"user_obj": new_user})
            APIKeysUtils.generate_api_key_for_user(user=new_user)
        return None

    def prepare_tests_api_client(self):
        self.api_client = APIClient()

    def prepare_tests_client(self):
        self.client = Client()

    @staticmethod
    def _add_user(username: str, email: str, password: str) -> User:
        return User.objects.create_user(username=username, email=email, password=password)

    @staticmethod
    def add_api_key_for_user(user: User) -> APIKey:
        return APIKeysUtils.generate_api_key_for_user(user=user)

    @classmethod
    def disable_celery_execution(cls):
        settings.CELERY_ALWAYS_EAGER = mock.Mock()
        settings.CELERY_ALWAYS_EAGER.return_value = True

    def _test_ping(self):
        result = self.client.get(reverse("ping"), follow=True)
        self.assertEqual(result.status_code, status.HTTP_200_OK)

    @staticmethod
    def _get_api_keys() -> QuerySet[APIKey]:
        return APIKey.objects.all()

    @staticmethod
    def _get_auth_header_for_api_key(api_key: APIKey) -> dict:
        return {"Token": api_key.api_key}

    def _make_mock_for_rabbit_send_message(self):
        patcher = mock.patch(f"common.utils.rabbit_mq.RabbitMQ.send_message_to_rabbit_mq")
        self.mock = patcher.start()
        self.mock.return_value = None
        self.addCleanup(patcher.stop)

    def _check_django_messages(self, response, expected_len: int, msg_str: str, msg_level):
        messages_in = list(messages.get_messages(response.wsgi_request))
        self.assertEqual(len(messages_in), expected_len)  # First one can be Login, or something else
        self.assertEqual(str(messages_in[expected_len - 1]), msg_str)  # ... so we check only latest ones
        self.assertEqual(messages_in[expected_len - 1].level, msg_level)

    @staticmethod
    def _get_mocked_image():
        import tempfile
        return tempfile.NamedTemporaryFile(suffix=".jpg").name

    def _make_mock_set_value_from_cache(self) -> None:
        patcher = mock.patch(f"ai_models.utils.queue.QueueManager.set_up_last_date_time_ai_image_generated")
        self._mock_set_value_from_cache = patcher.start()
        self.addCleanup(self._mock_set_value_from_cache.stop)

    def _make_mock_get_value_from_cache(self, value: datetime.datetime = None) -> None:
        patcher = mock.patch(f"ai_models.utils.queue.QueueManager.get_last_date_time_ai_image_generated")
        self._mock_get_value_from_cache = patcher.start()
        self._mock_get_value_from_cache.return_value = value
        self.addCleanup(self._mock_get_value_from_cache.stop)

    # @staticmethod
    # def _add_testing_model_and_model_author(author: str, model_name: str) -> AIModel:
    #     author_model_params = {"name": author}
    #     author_model_obj = AIModelsUtils.add_author_model(author_model_params)
    #     model_params = {"name": model_name,
    #                     "author": author_model_obj,
    #                     "type": ModelType.CHAT,
    #                     }
    #     return AIModelsUtils.add_model(model_params)

    def _init_problem(self, problem_params: ProblemTypeMinimum) -> "Problem":
        model_name = "Mistral-7B-OpenOrca"
        author = "Open-Orca"
        self.ai_model = "Open-Orca/Mistral-7B-OpenOrca"
        self.intro_msg_1 = "### System Prompt"
        # self.intro_msg_2 = f"You are {problem_params.get('name')}, an uncensored and unbiased sexy-partner!."
        # self.instructions_for_ai = "Reply to user input with..."
        self.user_msg_title = "### User Message"
        self.ai_msg_title = f"### {problem_params.get('name')}"
        problem = ProblemManager.create_problem(params=problem_params)
        return problem

    def _init_room(self, problem: "Problem") -> Room:
        room = RoomUtils.get_or_crate_user_room(user=self.user2["user_obj"],
                                                problem=problem,
                                                )
        return room

    def _turn_on_mock_init_ai_chat_provider(self):
        patcher = mock.patch(f"chats.utils.ai_chatter.AIChatter._init_ai_chat_provider_with_params")
        self._mock_ai_chat_provider = patcher.start()
        self.addCleanup(self._mock_ai_chat_provider.stop)

    def _turn_on_mock_execute_chatter(self):
        patcher = mock.patch(f"chats.utils.ai_chatter.AIChatter.execute_all_prompt")
        self._mock_execute_all_prompt = patcher.start()
        self.addCleanup(self._mock_execute_all_prompt.stop)

    def _create_problem(self) -> "Problem":
        problem_name = "Jennifer"
        problem_params: ProblemTypeMinimum = {
            "author": self.user1["user_obj"],
            "name": problem_name,
            "country": "US",
            "age": 18,
            }
        return self._init_problem(problem_params=problem_params)

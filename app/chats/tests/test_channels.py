import json
from unittest import mock

from channels.db import database_sync_to_async
from channels.testing import WebsocketCommunicator
from django.test import tag, TransactionTestCase

from api_keys.models import APIKey
from api_keys.utils import APIKeysUtils
from chats.utils.room import RoomUtils
from common.common_tests_utils import CommonTestCaseMixin
from config.asgi import application
from users.models import User


class AuthWebsocketCommunicator(WebsocketCommunicator):
    def __init__(self, application, path, headers=None, subprotocols=None, user=None):
        super(AuthWebsocketCommunicator, self).__init__(application, path, headers, subprotocols)
        if user is not None:
            self.scope['user'] = user


class WebsocketsProblemTestCase(CommonTestCaseMixin, TransactionTestCase):

    def setUp(self):
        self.pre_populate_couple_users()
        self.problem = self._create_problem()
        self.room = self._init_room(self.problem)
        self._turn_on_mock_init_ai_chat_provider()
        self._turn_on_mock_execute_chatter()
        self._turn_on_mock_create_celery_task()

    async def _init_communicator(self, room_slug: str):
        communicator = AuthWebsocketCommunicator(application=application, path=f"chat/{room_slug}/", user=self.user2['user_obj'])
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)
        return communicator

    async def _send_websocket_message(
        self, communicator, msg: dict, expected_response: dict = None
        ):
        msg_to_send = json.dumps(msg)
        await communicator.send_to(text_data=msg_to_send)
        response = await communicator.receive_from()
        if not expected_response:
            self.assertEqual(response, msg_to_send)
        else:
            json_expected_response = json.dumps(expected_response)
            self.assertEqual(response, json_expected_response)

    @tag("inv2")
    async def test_websocket_send_message(self):
        communicator = await self._init_communicator(room_slug=self.room.slug)
        user_alias_name = RoomUtils.ME
        message_to_send = "Hello!"
        expected_response = {
            "message": "<div hx-swap-oob='beforeend:#messages'><li class='d-flex justify-content-auto mb-4 col-12 col-md-8' style='align-content: start;'>"
                       "                                                <img src='/assets/main/assets/images/unknown_user_avatar.png' alt='avatar'"
                       "                                                     class=' d-flex align-self-start me-3"
                       "                                                      shadow-1-strong'"
                       "                                                      width='60'>"
                       "                                                <div class='card mask-custom' id='message'>"
                       "                                                    <div class='card-header d-flex justify-content-between p-1'"
                       "                                                         style='border-bottom: 1px solid rgba(255,255,255,.3);'>"
                       "                                                        <p class='fw-bold m-1 me-5'>"
                       f"                                                            {user_alias_name}</p>"
                       "                                  "
                       "                  </div>                                                   "
                       " <div class='card-body'>                                                        "
                       "<p class='mb-0'>                                                            "
                       f"{message_to_send}                                                        "
                       "</p>                                                    </div>                                                "
                       "</div>                                            </li></div>",
            "username": RoomUtils.ME,
            }
        msg = {"HEADERS": {"HX-Request": True, "HX-Trigger": None, "HX-Trigger-Name": None, "HX-Target": None},
               "message": message_to_send,
               }
        await self._send_websocket_message(
            communicator=communicator,
            msg=msg,
            expected_response=expected_response,
            )
        self._mock_celery_task_creation.assert_called_once_with(user_input=message_to_send, room_id=self.room.id)
        await communicator.disconnect()
        api_key = await self._get_api_key(user=self.user2["user_obj"])
        self.assertEqual(api_key.attempts, 1)

    @database_sync_to_async
    def _get_api_key(self, user: User) -> APIKey:
        return APIKeysUtils.get_user_latest_api_key_obj(user=user)

    def _turn_on_mock_create_celery_task(self):
        patcher = mock.patch(f"chats.consumers.ChatConsumer.send_user_input_to_celery")
        self._mock_celery_task_creation = patcher.start()
        self.addCleanup(self._mock_celery_task_creation.stop)

import json

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from rest_framework import status

from chats.models import Room
from chats.utils.formatter import FormatterUtils
from chats.utils.room import RoomUtils
from common.utils.helpers import HelperUtils
from config.logger import get_module_logger

logger = get_module_logger("Consumers")


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_group_name = None
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            logger.error("User is not authenticated")
            await self.auth_failed_error()
            return
        self.user_id = self.user.id
        self.room_name = self.scope["url_route"]["kwargs"]["room_slug"]
        self.room_group_name = f"chat_{self.room_name}"
        try:
            self.room: Room = await self.get_user_room()
        except Room.DoesNotExist:
            logger.error("Unauthorized access")
            await self.auth_failed_error()
            return

        self.room_id = self.room.id

        await self.channel_layer.group_add(
            self.room_group_name, self.channel_name
            )

        logger.info(f"Accepting connection with scope: {self.scope}")
        await self.accept()

    async def auth_failed_error(self):
        await self.accept()
        await self.send_error_msg_to_client(
            "Not Authorized", error_code=status.HTTP_401_UNAUTHORIZED
            )
        await self.close()

    async def send_error_msg_to_client(self, error_str: str, error_code: int = None):
        error_code_to_show = error_code or status.HTTP_400_BAD_REQUEST

        await self.send(
            text_data=json.dumps(
                {
                    "error": {
                        "code": error_code_to_show,
                        "text": error_str,
                        }
                    }
                )
            )

    async def disconnect(self, close_code):
        if self.room_group_name:
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
                )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_text = text_data_json["message"]
        if not message_text:
            return
        final_text = FormatterUtils.convert_text_to_md(message_text)
        if not final_text or len(final_text) == 0:
            return
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": final_text,
                "username": RoomUtils.ME,
                "avatar_img_path": RoomUtils.get_unknown_user_avatar(),
                "snowflake_id": HelperUtils.generate_snowflake_id(),
                }
            )
        await sync_to_async(RoomUtils.send_user_input_to_celery)(user_input=message_text, room_id=self.room_id)

    async def chat_message(self, event):
        message = event["message"]
        username = event["username"]
        is_circled_avatar = False if username == RoomUtils.ME else True
        avatar_img_path = event["avatar_img_path"]
        snowflake_id = event.get("snowflake_id")
        date_time = event.get("date_time")
        without_new_lines = RoomUtils.get_chat_template_message(user_name=username,
                                                                message=message,
                                                                avatar_img_path=avatar_img_path,
                                                                is_avatar_circled=is_circled_avatar,
                                                                snowflake_id=snowflake_id,
                                                                date_time=date_time,
                                                                )

        message_html = f"<div hx-swap-oob='beforeend:#messages'>{without_new_lines}</div>"
        text_data = json.dumps(
            {
                "message": message_html,
                "snowflake_id": snowflake_id,
                "username": username,
                }
            )
        logger.info(f"Chat message: {text_data=}")
        await self.send(
            text_data=text_data
            )

    @database_sync_to_async
    def get_user_room(self) -> Room:
        logger.info(f"{self.room_name=}")
        logger.info(f"{self.user=}")
        return RoomUtils.get_user_room_by_slug(slug=self.room_name, user_id=self.user_id)

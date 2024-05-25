from celery import shared_task

from chats.utils.chat_listener import ChatListener
from chats.utils.room import RoomUtils
from users.models import User


@shared_task
def process_user_input(user_input: str, room_id: int, notification_id: int) -> int:
    return ChatListener.process_user_input(user_input=user_input,
                                           room_id=room_id,
                                           notification_id=notification_id,
                                           )


@shared_task
def read_all_messages_in_chat(message_snowflake_id: int, user_id: int) -> int:
    user = User.objects.get(id=user_id)
    return RoomUtils.read_all_messages_in_chat_with_snowflake_id(snowflake_id=message_snowflake_id,
                                                                 user=user,
                                                                 )

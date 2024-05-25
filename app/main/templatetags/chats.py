from django import template
from django.utils.safestring import mark_safe

from chats.consts import MessageRole
from chats.models import Message
from chats.utils.formatter import FormatterUtils
from chats.utils.room import RoomUtils

register = template.Library()


@register.filter
def chat_message_view(message: Message | None) -> str:
    if not message:
        return ""
    if message.role == MessageRole.SYSTEM.value:  # Additional check to not show this to user
        return ""
    if not (message.photo or message.message):
        return ""
    therapist_name = message.room.problem.therapist_name or "AI Therapist"
    user_name = RoomUtils.ME if message.role == MessageRole.USER.value else therapist_name
    is_avatar_circled = False if user_name == RoomUtils.ME else True
    avatar_img_url = RoomUtils.get_avatar_for_message(message=message)
    has_been_read = False if message.date_time_read is None else True
    message_text = RoomUtils.get_chat_template_message(user_name=user_name,
                                                       message=FormatterUtils.convert_text_to_md(message.message),
                                                       avatar_img_path=avatar_img_url,
                                                       is_avatar_circled=is_avatar_circled,
                                                       photo=message.photo,
                                                       date_time=message.created_at,
                                                       has_been_read=has_been_read,
                                                       snowflake_id=message.snowflake_id,
                                                       )
    return mark_safe(message_text)

import datetime
import random
import string

from PIL import Image
from django.core.files import File
from django.db.models import QuerySet
from django.template.defaultfilters import date
from django.templatetags.static import static
from django.utils.text import slugify

from chats.consts import MessageRole
from chats.models import Room, Message
from chats.utils.formatter import FormatterUtils
from common.utils.helpers import HelperUtils
from config.logger import get_module_logger
from problems.models import Problem
from users.models import User

logger = get_module_logger("RoomUtils")


class RoomUtils:
    ME = "You"

    @classmethod
    def get_or_crate_user_room(cls, user: User, problem: Problem) -> Room | None:
        user_room = cls.get_user_room(user=user, problem=problem)
        if not user_room:
            user_room = cls.create_room_for_user(user=user, problem=problem)
        return user_room

    @classmethod
    def create_room_for_user(cls, user: User, problem: Problem) -> Room:
        room_name = str(user.uuid)
        uid = str(''.join(random.choices(string.ascii_letters + string.digits, k=4)))
        room_slug = slugify(room_name + "_" + uid)
        user_room = Room.objects.create(name=room_name,
                                        slug=room_slug,
                                        user=user,
                                        problem=problem,
                                        )
        return user_room

    @classmethod
    def get_user_room(cls, user: User, problem: Problem) -> Room | None:
        if user.is_authenticated:
            return Room.objects.filter(user=user,
                                       problem=problem,
                                       ).first()
        return None

    @classmethod
    def get_room_messages(cls, room_id: int) -> Room | None:
        return Message.objects.prefetch_related("user", "room",
                                                ).filter(room_id=room_id,
                                                         role__in=(MessageRole.ASSISTANT.value,
                                                                   MessageRole.USER.value,
                                                                   ),
                                                         ).order_by("-created_at").all()[:30]

    @classmethod
    def get_chat_template_message(cls,
                                  user_name: str,
                                  message: str,
                                  avatar_img_path: str,
                                  is_avatar_circled: bool = True,
                                  photo: Image = None,
                                  date_time: datetime = None,
                                  has_been_read: bool = False,
                                  snowflake_id: str = "",
                                  ) -> str:
        # class_text = "rounded-circle" if is_avatar_circled else ""
        class_text = "rounded-3" if is_avatar_circled else ""
        has_been_read_icon = "<i class='text-info fa-solid fa-check-double'></i>" if has_been_read else "<i class='fa-solid fa-check'></i>"
        if not date_time:
            date_time = datetime.datetime.now()
        if not isinstance(date_time, str):
            date_time = date(date_time, "D d M H:i")
        message = cls.show_image_in_chat_message(image=photo) if photo else message
        message_pattern = f"""<li class='d-flex justify-content-auto mb-4 col-12 col-md-8' style='align-content: start;'>
                                                <div height='60'>
                                                    <img src='{avatar_img_path}' alt='avatar'
                                                         class='{class_text} d-flex align-self-start me-1 me-md-2 mt-1 
                                                     shadow-1-strong'
                                                         style='width: 60px; height: 60x; object-fit: cover;'
                                                         width='60'>
                                                </div>
                                                <div class='card mask-custom' id='message'>
                                                    <div class='card-header d-flex justify-content-between p-1'
                                                         style='border-bottom: 1px solid rgba(255,255,255,.3);'>
                                                        <p class='fw-bold m-1 me-5'>
                                                            <span id='msgid{snowflake_id}'>{has_been_read_icon}</span> {user_name}</p>
                                                    </div>
                                                    <div class='card-body p-2 p-md-3'>
                                                        <p class='mb-0'>
                                                            {message}
                                                        </p>
                                                        <p class='mb-2'>
                                                            <i>{date_time} UTC (GMT)</i>
                                                        </p>
                                                    </div>
                                                    <span id='{snowflake_id}'></span>
                                                </div>
                                            </li>"""
        without_new_lines = ''.join(message_pattern.splitlines())
        return without_new_lines

    @staticmethod
    def show_image_in_chat_message(image: Image) -> str:
        if image:
            return f"<a href='{image.url}' target='_blank'><img style='max-height: 450px;' src='{image.url}' alt='My Photo'></a>"
        return ""

    @classmethod
    def get_avatar_for_message(cls, message: Message | None):
        if not message:
            return cls._get_problem_unknown_avatar()
        if message.role == MessageRole.USER.value:
            return cls.get_unknown_user_avatar()
        return cls._get_problem_unknown_avatar()

    @staticmethod
    def _get_problem_unknown_avatar() -> str:
        return static("main/assets/images/Folded-Hands-300x300.png")

    @staticmethod
    def get_unknown_user_avatar() -> str:
        return static("main/assets/images/user_icon_1_256x256.png")

    @classmethod
    def get_avatar_for_api_key_out_of_limit(cls, room: Room):
        return cls._get_problem_unknown_avatar()

    @classmethod
    def get_user_room_by_slug(cls, slug: str, user_id: int) -> Room:
        return Room.objects.prefetch_related("user").get(slug=slug, user_id=user_id)

    @classmethod
    def get_room_by_id(cls, room_id: int) -> Room:
        return Room.objects.get(id=room_id)

    @classmethod
    def get_problem_name(cls, room: Room) -> str:
        return room.problem.problem_type

    @classmethod
    def add_a_message_to_room(cls,
                              room: "Room",
                              message: str | None,
                              user: User | None = None,
                              image_bytes: bytes = None,
                              problem_uuid: str = None,
                              role: MessageRole = None,
                              raw_message: str = None,
                              extra_data: list = None,
                              notification_id: int = None,
                              full_ai_response: dict = None,
                              ) -> Message:
        from notifications.utils.notification_manager import NotificationManager
        if not role:
            if user:
                role = MessageRole.USER
            else:
                role = MessageRole.ASSISTANT
        # If user is None = the message is from the Problem
        if raw_message:
            raw_message = raw_message.strip()
            raw_message = cls._remove_tabs_at_the_end_of_the_string(string=raw_message)
        if message:
            message = message.split("---")[0]
            message = cls._remove_ns_at_the_end_of_the_string(message)
            message = cls._remove_brackets_text(message)
        new_message_data = {"room_id": room.id,
                            "user": user,
                            "message": message,
                            "role": role.value,
                            "raw_message": raw_message,
                            "extra_data": extra_data,
                            "full_ai_response": full_ai_response,
                            }
        logger.info(f"Adding message: {new_message_data=}")
        message = Message.objects.create(**new_message_data)
        if image_bytes:
            image_name = cls._get_photo_message_name(room_id=room.id, problem_uuid=problem_uuid)
            message.photo.save(f"{image_name}.png", File(image_bytes))
        cls._updated_room_updated_at_field(room=room)
        if not notification_id:
            NotificationManager.add_task_to_send_notification_from_rabbit_mq(message=message)
        else:
            NotificationManager.set_up_message_obj_for_notification(notification_id=notification_id,
                                                                    message=message,
                                                                    )
        return message

    @classmethod
    def get_latest_message_in_the_room(cls, room: "Room") -> Message:
        return cls._get_latest_message_in_the_room_qs(room=room).first()

    @staticmethod
    def _get_latest_message_in_the_room_qs(room: "Room") -> QuerySet[Message]:
        return Message.objects.filter(room_id=room.id, role__in=[MessageRole.USER.value,
                                                                 MessageRole.ASSISTANT.value,
                                                                 ]
                                      ).order_by("-created_at")

    @classmethod
    def _updated_room_updated_at_field(cls, room: "Room"):
        room.updated_at = datetime.datetime.now()
        room.save(update_fields=["updated_at"])

    @classmethod
    def _remove_ns_at_the_end_of_the_string(cls, string: str) -> str:
        import re
        return re.sub('(\n)*$', '', string)

    @classmethod
    def _remove_tabs_at_the_end_of_the_string(cls, string: str) -> str:
        import re
        return re.sub('(\t)*$', '', string)

    @classmethod
    def _remove_brackets_text(cls, string: str) -> str:
        import re
        return re.sub("[\(\[].*?[\)\]]", "", string)

    @staticmethod
    def _get_photo_message_name(room_id: int, problem_uuid: str):
        return f"{str(room_id)}_{problem_uuid}_{HelperUtils.generate_snowflake_id()}"

    @classmethod
    def turn_off_image_generating_mode(cls, room: "Room"):
        room.is_image_generating = False
        room.save(update_fields=["is_image_generating"])

    @classmethod
    def turn_on_image_generating_mode(cls, room: "Room"):
        room.is_image_generating = True
        room.save(update_fields=["is_image_generating"])

    @classmethod
    def send_msg_to_websocket(cls,
                              room: "Room",
                              avatar_img_path: str,
                              response: str,
                              snowflake_id: str = None,
                              date_time: datetime = None,
                              ):
        if not date_time:
            date_time = datetime.datetime.now()
        date_time = date(date_time, "D d M H:i")
        date_time = str(date_time)
        if not snowflake_id:
            snowflake_id = ""
        # Send to Websockets
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        from asgiref.sync import async_to_sync
        room_chat_name = f"chat_{room.slug}"
        therapist_name = room.problem.therapist_name or "AI Therapist"
        msg = {
            "type": "chat_message",
            "message": FormatterUtils.convert_text_to_md(response),
            "username": therapist_name,
            "avatar_img_path": avatar_img_path,
            "snowflake_id": str(snowflake_id),
            "date_time": date_time,
            }
        async_to_sync(channel_layer.group_send)(room_chat_name, msg)

    @classmethod
    def read_all_messages_in_chat_with_snowflake_id(cls, snowflake_id: int, user: User) -> int | None:
        from chats.models import Message
        latest_message: Message = Message.objects.filter(snowflake_id=snowflake_id, room__user_id=user.id).first()
        if latest_message:
            updated_counter = Message.objects.filter(room=latest_message.room,
                                                     created_at__lte=latest_message.created_at,
                                                     date_time_read__isnull=True,
                                                     ).update(date_time_read=datetime.datetime.now())
            return updated_counter
        return None

    @staticmethod
    def get_timeout_based_on_message_length_in_seconds(message: str) -> int:
        return 2 + int(len(message) / 40)

    @staticmethod
    def get_message_obj_based_on_message_id(message_id: int) -> Message | None:
        return Message.objects.filter(id=message_id).first()

    @classmethod
    def get_message_before_message(cls, message: Message) -> Message | None:
        room = message.room
        return cls._get_latest_message_in_the_room_qs(room=room).exclude(id=message.id).first()

    @classmethod
    def send_user_input_to_celery(cls, user_input: str, room_id: int, notification_id: int = None):
        from chats.tasks import process_user_input
        kwargs = {"user_input": user_input, "room_id": room_id, "notification_id": notification_id}
        process_user_input.apply_async(kwargs=kwargs,
                                       queue="chats",
                                       )

    @classmethod
    def update_tries_to_get_the_answer_for_message(cls, message_obj: Message, tries_to_get_the_answer: int):
        message_obj.tries_to_get_the_answer = tries_to_get_the_answer
        message_obj.save(update_fields=["tries_to_get_the_answer",
                                        "updated_at",
                                        ]
                         )

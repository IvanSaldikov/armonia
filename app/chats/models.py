from django.db import models
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from chats.consts import MessageRole
from common.models import BaseModel
from common.utils.helpers import HelperUtils
from problems.models import Problem
from users.models import User


class Room(BaseModel):
    name = models.CharField(max_length=128)
    slug = models.SlugField(unique=True)
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='rooms',
                             )
    problem = models.ForeignKey(Problem,
                                verbose_name="Problem",
                                on_delete=models.CASCADE,
                                null=False,
                                blank=False,
                                related_name="rooms",
                                limit_choices_to={'is_active': True},
                                help_text="Problem, this room connected with",
                                )

    def __str__(self):
        return f"{self.user} + {self.problem.problem_type}"


class Message(BaseModel):
    room = models.ForeignKey(Room, related_name="messages", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             default=None,
                             null=True,
                             blank=True,
                             )
    message = models.TextField(null=True, blank=True, default=None)
    raw_message = models.TextField(null=True, blank=True, default=None)
    photo = models.ImageField(null=True, upload_to="messages_photos", blank=True, default=None)
    date_time_read = models.DateTimeField(default=None, null=True, blank=True)
    snowflake_id = models.BigIntegerField(null=True, blank=True)
    role = models.CharField(max_length=15,
                            null=False,
                            blank=False,
                            choices=MessageRole.choices(),
                            )
    extra_data = models.JSONField(default=None, null=True, blank=True)
    full_ai_response = models.JSONField(default=None, null=True, blank=True)
    tries_to_get_the_answer = models.IntegerField(default=None, null=True, blank=True)

    def __str__(self):
        user = "AI THERAPIST"
        if self.user is not None:
            user = str(self.user.id)
        message = str(self.message[:25]) if self.message else "*photo*"
        ret = (
            self.room.name + " - UserID: " +
            user + " : " + message
        )
        return ret

    @property
    def photo_src(self) -> str | None:
        if self.photo:
            return format_html(f'<a href="{self.photo.url}" target="_blank">'
                               f'<img src="{self.photo.url}" alt="Image" height="80px">'
                               f'</a>'
                               )
        return '-'

    @property
    def user_from(self) -> str | None:
        ret = "<span style='color: blue'>AI</span>" if not self.user else "<span style='color: red'>USER</span>"
        return mark_safe(ret)

    def save(self, **kwargs):
        self.snowflake_id = int(HelperUtils.generate_snowflake_id())
        super().save(**kwargs)

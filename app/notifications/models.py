import uuid

from django.core.validators import MinLengthValidator
from django.db import models

from chats.models import Message
from common.models import BaseModel
from users.models import User


class Notification(BaseModel):
    id = models.BigAutoField(primary_key=True)
    service_provider = models.ForeignKey("ServiceProvider",
                                         on_delete=models.DO_NOTHING,
                                         null=False,
                                         blank=False,
                                         related_name="notification",
                                         )
    is_sent = models.BooleanField(default=False, null=False, blank=False)
    data = models.JSONField(null=True, blank=True, default=None)
    message = models.OneToOneField(Message,
                                   on_delete=models.CASCADE,
                                   null=True,
                                   blank=True,
                                   related_name="notification",
                                   )
    date_sent = models.DateTimeField(null=True, blank=True)
    internal_message_id = models.IntegerField(null=True, blank=True)
    is_sent_by_user = models.BooleanField(verbose_name="Message was sent by user",
                                          null=False, blank=False, default=False,
                                          )

    def __str__(self):
        return f"Notification from Provider ID: `{self.service_provider_id}` about message {self.message}"

    class Meta:
        ordering = ("-created_at",)


class ServiceProvider(BaseModel):
    """It can be Telegram, Whatsapp, Email, Slack, Websocket etc"""
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=250,
                            null=False,
                            blank=False,
                            )
    is_active = models.BooleanField(default=False, null=False, blank=False)
    connection_link = models.URLField(max_length=350, default=None, null=True, blank=True)

    def __str__(self):
        return self.name


class NotificationConnection(BaseModel):
    """Connections between a User and a Service Provider"""

    id = models.BigAutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             null=True,
                             blank=False,
                             related_name="notification_connections",
                             limit_choices_to={'is_active': True},
                             )
    service_provider = models.ForeignKey("ServiceProvider",
                                         on_delete=models.CASCADE,
                                         null=False,
                                         blank=False,
                                         related_name="notification_connections",
                                         limit_choices_to={'is_active': True},
                                         )
    is_active = models.BooleanField(default=True, null=False, blank=False)
    data = models.JSONField(null=True, blank=True, default=None,
                            verbose_name="Additional user data",
                            )
    connection_number = models.CharField(max_length=16,
                                         null=True,
                                         blank=True,
                                         validators=[MinLengthValidator(10)],
                                         help_text="If a link (uuid) is not used, we can use "
                                                   "this code to find the connection record"
                                         )

    def __str__(self):
        return f"Notification connection between {self.user=} and {self.service_provider=}"

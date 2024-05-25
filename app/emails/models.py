from django.db import models

from common.models import BaseModel
from common.types import BaseEnum


class EmailServiceProvidersType(BaseEnum):
    Brevo = "Brevo"


class EmailMessage(BaseModel):
    id = models.BigAutoField(primary_key=True)
    email_provider = models.CharField(max_length=150, choices=EmailServiceProvidersType.choices(), default=EmailServiceProvidersType.Brevo)
    pre_sent_data = models.JSONField(null=True, default=None, blank=True)
    post_sent_data = models.JSONField(null=True, default=None, blank=True)
    date_sent = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Email message: {self.email_provider}. Is Sent {self.date_sent}"

from django.db import models

from common.models import BaseModel
from users.models import User


class Stat(BaseModel):
    metrics = models.JSONField(null=False, verbose_name="Metrics data itself")

    def __str__(self):
        return f"Metrics created at {self.created_at}"

from django_countries.fields import CountryField

from common.models import BaseModel
from django.db import models


class CountryExt(BaseModel):
    id = models.BigAutoField(primary_key=True)
    country = CountryField()
    is_priority = models.BooleanField(default=True, null=False, blank=False)
    denonym = models.CharField(max_length=255,
                               null=True,
                               blank=True,
                               default=None,
                               help_text="UK -> English, US -> American, etc")
    is_porn_legal = models.BooleanField(default=True, null=False, blank=False)

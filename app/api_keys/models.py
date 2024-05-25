from django.contrib.auth import get_user_model
from django.db import models
from django.utils.html import format_html

from api_keys.consts import MessagesLimit
from common.models import BaseModel


class APIKey(BaseModel):
    id = models.BigAutoField(primary_key=True)
    api_key = models.CharField(
        max_length=150,
        help_text="API Key",
        db_index=True,
        )
    usage_times = models.IntegerField(
        help_text="How many times this token was used",
        default=0,
        )
    usage_times_web = models.IntegerField(
        help_text="How many times this token was used via the Web interface",
        default=0,
        )
    attempts = models.IntegerField(
        help_text="How many times user started the job of running AI images",
        default=0,
        )
    usage_free_times_daily = models.IntegerField(
        help_text="How many times this token was used for free today",
        default=0,
        )
    usage_free_times_total = models.IntegerField(
        help_text="How many times this token was used for free",
        default=0,
        )
    usage_daily_first_date_time = models.DateTimeField(default=None, blank=True, null=True)  # This we need to understand when to set usage to 0
    user = models.ForeignKey(get_user_model(),
                             verbose_name="Who this API key belongs to",
                             on_delete=models.CASCADE,
                             null=False,
                             blank=False,
                             related_name="api_keys",
                             )
    premium_limit = models.IntegerField(help_text="How many times this API Key can be used for Premium models",
                                        null=True, blank=True, default=MessagesLimit.PremiumFree.value,
                                        )
    is_blocked = models.BooleanField(default=False, null=False, blank=False)
    is_super_model = models.BooleanField(default=True, null=False, blank=False,
                                         verbose_name="Use Super Premium Model",
                                         help_text="Super Model has significantly large context window and is very smart AI. "
                                                   "But Super Premium is much much more expensive than just premium model. If you really "
                                                   "need all powerful that AI has at the moment in the World you must use Super Premium model"
                                         )

    def __str__(self):
        return f"API Key for user: {self.user}: {self.api_key[:4]}******"

    def total_times_used(self):
        return self.usage_times + self.usage_times_web

    @property
    def user_country(self) -> str:
        return self.user.country_code.name

    @property
    def country_flag(self) -> str | None:
        if self.user.country_code:
            return format_html(f"<img src='{self.user.country_code.flag}' alt='{self.user.country_code.name}' title='{self.user.country_code.name}'>")
        return '-'

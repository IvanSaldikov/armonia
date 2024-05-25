import uuid

from django.core.validators import MinLengthValidator, MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.html import format_html
from django_countries.fields import CountryField

from common.models import BaseModel
from problems.consts import Gender, ProblemType
from users.models import User


class Problem(BaseModel):
    id = models.BigAutoField(primary_key=True)
    author = models.ForeignKey(User,
                               verbose_name="Author",
                               on_delete=models.SET_NULL,
                               null=True,
                               blank=True,
                               related_name="problems",
                               limit_choices_to={'is_active': True},
                               help_text="User, who added this problem to solve",
                               )
    problem_type = models.CharField(choices=ProblemType.name_values(),
                                    null=False, blank=False,
                                    verbose_name="📝 Problem Type",
                                    help_text="Short description of your problem you want to Solve with AI Therapist",
                                    )
    problem_description = models.TextField(null=False, blank=False, max_length=3000,
                                           verbose_name="Problem description",
                                           help_text="Describe the problem you want to solve with AI Therapist. "
                                                     "Don't worry about this much, you can add more details later in the chat "
                                                     "(different languages are supported - let's try your own language)",
                                           )
    user_age = models.IntegerField(default=None, null=True, blank=True,
                                   validators=[MinValueValidator(18), MaxValueValidator(80)],
                                   verbose_name="👶 Your Age",
                                   help_text="Tell us your age please to allow AI Therapist be able to provide more "
                                             "qualified help according the needs of each generation"
                                   )
    therapist_avatar = models.ImageField(null=True, upload_to="avatars", blank=True, default=None)
    therapist_name = models.CharField(max_length=100, unique=False,
                                      validators=[MinLengthValidator(3)],
                                      default=None, null=True, blank=True,
                                      verbose_name="👩‍⚕️ Therapist name",
                                      help_text="AI Therapist name you would like to call him/her with. Just for your comfort 🙏"
                                      )
    therapist_gender = models.CharField(choices=Gender.choices(),
                                        null=True, blank=True, default=None,
                                        help_text="Choose gender of your AI Therapist who your are comfortable "
                                                  "have conversation and share your thoughts with"
                                        )
    therapist_country = CountryField(default=None, null=True, blank=True,
                                     verbose_name="Therapist Country",
                                     help_text="You can choose country which Therapist are initially from "
                                               "to add some context to AI response when it's appropriate",
                                     )
    slug = models.SlugField(max_length=120, default="", null=False)
    is_active = models.BooleanField(default=True, null=False, blank=False)
    is_public = models.BooleanField(default=False, null=False, blank=False)
    is_solved = models.BooleanField(default=False, null=False, blank=False)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    is_premium = models.BooleanField(default=False, null=False, blank=False,
                                     verbose_name="👑 Premium AI Therapist",
                                     help_text="Use advanced and very clever model for AI Therapist (for paid plans only, 5 messages are free)"
                                     )

    def __str__(self):
        return f"Problem: {self.problem_type}. User: {self.author}. Public: {self.is_public}. Active: {self.is_active}"

    class Meta:
        verbose_name_plural = "Problems"

    @property
    def photo_src(self) -> str | None:
        if self.therapist_avatar:
            return format_html(f'<a href="{self.therapist_avatar.url}" target="_blank">'
                               f'<img src="{self.therapist_avatar.url}" alt="Image" height="80px">'
                               f'</a>'
                               )
        return '-'

    @property
    def country_flag(self) -> str | None:
        if self.therapist_country:
            return format_html(f"<img src='{self.therapist_country.flag}' alt='{self.therapist_country.name}' title='{self.therapist_country.name}'>")
        return '-'

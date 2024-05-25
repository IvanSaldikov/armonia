from django.conf import settings
from django.db.models import Count

from api_keys.consts import MessagesLimit
from api_keys.models import APIKey
from chats.models import Message
from problems.models import Problem
from users.models import User


class ServiceMetrics:
    @classmethod
    def total_users(cls) -> int:
        return User.objects.filter(is_superuser=False).count()

    @classmethod
    def users_with_messages(cls) -> int:
        return User.objects.annotate(message_count=Count("message")).filter(message_count__gt=0, is_superuser=settings.DEBUG).count()

    @classmethod
    def users_with_problems(cls) -> int:
        return User.objects.annotate(problems_count=Count("problems")).filter(problems_count__gt=0, is_superuser=settings.DEBUG).count()

    @classmethod
    def users_with_no_messages(cls) -> int:
        return User.objects.annotate(message_count=Count("message")).filter(message_count=0, is_superuser=settings.DEBUG).count()

    @classmethod
    def reached_maximum_messages(cls) -> int:
        count_1 = APIKey.objects.filter(usage_times_web=MessagesLimit.PremiumFree.value,
                                        user__is_superuser=settings.DEBUG,
                                        ).count()
        return count_1

    @classmethod
    def number_of_problems_not_public(cls):
        return Problem.objects.filter(is_public=False, is_active=True, author__is_superuser=settings.DEBUG).count()

    @classmethod
    def number_of_problems_public(cls):
        return Problem.objects.filter(is_public=True, is_active=True).count()

    @classmethod
    def number_of_users_messages(cls):
        return Message.objects.filter(user__isnull=False, user__is_superuser=settings.DEBUG).count()

    @classmethod
    def number_of_problem_messages_total(cls):
        return Message.objects.filter(user__isnull=True).count()

    @classmethod
    def number_of_problem_messages_text(cls):
        return Message.objects.filter(user__isnull=True, message__isnull=False).count()

    @classmethod
    def number_of_problem_messages_photo(cls):
        return Message.objects.filter(user__isnull=True, message__isnull=True).count()

    @classmethod
    def ratio_reached_per_signups(cls):
        total_users = cls.total_users()
        if total_users > 0:
            return round(cls.reached_maximum_messages() / total_users * 100, 1)
        return "--"

    @classmethod
    def ratio_at_least_one_message_users_to_signups(cls):
        total_users = cls.total_users()
        if total_users > 0:
            return round(cls.users_with_messages() / total_users * 100, 1)
        return "--"

    @classmethod
    def chat_satisfaction(cls):
        users_messages = cls.users_with_messages()
        if users_messages > 0:
            return round(cls.reached_maximum_messages() / users_messages * 100, 1)
        return "--"

    @classmethod
    def photos_to_text_messages_ratio(cls):
        text_messages = cls.number_of_problem_messages_text()
        if text_messages > 0:
            return round(cls.number_of_problem_messages_photo() / text_messages * 100, 1)
        return "--"

    @classmethod
    def custom_problems_to_total_users_with_messages_ratio(cls):
        total_users_with_messages = cls.users_with_messages()
        if total_users_with_messages > 0:
            return round(cls.users_with_problems() / total_users_with_messages * 100, 1)
        return "--"

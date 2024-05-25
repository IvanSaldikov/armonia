from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from import_export.admin import ImportExportMixin

from .models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("email",)


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ("email",)


@admin.register(User)
class CustomUserAdmin(ImportExportMixin, AuthUserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    list_display = (
        "email",
        "uuid",
        "country_flag",
        "country_code",
        "first_name",
        "last_name",
        "gender",
        "is_email_messages_allowed",
        "is_active",
        "is_staff",
        "is_connected_notifications",
        "last_login",
        "date_joined",
        "subscription_ends",
        "id",
        )
    list_filter = (
        "is_staff",
        "is_superuser",
        "is_active",
        )
    search_fields = ("email",)
    ordering = ("-date_joined",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Personal info",
            {
                "fields": (
                    "uuid",
                    "id",
                    "first_name",
                    "last_name",
                    "gender",
                    "country_code",
                    "birth_date",
                    "is_connected_notifications",
                    )
                },
            ),
        ("Permissions", {"fields": ("is_active",
                                    "is_staff",
                                    "is_superuser",
                                    )}),
        (
            "Important dates",
            {"fields": ("last_login", "date_joined", "subscription_ends")},
            ),
        )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2"),
                },
            ),
        )
    readonly_fields = (
        "id",
        "uuid",
        "last_login",
        "date_joined",
        )

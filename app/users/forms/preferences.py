from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

from users.models import User


class CountryFieldExt(CountryField):
    ...


class UserChooseCountryForm(forms.ModelForm):

    class Meta:
        model = User
        fields = ("is_country_related_content_enabled",
                  "country_code",
                  )
        widgets = {"country_code": CountrySelectWidget()}
        help_texts = {"country_code": "",
                      "is_country_related_content_enabled": "The AI content will be related to the country which you "
                                                            "select with this setting. If unchecked - a "
                                                            "country-neutral content will be generated"

                      }


class UserEmailNotificationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("is_email_messages_allowed",)

from django import forms

from api_keys.models import APIKey
from api_keys.utils import APIKeysUtils


class GenerateAPIKeyForm(forms.ModelForm):

    class Meta:
        model = APIKey
        fields = ()

    def save(self, commit=True):
        new_api_key: APIKey = super().save(commit=False)
        new_api_key.api_key = APIKeysUtils.generate_api_key_and_store_to_db()
        if commit:
            new_api_key.save()
        return new_api_key

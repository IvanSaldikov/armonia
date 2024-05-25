from api_keys.models import APIKey
from rest_framework import serializers


class APIKeySerializer(serializers.ModelSerializer):
    """API Keys"""

    class Meta:
        model = APIKey
        fields = [
            "api_key",
            "usage_times",
            "created_at",
            "updated_at",
            "id",
        ]


class RunGeneratingApiKeySerializer(serializers.Serializer):
    image_source_url = serializers.CharField(
        required=True,
        help_text="Image source URL",
        allow_blank=False,
    )
    prompt = serializers.CharField(
        required=True,
        help_text="Prompt",
        allow_blank=False,
    )

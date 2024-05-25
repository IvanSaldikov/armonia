from rest_framework import serializers


class PingSerializer(serializers.Serializer):
    status = serializers.CharField(help_text="Should be `ok`")

from rest_framework import serializers


class ChatReadMessages(serializers.Serializer):
    message_snowflake_id = serializers.IntegerField(required=True)

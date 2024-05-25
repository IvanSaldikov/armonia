from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from chats.tasks import read_all_messages_in_chat
from config.logger import get_module_logger
from .serializers import ChatReadMessages

logger = get_module_logger(__name__)


class ChatReadMessagesView(GenericViewSet):
    http_method_names = ["post"]
    lookup_field = "uuid"
    serializer_class = ChatReadMessages
    permission_classes = [IsAuthenticated]

    @action(methods=["POST"], detail=False)
    def read_all_messages(self, request):
        serializer: ChatReadMessages = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        message_snowflake_id = data["message_snowflake_id"]
        kwargs = {"message_snowflake_id": message_snowflake_id,
                  "user_id": request.user.id,
                  }
        read_all_messages_in_chat.apply_async(kwargs=kwargs,
                                              queue="other",
                                              )
        return Response(
            status=status.HTTP_200_OK,
            data={
                "success": True,
                },
            )

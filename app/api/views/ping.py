from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from api.permissions import ALLOW_ANY, IS_AUTHENTICATED
from api.serializers import PingSerializer
from config.logger import get_module_logger

logger = get_module_logger(__name__)


class PingView(GenericAPIView):
    permission_classes = [
        ALLOW_ANY,
        ]
    serializer_class = PingSerializer

    def get(self, request):
        data_in = {"status": "ok"}
        return Response(PingSerializer(data_in).data)

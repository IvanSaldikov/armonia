from typing import TypedDict

from chats.models import Message, Room
from common.types import BaseEnum
from config.logger import get_module_logger

logger = get_module_logger("AI Chatter General Interface")


class AIResponseType(BaseEnum):
    OK = "OK"


class ProcessUserInputResult(TypedDict):
    response: str
    status: AIResponseType
    message_obj: Message | None


class AIChatterInterface:
    def __init__(self, room: Room) -> None:
        self.room: Room = room

    def process_user_input(self, user_input: str, notification_id: int) -> ProcessUserInputResult:
        raise NotImplementedError

    def _get_model_to_use(self) -> str:
        raise NotImplementedError

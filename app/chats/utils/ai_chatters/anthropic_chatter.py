import os

from anthropic import Anthropic
from anthropic.types import Message
from django.db.models import QuerySet

from chats.consts import MessageRole
from chats.models import Room, Message as ChatMessage
from chats.utils.ai_chatters.interface import ProcessUserInputResult, AIResponseType, AIChatterInterface
from chats.utils.room import RoomUtils
from config.logger import get_module_logger
from problems.utils import ProblemManager

logger = get_module_logger("AI Chatter Anthropic")


class AnthropicChatter(AIChatterInterface):
    """https://console.anthropic.com/workbench/f8320278-97f7-47d9-b0b3-a7be2eaf28b9"""
    ADVANCED_MODEL_NAME = "claude-3-opus-20240229"
    MIDDLE_MODEL_NAME = "claude-3-sonnet-20240229"
    SIMPLE_MODEL_NAME = "claude-3-haiku-20240307"

    def __init__(self, room: Room) -> None:
        self.messages = []
        super().__init__(room)
        self._init_ai_client()
        self.current_model_to_use = self.SIMPLE_MODEL_NAME
        self._is_premium_model = False
        self._load_history_from_room()

    def _init_ai_client(self):
        ai_api_key = os.environ.get("ANTHROPIC_API_KEY", None)
        if not ai_api_key:
            raise Exception("Anthropic AI API key has not been set. Please set up this key via ANTHROPIC_API_KEY environment")
        self._ai_client = Anthropic(
            api_key=ai_api_key,
            )

    def _get_initial_instruct(self) -> str:
        problem = self.room.problem
        problem_extra_data = ProblemManager.get_extra_data_for_problem(problem=problem)
        init_msg = (
            f"You are a psychologist who helps the user with their issues. Your task, using different approaches from psychology, conduct therapy with the user so that he feels better. First of all you need to understand user issue, try to figure out what you need to solve the problem, plan the therapy and conduct it step by step after user's replies. {problem_extra_data}"
        )
        logger.info(init_msg)
        return init_msg

    def _load_history_from_room(self) -> None:
        all_chat_messages = self._get_messages()
        logger.info(f"========================")
        logger.info(f"Loading history from room {self.room.id}")
        for message in all_chat_messages:
            new_item = {
                "role": message.role,
                "content": message.message,
                }
            logger.info(f"{new_item=}")
            self.messages.append(new_item)

    def _get_messages(self) -> QuerySet[ChatMessage]:
        return self.room.messages.filter(room_id=self.room.id, message__isnull=False).order_by("created_at").all()

    def process_user_input(self, user_input: str, notification_id: int) -> ProcessUserInputResult | None:
        new_item_user = {
            "role": MessageRole.USER.value,
            "content": user_input,
            }
        self.messages.append(new_item_user)
        logger.info(f"User input was added {new_item_user=}")
        latest_message = RoomUtils.get_latest_message_in_the_room(room=self.room)
        if not latest_message or (latest_message and latest_message.role != MessageRole.USER.value):  # prevent adding user message to the chat room twice
            user_message_obj = RoomUtils.add_a_message_to_room(room=self.room,
                                                               role=MessageRole.USER,
                                                               message=user_input,
                                                               extra_data=self.messages,
                                                               notification_id=notification_id,
                                                               )
            if notification_id:  # It means that user has sent message from Telegram, so we need to sync with the Web Chat
                avatar_img_path = RoomUtils.get_avatar_for_message(message=user_message_obj)
                RoomUtils.send_msg_to_websocket(room=self.room,
                                                avatar_img_path=avatar_img_path,
                                                response=user_message_obj.message,
                                                snowflake_id=user_message_obj.snowflake_id,
                                                )
            ai_answer = self._get_ai_response()
            if not ai_answer:  # Sometimes there are errors happening
                return None
            assistant_text = ai_answer.content[0].text
            new_item = {
                "role": MessageRole.ASSISTANT.value,
                "content": assistant_text,
                }
            self.messages.append(new_item)
            message_obj = RoomUtils.add_a_message_to_room(room=self.room,
                                                          role=MessageRole.ASSISTANT,
                                                          message=assistant_text,
                                                          raw_message=assistant_text,
                                                          extra_data=self.messages,
                                                          full_ai_response=ai_answer.to_dict(),
                                                          )
            response_to_send = message_obj.message
        else:
            return None
        return {"response": response_to_send,
                "message_obj": message_obj,
                "status": AIResponseType.OK,
                }

    def _get_ai_response(self) -> Message:
        logger.info(f"=========================================")
        logger.info(f"-----------------------------------------")
        logger.info(f"Getting AI Response for {self.messages=}")
        model_name = self._get_model_to_use()
        logger.info(f"Model name to be used in this request {model_name=}, {self._is_premium_model=}")
        # Call the LLM with the JSON schema
        chat_completion = self._ai_client.messages.create(
            model=model_name,
            system=self._get_initial_instruct(),
            max_tokens=610,
            top_p=0.4,
            messages=self.messages,
            )
        resp = chat_completion.content[0].text
        logger.info(f"AI RESPONSE {resp=}")
        return chat_completion

    def _get_model_to_use(self) -> str:
        return self.current_model_to_use

    def set_premium_model(self, is_super_model: bool = True):
        if is_super_model:
            self.current_model_to_use = self.ADVANCED_MODEL_NAME  # When you will be ready
        else:
            self.current_model_to_use = self.MIDDLE_MODEL_NAME  # Cheaper but still okay
        self._is_premium_model = True

import json
import time

from allauth.utils import build_absolute_uri
from django.urls import reverse

from api_keys.exceptions import APIKeyExceededTotalLimit, APIKeyExceededDailyLimit
from api_keys.models import APIKey
from api_keys.utils import APIKeysUtils
from chats.models import Room
from chats.utils.ai_chatters.anthropic_chatter import AnthropicChatter
from chats.utils.ai_chatters.interface import ProcessUserInputResult
from chats.utils.room import RoomUtils
from common.utils.helpers import HelperUtils
from config.logger import get_module_logger

logger = get_module_logger("Chat Listener")


class ChatListener:

    @classmethod
    def process_user_input(cls, user_input: str, room_id: int, notification_id: int) -> int | None:
        logger.info(f"PROCESSING USER INPUT IN CHAT {room_id=} {user_input=}")
        room = RoomUtils.get_room_by_id(room_id=room_id)
        api_key_obj = APIKeysUtils.get_user_latest_api_key_obj(user=room.user)
        if not api_key_obj:
            return None
        try:
            cls.process_user_current_api_key(api_key_obj=api_key_obj)
        except APIKeyExceededTotalLimit:
            logger.info(f"API key Total exceeded for user {room.user}")
            if room.problem.is_premium:
                response_to_send = cls._get_api_key_total_limit_message()
                time.sleep(RoomUtils.get_timeout_based_on_message_length_in_seconds(message=response_to_send))  # To be able to pretend as a real user
                RoomUtils.send_msg_to_websocket(room=room,
                                                avatar_img_path=RoomUtils.get_avatar_for_api_key_out_of_limit(room=room),
                                                response=response_to_send,
                                                snowflake_id=HelperUtils.generate_snowflake_id(),
                                                date_time=HelperUtils.get_datetime_now(),
                                                )
                return None
        except APIKeyExceededDailyLimit:
            logger.info(f"API key Daily exceeded for user {room.user}")
            if not room.problem.is_premium:
                response_to_send = cls._get_api_key_daily_limit_message()
                time.sleep(RoomUtils.get_timeout_based_on_message_length_in_seconds(message=response_to_send))  # To be able to pretend as a real user
                RoomUtils.send_msg_to_websocket(room=room,
                                                avatar_img_path=RoomUtils.get_avatar_for_api_key_out_of_limit(room=room),
                                                response=response_to_send,
                                                snowflake_id=HelperUtils.generate_snowflake_id(),
                                                date_time=HelperUtils.get_datetime_now(),
                                                )
                return None

        response_result = cls._get_response_to_send_message(user_input=user_input,
                                                            room=room,
                                                            notification_id=notification_id,
                                                            is_super_model=api_key_obj.is_super_model,
                                                            )
        if not response_result:
            logger.error(f"PROCESSING USER INPUT IN CHAT {room_id=} {user_input=} RETURN NOT PROCESSED {response_result=}")
            return None
        if room.problem.is_premium:
            APIKeysUtils.increase_amount_of_usage_for_user_api_key_premium(api_key=api_key_obj)
        else:
            APIKeysUtils.increase_amount_of_usage_for_user_api_key_free(api_key=api_key_obj)
        message_obj = response_result["message_obj"]
        avatar_img_path = RoomUtils.get_avatar_for_message(message=message_obj)
        response_to_send = response_result["response"]
        time.sleep(RoomUtils.get_timeout_based_on_message_length_in_seconds(message=response_to_send))  # To be able to pretend as a real user
        RoomUtils.send_msg_to_websocket(room=room,
                                        avatar_img_path=avatar_img_path,
                                        response=response_to_send,
                                        snowflake_id=message_obj.snowflake_id,
                                        date_time=message_obj.created_at,
                                        )
        return message_obj.id

    @staticmethod
    def _get_response_to_send_message(room: Room,
                                      user_input: str,
                                      notification_id: int,
                                      is_super_model: bool,
                                      ) -> ProcessUserInputResult:
        response_result = None
        chatter = AnthropicChatter(room=room)
        if room.problem.is_premium:
            chatter.set_premium_model(is_super_model=is_super_model)

        shot_num = 0
        while response_result is None and shot_num <= 3:
            try:
                shot_num += 1
                logger.info(f"Trying to send AI request {shot_num=}...")
                response_result = chatter.process_user_input(user_input=user_input,
                                                             notification_id=notification_id,
                                                             )
                logger.info(f"...Trying to send AI request {shot_num=}... SUCCESS!!!")
                RoomUtils.update_tries_to_get_the_answer_for_message(message_obj=response_result["message_obj"],
                                                                     tries_to_get_the_answer=shot_num,
                                                                     )
            except json.decoder.JSONDecodeError as e:
                logger.info(f"...Trying to send AI request {shot_num=}... ERROR!!!")
                logger.warning(f"Error while loading response from AI {str(e)}")
                time.sleep(2)
        return response_result

    @classmethod
    def _get_api_key_total_limit_message(cls) -> str:
        return (f"Sorry, your API key has reached the limit for Premium AI Therapist. "
                f"You can purchase additional messages here: {cls.get_pricing_full_page_url()} or "
                f"continue using Free AI Therapist in your new Problems to solve "
                f"(just uncheck Is Premium AI Therapist when creating the problem to Solve)")

    @classmethod
    def _get_api_key_daily_limit_message(cls) -> str:
        return (f"Sorry, your API key has reached the daily limit for Free AI Therapist. "
                f"You can purchase additional messages here: {cls.get_pricing_full_page_url()} or "
                f"continue using Free AI Therapist next day in your Free Problems to solve "
                f"(just uncheck Is Premium AI Therapist when creating the problem to Solve)")

    @staticmethod
    def get_pricing_full_page_url():
        return build_absolute_uri(None, reverse('pricing'), protocol="https")

    @staticmethod
    def process_user_current_api_key(api_key_obj: APIKey) -> None:
        # API Keys verifying
        APIKeysUtils.increase_amount_of_attempts_for_user_api_key(api_key=api_key_obj)
        APIKeysUtils.verify_api_key(api_key=api_key_obj.api_key)

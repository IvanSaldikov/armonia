import random
from datetime import datetime


class HelperUtils:

    @staticmethod
    def generate_snowflake_id() -> str:
        from snowflake import SnowflakeGenerator

        instance_id = random.randint(1, 1022)
        snowflake_int = next(SnowflakeGenerator(instance_id))
        return str(snowflake_int)

    @staticmethod
    def get_datetime_now() -> datetime:
        return datetime.now()

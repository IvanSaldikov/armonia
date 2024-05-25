import re

from django.core.exceptions import ValidationError


class ContactLinksValidator:
    SUPPORTED_SERVICES_LIST = {
        "telegram": {
            "domain": "t.me",
            "min": 6,
            "max": 33,
            "profile_link_pattern": "https://t.me/<nickname>",
        },
        "linkedin": {
            "domain": "linkedin.com/in",
            "min": 3,
            "max": 100,
            "profile_link_pattern": "https://linkedin.com/in/<nickname>",
        },
        "instagram": {
            "domain": "instagram.com",
            "min": 1,
            "max": 30,
            "profile_link_pattern": "https://instagram.com/<nickname>",
        },
        "twitter": {
            "domain": "twitter.com",
            "min": 4,
            "max": 15,
            "profile_link_pattern": "https://twitter.com/<nickname>",
        },
        "facebook": {
            "domain": "facebook.com",
            "min": 1,
            "max": 30,
            "profile_link_pattern": "https://facebook.com/<nickname>",
        },
        "tiktok": {
            "domain": "tiktok.com/@",
            "min": 1,
            "max": 24,
            "profile_link_pattern": "https://tiktok.com/@<nickname>",
        },
        "_generic": {
            "domain": "[-a-zA-Z0-9@:%._\\+~#=]{1,256}\\.[a-zA-Z0-9()]{1,6}",
            "min": 1,
            "max": 150,
            "profile_link_pattern": "https://<domain>/<nickname>",
        },
    }

    @classmethod
    def get_telegram_url_validator(cls, value: str):
        return cls._get_url_validator(value=value, service_id="telegram")

    @classmethod
    def get_linkedin_url_validator(cls, value: str):
        return cls._get_url_validator(value=value, service_id="linkedin")

    @classmethod
    def get_instagram_url_validator(cls, value: str):
        return cls._get_url_validator(value=value, service_id="instagram")

    @classmethod
    def get_twitter_url_validator(cls, value: str):
        return cls._get_url_validator(value=value, service_id="twitter")

    @classmethod
    def get_facebook_url_validator(cls, value: str):
        return cls._get_url_validator(value=value, service_id="facebook")

    @classmethod
    def get_tiktok_url_validator(cls, value: str):
        return cls._get_url_validator(value=value, service_id="tiktok")

    @classmethod
    def get_url_validator(cls, value: str):
        return cls._get_url_validator(value=value, service_id="_generic")

    @classmethod
    def _get_url_validator(cls, value: str, service_id: str):
        pattern_str = cls._get_url_pattern(service_id=service_id)
        if not pattern_str:
            return None
        data = cls.SUPPORTED_SERVICES_LIST[service_id]
        msg = (
            f"REGEX_INVALID|{data['profile_link_pattern']}|{data['min']}|{data['max']}"
        )
        regex_matches = re.match(pattern_str, value)
        if not regex_matches:
            raise ValidationError(msg, params={"value": value})

    @classmethod
    def _get_url_pattern(cls, service_id: str):
        data = cls.SUPPORTED_SERVICES_LIST.get(service_id)
        if not data:
            return None
        min_nickname_length = data["min"]
        max_nickname_length = data["max"]
        url_address = data["domain"]
        return cls._get_url_pattern_generic(
            min_nickname_length=min_nickname_length,
            max_nickname_length=max_nickname_length,
            url_address=url_address,
        )

    @staticmethod
    def _get_url_pattern_generic(
        min_nickname_length: int, max_nickname_length: int, url_address: str
    ) -> str:
        url_address = url_address.replace(".", "\\.")
        url_address = url_address.replace("/", "\\/")
        url_ptrn = "^https?:\\/\\/(?:www\\.)?"
        url_ptrn += url_address
        url_ptrn += "\\b(?:[-a-zA-Z0-9()@:%_\\+.~#?&\\/=]"
        url_ptrn += f"{{{min_nickname_length + 1},{max_nickname_length + 1}}})$"
        return url_ptrn

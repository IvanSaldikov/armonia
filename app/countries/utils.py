from django.conf import settings
from django_countries.fields import Country

from config.logger import get_module_logger
from countries.consts.nationalities import NATIONALITIES

logger = get_module_logger("country_utils")


class CountriesUtils:
    DEFAULT_COUNTRY = "XX"  # International
    SESSION_KEY = "country_code"

    @classmethod
    def set_and_get_default_country_code(cls, request) -> str:
        if request.user.is_authenticated:
            return cls._set_and_get_lang_from_user_profile(request=request)
        else:
            return cls.set_and_get_lang_in_session(request=request)

    @classmethod
    def _set_and_get_lang_from_user_profile(cls, request) -> str:
        if not request.user.country_code:
            request.user.country_code = cls.set_and_get_lang_in_session(request)
            request.user.save(update_fields=["country_code"])
        if request.user.country_code and cls._get_lang_from_session(request) in (None, CountriesUtils.DEFAULT_COUNTRY):
            cls.set_lang_into_session(request=request,
                                      value=str(request.user.country_code),
                                      )
        return request.user.country_code

    @classmethod
    def set_and_get_lang_in_session(cls, request):
        # Get Default Country code from external service
        # Put it into session
        if not cls._get_lang_from_session(request):
            cls.set_lang_into_session(request=request, value=cls._get_country_based_on_ip(request))
        return cls._get_lang_from_session(request)

    @classmethod
    def _get_lang_from_session(cls, request):
        return request.session.get(cls.SESSION_KEY)

    @classmethod
    def set_lang_into_session(cls, request, value):
        request.session[cls.SESSION_KEY] = value

    @classmethod
    def _get_country_based_on_ip(cls, request) -> str:
        client_ip = cls._get_client_ip(request)
        if client_ip in {"127.0.0.1",
                         }:
            return cls.DEFAULT_COUNTRY
        logger.info(f'Getting Geo data for {client_ip}')
        country_code = cls._get_country_code_based_on_ip(ip_address=client_ip)
        logger.info(f"Got the data for this ip address: {client_ip}: {country_code=}")
        return country_code or cls.DEFAULT_COUNTRY

    @classmethod
    def _get_country_code_based_on_ip(cls, ip_address: str) -> str | None:
        import maxminddb
        geo_data_file = cls._get_mmdb_data_file_location()
        with maxminddb.open_database(geo_data_file) as reader:
            response = reader.get(ip_address)
            if response:
                country_code = response.get("country")
            else:
                country_code = None
        return country_code

    @staticmethod
    def _get_mmdb_data_file_location() -> str:
        return settings.ARMONIA_GEO_DATA_FILE_LOCATION

    @staticmethod
    def _get_client_ip(request) -> str:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    @classmethod
    def get_demonym_from_country_obj(cls, country_obj: Country) -> str:
        return NATIONALITIES.get(country_obj.code, {}).get("nationality", "")

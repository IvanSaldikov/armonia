from allauth.core import context
from allauth.core.exceptions import ImmediateHttpResponse

from countries.utils import CountriesUtils


class CountryMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        with context.request_context(request):
            CountriesUtils.set_and_get_default_country_code(request)
            response = self.get_response(request)
            return response

    def process_exception(self, request, exception):
        if isinstance(exception, ImmediateHttpResponse):
            return exception.response

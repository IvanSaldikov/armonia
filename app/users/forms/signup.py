from allauth.account.forms import SignupForm
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Invisible

from api_keys.utils import APIKeysUtils
from countries.utils import CountriesUtils


def common_custom_signup_func(request, user):
    user.country_code = CountriesUtils.set_and_get_lang_in_session(request=request)
    APIKeysUtils.generate_api_key_for_user(user=user)


class TunedSignupForm(SignupForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Invisible, label="")

    def custom_signup(self, request, user):
        common_custom_signup_func(request=request, user=user)
        self.signup(request, user)


class TunedSocialSignupForm(SocialSignupForm):

    def custom_signup(self, request, user):
        common_custom_signup_func(request=request, user=user)
        self.signup(request, user)

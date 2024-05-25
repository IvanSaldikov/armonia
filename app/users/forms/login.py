from allauth.account.forms import LoginForm
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Invisible


class TunedLoginForm(LoginForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Invisible, label="")

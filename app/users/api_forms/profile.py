from allauth.account.adapter import get_adapter
from allauth.account.forms import default_token_generator
from allauth.utils import build_absolute_uri
from dj_rest_auth.forms import AllAuthPasswordResetForm
from django.contrib.sites.shortcuts import get_current_site


class ResetPasswordFormExt(AllAuthPasswordResetForm):
    def save(self, request, **kwargs):
        current_site = get_current_site(request)
        email = self.cleaned_data["email"]
        token_generator = kwargs.get("token_generator", default_token_generator)

        for user in self.users:

            token = token_generator.make_token(user)

            # send the password reset email
            path = f"/reset-password?uid={user.uuid}&token={token}"

            url = build_absolute_uri(None, path, protocol="https")

            context = {
                "current_site": current_site,
                "user": user,
                "password_reset_url": url,
                "request": request,
                "use_https": True,
            }
            get_adapter(request).send_mail(
                "account/email/password_reset_key", email, context
            )
        return self.cleaned_data["email"]

from dj_rest_auth.serializers import PasswordResetSerializer
from users.api_forms.profile import ResetPasswordFormExt


class PasswordResetSerializerExt(PasswordResetSerializer):
    @property
    def password_reset_form_class(self):
        """Override the method to return our custom form"""
        return ResetPasswordFormExt

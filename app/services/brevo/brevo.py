from __future__ import print_function

from pprint import pprint
from typing import TypedDict

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

from config.logger import get_module_logger

logger = get_module_logger("BrevoService")


class EmailUserInfo(TypedDict):
    email: str
    name: str


class BrevoService:
    # DOCS: https://developers.brevo.com/docs/send-a-transactional-email

    def __init__(self, api_key: str):
        if not api_key:
            logger.error("BrevoService is not initializer")
        self.api_key = api_key

    def send_email_based_on_template(self,
                                     user: EmailUserInfo,
                                     template_id: int,
                                     additional_params: dict,
                                     ):
        if not self.api_key:
            return

        # Configure API key authorization: api-key
        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key['api-key'] = self.api_key

        # create an instance of the API class
        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=[user],
                                                       template_id=template_id,
                                                       params=additional_params,
                                                       )

        try:
            # Send a transactional email
            api_response = api_instance.send_transac_email(send_smtp_email)
            pprint(api_response)
        except ApiException as e:
            print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)

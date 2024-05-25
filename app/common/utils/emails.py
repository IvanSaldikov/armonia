from users.models import User


class EmailUtils:
    @staticmethod
    def get_email_body_footer() -> str:
        return """Cheers,
    Armonia.day Website
    Help: i@armonia.day
    Website: https://armonia.day
    Contact email for any question: i@armonia.day
    ---------
    You're receiving this message because your email was entered as a contact email
    by you at Armonia.day website. If it was by mistake, please just ignore it.
    ---------
    To know more about our Privacy policy please visit our main page to get the link:
    https://armonia.day
            """

    @staticmethod
    def get_dear_str(user: User) -> str:
        dear_str = "Hello!"
        if user.first_name:
            dear_str = f"Hello, {user.first_name}!"
        return dear_str

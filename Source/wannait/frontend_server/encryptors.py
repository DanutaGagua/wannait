from django.contrib.auth.tokens import PasswordResetTokenGenerator
from urllib3.packages import six


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (six.text_type(user.username) +
                six.text_type(timestamp))


account_activation_token = TokenGenerator()

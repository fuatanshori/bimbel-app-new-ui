from django.contrib.auth.tokens import PasswordResetTokenGenerator


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        aktifasi_timestamp = (
            ""
            if user.waktu_aktifasi is None
            else user.waktu_aktifasi.replace(microsecond=0, tzinfo=None)
        )
        email_field = user.get_email_field_name()
        email = getattr(user, email_field, "") or ""
        return f"{user.pk}{user.password}{user.is_active}{aktifasi_timestamp}{timestamp}{email}"


account_activation_token = TokenGenerator()

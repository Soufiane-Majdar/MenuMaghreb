from django.core.mail.backends.smtp import EmailBackend
from django.conf import settings

class CustomEmailBackend(EmailBackend):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('host', settings.EMAIL_HOST)
        kwargs.setdefault('port', settings.EMAIL_PORT)
        kwargs.setdefault('username', settings.EMAIL_HOST_USER)
        kwargs.setdefault('password', settings.EMAIL_HOST_PASSWORD)
        kwargs.setdefault('use_tls', settings.EMAIL_USE_TLS)
        super().__init__(*args, **kwargs)

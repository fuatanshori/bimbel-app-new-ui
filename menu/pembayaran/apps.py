from django.apps import AppConfig


class PembayaranConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'menu.pembayaran'

    def ready(self) -> None:
        from . import signals
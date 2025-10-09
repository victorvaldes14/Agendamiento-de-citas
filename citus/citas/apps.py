from django.apps import AppConfig


class CitasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'citas'

    def ready(self):
        # Importa las señales al arrancar la app
        from . import signals  # noqa: F401

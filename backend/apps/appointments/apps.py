from django.apps import AppConfig


class AppointmentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.appointments'
    verbose_name = 'Gestion des Rendez-vous'

    def ready(self):
        import apps.appointments.signals

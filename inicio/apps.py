from django.apps import AppConfig


class InicioConfig(AppConfig):
    name = 'inicio'
    
    def ready(self):
        """Registrar signals cuando la app esté lista"""
        import inicio.signals

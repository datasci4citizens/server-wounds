from django.apps import AppConfig


class AppCicatrizandoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app_cicatrizando'
    
    def ready(self):
        try:
            import app_cicatrizando.models_omop
        except ImportError:
            pass

from django.apps import AppConfig


class MonitoringConfig(AppConfig):
    name = "monitoring"
    # auto add ID if not added
    default_auto_field = "django.db.models.BigAutoField"

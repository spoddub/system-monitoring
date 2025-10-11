from django.apps import AppConfig


class MonitoringConfig(AppConfig):
    name = "system_monitoring"
    # auto add ID if not added
    default_auto_field = "django.db.models.BigAutoField"

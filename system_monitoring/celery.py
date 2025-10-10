from celery import Celery


app = Celery("system_monitoring")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

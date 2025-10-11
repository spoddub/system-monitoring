import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "system_monitoring.settings")

app = Celery("system_monitoring")
# ищет все что начинается с CELERY
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

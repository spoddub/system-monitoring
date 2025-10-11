from celery import Celery

app = Celery("system_monitoring")
# ищет все что начинается с CELERY
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "saas_starter.settings.development")

app = Celery("saas_starter")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

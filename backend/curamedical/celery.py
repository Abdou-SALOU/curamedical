import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'curamedical.settings')

app = Celery('curamedical')
# Toutes les options CELERY_* viennent de settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')
# Découvre automatiquement les tasks.py de chaque app installée
app.autodiscover_tasks()

from __future__ import absolute_import
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", 
                      "config.settings")

app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY") 

app.conf.broker_connection_retry_on_startup = True
app.conf.broker_connection_max_retries = 10
app.conf.broker_connection_retry = True
app.conf.broker_pool_limit = None

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

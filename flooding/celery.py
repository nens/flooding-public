from __future__ import print_function
from __future__ import absolute_import

import os

from celery import Celery

# Set the default Django settings module for the 'celery' program, if it's not
# set yet.
#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flooding.developmentsettings')

app = Celery('flooding')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Don't autodiscover tasks, we use CELERY_IMPORTS because we have lizard-worker
# tasks too. The tasks are in flooding_lib/celery_tasks.py.
#app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print('Request: ', repr(self.request))

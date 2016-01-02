from __future__ import absolute_import
from kombu import Queue, Exchange

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'myproject.settings'

from celery import Celery
from datetime import timedelta

app = Celery(
    'Hiryu',
    broker='redis://',
    backend='redis://',
    include=[
        'Hiryu.tasks',
    ])

app.conf.update(
    CELERY_DEFAULT_QUEUE = 'hiryu',
    CELERY_QUEUES = (
        Queue('hiryu', Exchange('hiryu'), routing_key='hiryu'),
    ),
    #CELERY_IGNORE_RESULT = True,
    CELERY_TASK_RESULT_EXPIRES = 600,
    #CELERY_MAX_CACHED_RESULTS = -1,
    CELERY_MAX_TASKS_PER_CHILD = 1,
    CELERYD_TASK_TIME_LIMIT = 600,
    CELERY_ACCEPT_CONTENT = ['json', 'pickle'],
    CELERY_TASK_SERIALIZER = 'pickle',
    CELERY_RESULT_SERIALIZER = 'pickle',
)

if __name__ == '__main__':
    app.start()



from __future__ import absolute_import

import os

import celery
print celery.__file__

from celery import Celery

from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Atypidae.settings')

Atyp = Celery('Atypidae')
#     backend='cache+memcached://127.0.0.1:11211/',
#     broker='amqp://guest@localhost/'
# )

# Using a string here means the worker will not have to
# pickle the object when using Windows.
Atyp.config_from_object('django.conf:settings')
Atyp.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


# @Atyp.task(bind=True)
# def debug_task(self):
#     print('Request: {0!r}'.format(self.request))

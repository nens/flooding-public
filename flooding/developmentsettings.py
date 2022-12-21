from __future__ import print_function

from flooding.settings import *  # NOQA

INTERNAL_IPS = ('127.0.0.1',)

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'HOST': 'db',
        'PORT': 5432,  # Mapnik requires an explicit port number
        'NAME': 'flooding',
        'USER': 'flooding',
        'PASSWORD': 'flooding',
    }
}

BROKER_SETTINGS = {
    "BROKER_HOST": "rabbit",
    "BROKER_PORT": 5672,
    "BROKER_USER": "flooding",
    "BROKER_PASSWORD": "flooding",
    "BROKER_VHOST": "flooding",
    "HEARTBEAT": False
}

BROKER_URL = 'amqp://%s:%s@%s:%d/%s' % (
    BROKER_SETTINGS['BROKER_USER'],
    BROKER_SETTINGS['BROKER_PASSWORD'],
    BROKER_SETTINGS['BROKER_HOST'],
    BROKER_SETTINGS['BROKER_PORT'],
    BROKER_SETTINGS['BROKER_VHOST']
)

CELERY_BROKER_URL = BROKER_URL
RASTER_SERVER_URL = 'http://127.0.0.1:5000/wms'

RAVEN_CONFIG = {
}

TMP_ROOT = '/tmp'

try:
    from flooding.localdevelopmentsettings import *  # NOQA
except ImportError:
    pass

from flooding.settings import *  # NOQA

# this is a developmentsettings copy, refer to localstagingsettings.py
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

RASTER_SERVER_URL = "http://flooding.staging.lizard.net/wms"

RAVEN_CONFIG = {
}

try:
    from flooding.localstagingsettings import *  # NOQA
except ImportError:
    pass

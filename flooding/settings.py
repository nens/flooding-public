# Base Django settings, suitable for production.  Imported (and partly
# overridden) by developmentsettings.py which also imports
# localsettings.py (which isn't stored in svn).
# Build19890150.1534fout takes care of using the correct one.  So:
# "DEBUG = TRUE" goes into developmentsettings.py and per-developer
# database ports go into localsettings.py.  May your hear turn purple
# if you ever put personal settings into this file or into
# developmentsettings.py!

import logging
import os
import tempfile
import pkg_resources
import matplotlib
matplotlib.use('Agg')

import sys
try:
    import PIL.Image
    sys.modules['Image'] = PIL.Image
except ImportError:
    import Image

from logging.handlers import RotatingFileHandler

# SETTINGS_DIR allows media paths and so to be relative to this settings file
# instead of hardcoded to c:\only\on\my\computer.
SETTINGS_DIR = os.path.dirname(os.path.realpath(__file__))

# BUILDOUT_DIR is for access to the "surrounding" buildout, for instance for
# BUILDOUT_DIR/var/media files to give django-staticfiles a proper place
# to place all collected static files.
BUILDOUT_DIR = os.path.abspath(os.path.join(SETTINGS_DIR, '..'))

# Downloadable Excel files
EXCEL_DIRECTORY = os.path.join(BUILDOUT_DIR, "var", "excel")

# Triple blast.  Needed to get matplotlib from barfing on the server: it needs
# to be able to write to some directory.
if 'MPLCONFIGDIR' not in os.environ:
    os.environ['MPLCONFIGDIR'] = tempfile.gettempdir()

# Production, so DEBUG is False. developmentsettings.py sets it to True.
DEBUG = False

# ADMINS get internal error mails, MANAGERS get 404 mails.
ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)
MANAGERS = ADMINS

# this is a developmentsettings copy, refer to localstagingsettings
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

# Almost always set to 1.  Django allows multiple sites in one database.
SITE_ID = 1

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name although not all
# choices may be available on all operating systems.  If running in a Windows
# environment this must be set to the same as your system time zone.
TIME_ZONE = 'Europe/Amsterdam'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'nl'
# For at-runtime language switching.  Note: they're shown in reverse order in
# the interface!
ugettext = lambda s: s

LANGUAGES = (
    ('nl', ugettext('Nederlands')),
    ('en', ugettext('English')),
)

LOCALE_PATHS = (os.path.join(BUILDOUT_DIR, 'src', 'flooding-lib', 'flooding_lib', 'locale'),)
# If you set this to False, Django will make some optimizations so as not to
# load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds user-uploaded media.
MEDIA_ROOT = os.path.join(BUILDOUT_DIR, 'var', 'media')
# Absolute path to the directory where django-staticfiles'
# "bin/django build_static" places all collected static files from all
# applications' /media directory.
STATIC_ROOT = os.path.join(BUILDOUT_DIR, 'var', 'static')

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    # Enable support for django-compressor.
    'compressor.finders.CompressorFinder',
    )

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
MEDIA_URL = '/media/'
# URL for the per-application /media static files collected by
# django-staticfiles.  Use it in templates like
# "{{ MEDIA_URL }}mypackage/my.css".
STATIC_URL = '/static_media/'
# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.  Uses STATIC_URL as django-staticfiles nicely collects
# admin's static media into STATIC_ROOT/admin.
ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

MIDDLEWARE_CLASSES = (
    # Gzip needs to be at the top.
    #'django.middleware.gzip.GZipMiddleware',
    # Below is the default list, don't modify it.
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    )

# Make this unique, and don't share it with anybody.
SECRET_KEY = ''

ROOT_URLCONF = 'flooding.urls'

CACHE_BACKEND = 'file://%s' % os.path.join(BUILDOUT_DIR, 'var', 'cache')
# Note: for development only, check django website for caching solutions for
# production environments
# ^^^ TODO

INSTALLED_APPS = (
    'django.contrib.auth',
    'flooding',
    'flooding_lib.tools.pyramids',
    'flooding_lib.sharedproject',
    'flooding_base',
    'flooding_presentation',
    'flooding_visualization',  # Must be below flooding_presentation
    'flooding_lib.tools.approvaltool',
    'lizard_worker',
    'flooding_lib',  # Must be below flooding_visualization,
                     # flooding_presentation, lizard_worker and
                     # approvaltool
    'flooding_lib.tools.importtool',
    'flooding_lib.tools.exporttool',
    'flooding_lib.tools.gdmapstool',
    'django.contrib.staticfiles',
    'raven.contrib.django.raven_compat',
    'django.contrib.admin',
    'django.contrib.contenttypes',
    'django.contrib.gis',
    'django.contrib.sessions',
    'django.contrib.sites',
    'supervisor',
    'markdown_deux',  # For markdown template filter in flooding-base
    'django_celery_results',
)

# Copied from nensskel template
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(name)s %(levelname)s\n    %(message)s',
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'handlers': {
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        },
        'logfile': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'formatter': 'verbose',
            'filename': os.path.join(BUILDOUT_DIR,
                                     'var', 'log', 'django.log'),
        },
        'sentry': {
            'level': 'WARN',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console', 'logfile', 'sentry'],
            'propagate': True,
            'level': 'INFO',
        },
        'django.db.backends': {
            'handlers': ['null'],  # Quiet by default!
            'propagate': False,
            'level': 'DEBUG',
        },
        'south': {
            'handlers': ['console', 'logfile', 'sentry'],
            'propagate': False,
            'level': 'INFO',  # Suppress the huge output in tests
        },
        'factory': {
            'handlers': ['console'],
            'propagate': False,
            'level': 'INFO',  # Suppress the huge output in tests
        },
        'django.request': {
            'handlers': ['console', 'logfile', 'sentry'],
            'propagate': False,
            'level': 'ERROR',  # WARN also shows 404 errors
        },
    }
}

# We create a handler to be able to show the tail of the Django log to the
# user. The handler implements the tail through up to two log files that are
# each up to 4 KB large. The log files are called
#
#    - /var/log/django_tail.log and
#    - /var/log/django_tail.log.1
#
# The latter log file is only created when the former has reached its maximum
# size.
TAIL_LOG = os.path.join(BUILDOUT_DIR, 'var', 'log', 'django_tail.log')

handler = RotatingFileHandler(TAIL_LOG, maxBytes=4096, backupCount=1)
logging.getLogger().addHandler(handler)

SYMBOLS_DIR = pkg_resources.resource_filename(
    'flooding_visualization', 'media/flooding_visualization/symbols')
FLOODING_SHARE = ''
EXTERNAL_PRESENTATION_MOUNTED_DIR = os.path.join(
    FLOODING_SHARE, 'presentationdatabase_totaal')
EXTERNAL_RESULT_MOUNTED_DIR = os.path.join(
    FLOODING_SHARE, 'resultaten')
# Set /tmp on separate divice and check it periodically
TMP_DIR = '/tmp'

GIS_DIR = os.path.join(BUILDOUT_DIR, 'var', 'gisdata')

RASTER_SERVER_URL = "http://flooding.lizard.net/wms"

#location of directories for task execution. Pelase configure to local
#installation root of HIS schade en slachtoffers module
HISSSM_ROOT = ''
#root of sobek program installation
SOBEK_PROGRAM_ROOT = ''
#root of sobek projects
SOBEK_PROJECT_ROOT = ''
#root of temporary directory for flooding tasks on windows
TMP_ROOT = 'c:\\temp'

PERFORM_TASK_MODULE = "flooding_lib.tasks.perform_task"
PERFORM_TASK_FUNCTION = "perform_task"

#queue's setting for flooding-worker
QUEUES = {
    "default": {
        "exchange": "",
        "binding_key": "default"},
    "logging": {
        "exchange": "router",
        "binding_key": "logging"},
    "failed": {
        "exchange": "router",
        "binding_key": "failed"},
    "sort": {
        "exchange": "router",
        "binding_key": "sort"},
    "120": {
        "exchange": "router",
        "binding_key": "120"},
    "130": {
        "exchange": "router",
        "binding_key": "130"},
    "132": {
        "exchange": "router",
        "binding_key": "132"},
    "134": {
        "exchange": "router",
        "binding_key": "134"},
    "150": {
        "exchange": "router",
        "binding_key": "150"},
    "155": {
        "exchange": "router",
        "binding_key": "155"},
    "160": {
        "exchange": "router",
        "binding_key": "160"},
    "162": {
        "exchange": "router",
        "binding_key": "162"},
    "180": {
        "exchange": "router",
        "binding_key": "180"},
    "185": {
        "exchange": "router",
        "binding_key": "185"},
    "190": {
        "exchange": "router",
        "binding_key": "190"},
    "200": {
        "exchange": "router",
        "binding_key": "200"},
    "210": {
        "exchange": "router",
        "binding_key": "210"},
    "220": {
        "exchange": "router",
        "binding_key": "220"},
    "900": {
        "exchange": "router",
        "binding_key": "900"},
}

HEARTBEAT_QUEUES = ["120", "130", "132", "134", "150", "155", "160", "162", "180", "185", "190", "200", "210", "220"]

# TODO: configure your broker settings
BROKER_SETTINGS = {
    "BROKER_HOST": "localhost",
    "BROKER_PORT": 5672,
    "BROKER_USER": "",
    "BROKER_PASSWORD": "",
    "BROKER_VHOST": "TODO",
    "HEARTBEAT": False
}

CELERY_RESULT_BACKEND = 'django-db'
#CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'
CELERY_IMPORTS = ['flooding_lib.celery_tasks']

# import ror-keringen
ROR_KERINGEN_PATH = os.path.join(BUILDOUT_DIR, 'var', 'ror_keringen')
ROR_KERINGEN_APPLIED_PATH = os.path.join(ROR_KERINGEN_PATH, 'applied')
ROR_KERINGEN_NOTAPPLIED_PATH = os.path.join(ROR_KERINGEN_PATH, 'not_applied')

RAVEN_CONFIG = {}

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

try:
    from flooding.localproductionsettings import *
except ImportError:
    pass

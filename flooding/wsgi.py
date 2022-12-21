"""
WSGI config for schademodule project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/howto/deployment/wsgi/
"""
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flooding.developmentsettings")

from django.core.wsgi import get_wsgi_application
# import logging
# import sys
# logger = logging.getLogger('that')
# logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
# logger.warn('this')
application = get_wsgi_application()

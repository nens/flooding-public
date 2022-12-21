# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.

from django.test import TestCase
from django.test.client import Client

from flooding_base.models import Application
from flooding_base.models import SubApplication
from flooding_base.models import Setting
from flooding_base.models import Site


class IntegrationTest(TestCase):
    def setUp(self):
        settings = (
            ('USE_GOOGLEMAPS', '0'),
            ('GOOGLEMAPS_KEY', ''),
            ('USE_OPENSTREETMAPS', '1'),
            ('URL_FAVICON', ''),
            ('URL_LOGO', ''),
            ('URL_TOPBAR', ''),
            ('RESTRICTMAP', '1'),
            )

        for setting, value in settings:
            Setting(key=setting, value=value).save()

        app = Application(name='test', type=Application.TYPE_FLOODING)
        app.save()
        sub_app = SubApplication(application=app, type=22)
        sub_app.save()
        Site(name='default_site', starter_application=sub_app).save()

    def test_homepage(self):
        c = Client()
        url = '/'

        response = c.get(url)
        self.assertEquals(response.status_code, 200)

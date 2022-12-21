# Python 3 is coming to town
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

from django.conf import settings
from django.conf.urls import include
from django.conf.urls import url
from django.contrib import admin

import flooding_base.urls
import flooding_lib.urls
import flooding_presentation.urls
import flooding_visualization.urls
import lizard_worker.urls
import django.contrib.staticfiles.urls

from flooding.views import ScenarioWorkflowView

admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^flooding/', include(flooding_lib.urls)),
    url(r'^visualization/', include(flooding_visualization.urls)),
    url(r'^presentation/', include(flooding_presentation.urls)),
    url(r'^worker/', include(lizard_worker.urls)),
    url(r'', include(flooding_base.urls)),

    url(r'^scenarios_processing/$', ScenarioWorkflowView.as_view(),
        name="scenarios_processing"),

    url(r'^scenarios_processing/step/(?P<step>\d+)$', ScenarioWorkflowView.as_view(),
        name="scenarios_processing"),

    url(r'^execute$', ScenarioWorkflowView.as_view(),
        name="execute_scenario"),

    url(r'^i18n/', include('django.conf.urls.i18n')),
]


if settings.DEBUG:
    # Add this also to the projects that use this application
    urlpatterns += [
        url(r'', include(django.contrib.staticfiles.urls))
    ]

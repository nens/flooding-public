# Python 3 is coming to town
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

from django.conf.urls import url

from flooding_lib.sharedproject import views


urlpatterns = [
    url(r'^ror/$',
        views.Dashboard.as_view(project_name="ror"),
        name='sharedproject_dashboard'),
    url(r'^ror/(?P<province_id>\d+)/$',
        views.Dashboard.as_view(project_name="ror"),
        name='sharedproject_dashboard_province'),
    url(r'^(?P<project_name>[a-z]+)/(?P<province_id>\d+)/excel/',
        views.excel,
        name='sharedproject_dashboard_excel'),
]

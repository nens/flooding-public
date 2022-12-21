# -*- coding: utf-8 -*-
# Python 3 is coming to town
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.uber_service, name='visualization'),
    url(r'^symbol/(?P<symbol>.*)$', views.get_symbol, name='visualization_symbol'),
    url(r'^legend/$', views.legend_shapedata, name='visualization_legend'),
    url(r'^testmapping/$', views.testmapping, name='visualization_testmapping'),
]

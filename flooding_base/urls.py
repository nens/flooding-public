# Python 3 is coming to town
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

from django.conf.urls import include
from django.conf.urls import url
from django.conf import settings

import django.contrib.auth.views
from . import views

config_pattern = r'^service/configuration/(?P<configuration_id>\d+)'
filter_pattern = config_pattern + r'/filter/(?P<filter_id>[_A-Za-z0-9]*)/'

urlpatterns = [
    # The old lizard.base urls that were previously mounted under /service.
    # We now mount them there directly.
    url(r'^service/$',views.service_uberservice, name='base_service_uberservice'),
    url(r'^service/configuration/$', views.service_get_configurations, name='base_service_get_configurations'),
    url(config_pattern + r'/filter/$',
        views.service_get_filters, name='base_service_get_filters'),
    url(filter_pattern + r'location/$',
        views.service_get_locations, name='base_service_get_locations'),
    url(filter_pattern + r'parameter/$',
        views.service_get_parameters, name='base_service_get_parameters'),
    url(config_pattern + r'/location/(?P<location_id>[_/A-Za-z0-9]*)/$',
        views.service_get_location, name='base_service_get_location'),
    url(config_pattern + r'/timeseries/$',
        views.service_get_timeseries,  name='base_service_get_timeseries'),

    # URLs that were previously defined in the old lizard root urls.py but
    # that have to do with base.

    url(r'^$', views.gui, name='root_url'),
    url(r'^get_config.js$',views.gui_config, name='gui_config'),
    url(r'^get_translated_strings.js$',
        views.gui_translated_strings, name='gui_translated_strings'),
    url(r'^help/$', views.help, name='help_url'),
    url(r'^userconfiguration/$', views.userconfiguration, name='userconfiguration_url'),
    url(r'^base/testdatabase/$', views.testdatabase_list, name='testdatabase_list'),
    url(r'^base/testdatabase/(?P<configuration_id>\d+)/$',
        views.testdatabase, name='testdatabase_detail'),
    url(r'^accounts/login/$', django.contrib.auth.views.login, name='login_url'),
    url(r'^accounts/logout/$', django.contrib.auth.views.logout, name='logout_url'),
    url(r'^accounts/password_change/$',
        django.contrib.auth.views.password_change, name='password_change_url'),
    url(r'^accounts/password_change/done/$',
        django.contrib.auth.views.password_change_done, name='password_change_done'),
]

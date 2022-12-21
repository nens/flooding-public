# Python 3 is coming to town
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.overview, name='flooding_tools_import_overview'),
    url(r'^verifyimport/(?P<import_scenario_id>\d+)$',
        views.verify_import, name='flooding_tools_import_verify'),
    url(r'^newimport/$',
        views.new_import, name='flooding_tools_import_new'),
    url(r'^approveimport/(?P<import_scenario_id>\d+)$',
        views.approve_import, name='flooding_tools_import_approve'),
    url(r'^groupimport/$',
        views.group_import, name='flooding_tools_import_group'),
    url(r'^groupimport/download_example_csv$',
        views.group_import_example_csv, name='flooding_tools_import_group_download_csv'),
    url(r'^newimport/(?P<import_scenario_id>\d+)/uploadfiles$',
        views.upload_import_scenario_files, name='flooding_tools_upload_files'),
    url(r'^rorkeringen/$$',
        views.ror_keringen_page, name='flooding_tools_ror_keringen_page'),
]

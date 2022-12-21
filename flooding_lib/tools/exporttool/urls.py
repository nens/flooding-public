# Python 3 is coming to town
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='flooding_tools_export_index'),
    url(r'^exportdetail/(?P<export_run_id>\d+)/resultfile/',
        views.exportrun_resultfile, name='flooding_tools_export_resultfile'),
    url(r'^exportdetail/(?P<export_run_id>\d+)$',
        views.export_detail, name='flooding_tools_export_detail'),
    url(r'^exportdetailscenarios/(?P<export_run_id>\d+)$',
        views.export_detail_scenarios, name='flooding_tools_export_detail_scenarios'),
    url(r'exportdetail/(?P<export_run_id>\d+)/togglearchive/$',
        views.toggle_archived_export, name='flooding_tools_archive_export'),
    url(r'exportdetail/(?P<export_run_id>\d+)/delete/$',
        views.delete_archived_export, name='flooding_tools_delete_export'),
    url(r'^newexportindex/$',
        views.new_export_index, name='flooding_tools_export_new_export_index'),
    url(r'^newexport/$',
        views.new_export, name='flooding_tools_export_new_export'),
    url(r'^loadexportform/(?P<export_run_id>\d+)/$',
        views.load_export_form, name='flooding_tools_export_load_export_form'),
    url(r'^reuseexport/(?P<export_run_id>\d+)$',
        views.reuse_export, name='flooding_tools_reuse_export'),
    url(r'^reuseexport/(?P<export_run_id>\w+)/scenarios$',
        views.export_run_scenarios, name='flooding_tools_reuse_export_scenarios'),
]

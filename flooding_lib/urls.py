# Python 3 is coming to town
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

from django.conf.urls import url, include
from django.conf import settings

from flooding_lib import views
from flooding_lib import scenario_sharing
from flooding_lib import services
from flooding_lib.views import pages, zipped, infowindow
from flooding_lib.models import Project
import flooding_lib.sharedproject.urls

info_dict = {
    'queryset': Project.objects.all(),
}


urlpatterns = [
    url(r'^$', views.index, name='flooding'),
    url(r'^tools/', include('flooding_lib.tools.urls')),
    url(r'^project/$', views.project_list, name='flooding_projects_url'),
    url(r'^project/add/$', views.project_addedit, name='flooding_project_add'),
    url(r'^project/(?P<object_id>\d+)/$', views.project, name='flooding_project_detail'),
    url(r'^project/(?P<object_id>\d+)/edit/$', views.project_addedit, name='flooding_project_edit'),
    url(r'^project/(?P<object_id>\d+)/delete/$', views.project_delete, name='flooding_project_delete'),
    url(r'^scenario/$', views.scenario_list, name='flooding_scenarios_url'),
    url(r'^scenario/add/$', views.scenario_addedit, name='flooding_scenario_add'),
    url(r'^scenario/share/$', scenario_sharing.list_view, name='flooding_scenario_share_list'),
    url(r'^scenario/share/(?P<project_id>\d+)/$',
        scenario_sharing.list_project_view, name='flooding_scenario_share_project_list'),
    url(r'^scenario/share/action/$',
        scenario_sharing.action_view, name='flooding_scenario_share_action'),
    url(r'^scenario/(?P<object_id>\d+)/$', views.scenario, name='flooding_scenario_detail'),
    url(r'^scenario/(?P<object_id>\d+)/edit/$',
        views.scenario_addedit, name='flooding_scenario_edit'),
    url(r'^scenario/(?P<object_id>\d+)/editnameremarks/$',
        views.scenario_editnameremarks, name='flooding_scenario_editnameremarks'),
    url(r'^scenario/(?P<object_id>\d+)/delete/$',
        views.scenario_delete, name='flooding_scenario_delete'),
    url(r'^scenario/(?P<scenario_id>\d+)/addcutofflocation/$',
        views.scenario_cutofflocation_add, name='flooding_scenario_cutofflocation_add'),
    url(r'^scenariocutofflocation/(?P<object_id>\d+)/delete/$',
        views.scenario_cutofflocation_delete, name='flooding_scenario_cutofflocation_delete'),
    url(r'^scenario/(?P<scenario_id>\d+)/addbreach/$',
        views.scenario_breach_add, name='flooding_scenario_breach_add'),
    url(r'^scenariobreach/(?P<object_id>\d+)/delete/$',
        views.scenario_breach_delete, name='flooding_scenario_breach_delete'),
    url(r'^infowindow/$', views.infowindow.infowindow, name='infowindow'),

    url(r'^fractal/$', views.fractal),
    url(r'^result/$', views.result_list, name='flooding_result_list'),

    # Note -- no $ at the end! There is a file name there, which we
    # ignore. It's only there so that the downloading web browser
    # knows what to call the file.
    url(r'^result_download/(?P<result_id>\d+)/', views.result_download, name='result_download'),
    url(r'^task/$', views.task_list, name='flooding_task_list'),
    url(r'^task/(?P<object_id>\d+)/$', views.task, name='flooding_task_detail'),
    url(r'^service/$', services.service, name='flooding_service'),
    url(r'^service/project/$',
        services.service_get_projects, name='flooding_service_get_projects'),
    url(r'^service/project/(?P<project_id>\d+)/scenarios/$',
        services.service_get_scenarios_from_project,
        name='flooding_service_get_scenarios_from_project'),
    url(r'^service/scenario/$',
        services.service_get_scenarios, name='flooding_service_get_scenarios'),
    url(r'^service/regionset/$',
        services.service_get_regionsets, name='flooding_service_get_regionsets'),
    url(r'^service/region/$',
        services.service_get_all_regions, name='flooding_service_get_all_regions'),
    url(r'^service/region/(?P<region_id>\d+)/breaches/$',
        services.service_get_breaches, name='flooding_service_get_breaches'),
    url(r'^service/regionset/(?P<regionset_id>\d+)/regions/$',
        services.service_get_regions, name='flooding_service_get_regions'),
    url(r'^service/breach/(?P<breach_id>\d+)/scenarios/$',
        services.service_get_scenarios_from_breach,
        name='flooding_service_get_scenarios_from_breach'),
    url(r'^service/scenario/(?P<scenario_id>\d+)/results/$',
        services.service_get_results_from_scenario,
        name='flooding_service_get_results_from_scenario'),

    url(r'^service/scenario/(?P<scenario_id>\d+)/tasks/$',
        services.service_get_tasks_from_scenario,
        name='flooding_service_get_tasks_from_scenario'),

    url(r'^service/scenario/(?P<scenario_id>\d+)/cutofflocations/$',
        services.service_get_cutofflocations_from_scenario,
        name='flooding_service_get_cutofflocations_from_scenario'),

    url(r'^service/result/(?P<object_id>\d+)/(?P<location_nr>\d+)' +
        r'/(?P<parameter_nr>\d+)/$',
        views.service_result, name='flooding_service_result'),

    url(r'^excel/$',
        views.ExcelImportExportView.as_view(),
        name='flooding_excel_import_export'),

    url(r'^excel/(?P<project_id>\d+)/$',
        views.ExcelImportExportViewProject.as_view(),
        name='flooding_excel_import_export_project'),

    # Note no $ at the end, we want to add the filename
    url(r'^excel/(?P<project_id>\d+)/',
        views.excel_download, name='flooding_excel_download'),

    url(r'^ror_keringen_zip/applied/(?P<filename>[a-zA-Z0-9\._\-]+)',
        views.ror_keringen_download,
        name='flooding_ror_keringen_download'),

    url(r'^shared/', include(flooding_lib.sharedproject.urls)),

    url(r'^breachinfo/(?P<project_id>\d+)/(?P<breach_id>\d+)/excel/',
        pages.breachinfo_excel,
        name='flooding_breachinfo_page_excel'),

    url(r'^breachinfo/(?P<project_id>\d+)/(?P<breach_id>\d+)/$',
        pages.BreachInfoView.as_view(),
        name='flooding_breachinfo_page'),

    url(r'^scenario/(?P<scenario_id>\d+)/inundationstats/$',
        pages.InundationStatsView.as_view(),
        name='flooding_inundationstats_page'),

    url(r'^scenario/(?P<scenario_id>\d+)/results/',
        zipped.scenario_results_zipfile,
        name='flooding_results_zipped'),

    url(r'^preload/(?P<project_id>\d+)/(?P<scenario_id>\d+)/',
        views.preload_scenario_redirect,
        name="preload_scenario_redirect"),
]

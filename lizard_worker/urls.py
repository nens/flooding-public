# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
# Python 3 is coming to town
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

from django.conf import settings
from django.conf.urls import handler404
from django.conf.urls import include
from django.conf.urls import url
from django.http import HttpResponseServerError
from django.template import Context
from django.template import loader
from lizard_worker.views import (
    WorkflowTasksView, WorkflowsView, LoggingView)

handler404  # pyflakes

urlpatterns = [
    url(r'^scenario/(?P<scenario_id>\d*)/$',
        WorkflowsView.as_view(), name='lizard_worker_scenario'),
    url(r'^workflow/(?P<workflow_id>\d+)/tasks/$',
        WorkflowTasksView.as_view(), name='lizard_worker_workflow_task'),
    url(r'^scenario/(?P<scenario_id>\d*)/workflow/(?P<workflow_id>\d+)/loggings/$',
        LoggingView.as_view(), name='lizard_worker_workflow_logging'),
    url(r'^scenario/(?P<scenario_id>\d*)/workflow/(?P<workflow_id>\d+)/loggings/step/(?P<step>\d+)$',
        LoggingView.as_view(), name='lizard_worker_workflow_logging'),
    url(r'^scenario/(?P<scenario_id>\d*)/workflow/(?P<workflow_id>\d+)/task/(?P<task_id>\d*)/loggings/$',
        LoggingView.as_view(), name='lizard_worker_workflow_task_logging'),
    url(r'^scenario/(?P<scenario_id>\d*)/workflow/(?P<workflow_id>\d+)/task/(?P<task_id>\d*)/loggings/stap/(?P<step>\d+)$',
        LoggingView.as_view(), name='lizard_worker_workflow_task_logging'),
]

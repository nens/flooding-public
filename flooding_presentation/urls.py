# Python 3 is coming to town
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^service/$', views.uber_service, name='presentation'),
    url(r'^permissions/$',views.overview_permissions, name='presentation_permissions'),
]

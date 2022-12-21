# Python 3 is coming to town
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^pyramid_parameters/$', views.pyramid_parameters, name='pyramids_parameters'),
    url(r'^pyramid_value/$', views.pyramid_value, name='pyramid_value'),
    url(r'^animation_value/$', views.animation_value, name='animation_value')
]

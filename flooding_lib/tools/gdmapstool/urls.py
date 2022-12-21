# Python 3 is coming to town
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='flooding_gdmaapstool_index'),
    url(r'^gdmapdetail/(?P<gdmap_id>\d+)$',
        views.gdmap_details, name='flooding_gdmapstool_mapdetails'),
    url(r'^reusegdmap/(?P<gdmap_id>\d+)$',
        views.reuse_gdmap, name='flooding_gdmapstool_reuse_gdmap'),
    url(r'^loadgdmapform/(?P<gdmap_id>\d+)/$',
        views.load_gdmap_form, name='flooding_tools_gdmap_load_form'),
    url(r'^savegdmapform/$',
        views.save_gdmap_form, name='flooding_tools_gdmap_save_form'),
]

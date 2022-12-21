# Python 3 is coming to town
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

from django.conf.urls import url, include

from . import views

urlpatterns = [
    url(r'^$', views.index, name='flooding_tools'),
    url(r'^export/',
        include('flooding_lib.tools.exporttool.urls')),
    url(r'^gdmap/',
        include('flooding_lib.tools.gdmapstool.urls')),
    url(r'^import/',
        include('flooding_lib.tools.importtool.urls')),
    url(r'^approval/',
        include('flooding_lib.tools.approvaltool.urls')),
    url(r'^pyramids/',
        include('flooding_lib.tools.pyramids.urls')),
]

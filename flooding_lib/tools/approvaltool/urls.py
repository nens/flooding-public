# Python 3 is coming to town
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'table/(?P<approvalobject_id>\d+)$',
        views.approvaltable_page, name='flooding_tools_approval_table'),
]

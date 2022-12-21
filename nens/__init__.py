#!c:/python25/python.exe
# -*- coding: utf-8 -*-
#***********************************************************************
#
# This file is part of the nens library.
#
# the nens library is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# the nens library is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with the nens libraray.  If not, see
# <http://www.gnu.org/licenses/>.
#
# Copyright 2006, 2007, 2008, 2009 Jack Ha
# Copyright 2008, 2009 Mario Frasca
#*
#***********************************************************************
#*
#* $Id$
#*
#* initial programmer :  Mario Frasca
#* initial date       :  20081105
#**********************************************************************

"""\ nens is a python library developed at Nelen & Schuurmans and
aiming at making repetitive work quicker.  it contains everything we
have developed here that has been used in more than one project.

to get help about a contained package, try:
help(nens.<name>)

.. automodule:: nens.sobek
   :members:
.. automodule:: nens.asc
   :members:
.. automodule:: nens.gp
   :members:
.. automodule:: nens.geom
   :members:
.. automodule:: nens.fews
   :members:
.. automodule:: nens.mock
   :members:
.. automodule:: nens.numeric
   :members:
.. automodule:: nens.turtleurbanclasses
   :members:
.. automodule:: nens.turtleruralclasses
   :members:
.. automodule:: nens.uuid
   :members:
"""

import sys

if sys.version_info >= (2, 4):
    __all__ = ['sobek',
               'asc',
               'gp',
               'geom',
               'fews',
               'mock',
               'turtleurbanclasses',
               'uuid',
               ]
else:
    __all__ = ['gp',
               ]

__revision__ = "$Rev$"[6:-2]

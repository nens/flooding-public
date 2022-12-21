#!/usr/bin/python
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
# Copyright 2011 Nelen & Schuurmans
#*
#***********************************************************************
#*
#* Project    : various
#*
#* $Id: geom_tests.py 24585 2011-10-03 12:35:00Z mario.frasca $
#*
#* initial programmer :  Mario Frasca
#* initial date       :  2011-11-15
#**********************************************************************

import unittest
import logging
import tempfile
import os
from fews import DiagHandler


class FewsDiagHandlerTest(unittest.TestCase):
    def testLogsTranslatingFewsLevels(self):
        root = logging.getLogger("")
        handle, logfile = tempfile.mkstemp(suffix=".xml")
        os.close(handle)
        fews_handler = DiagHandler(logfile)
        root.addHandler(fews_handler)
        root.debug("should be fews:3")
        root.info("should be fews:3")
        root.warn("should be fews:2")
        root.error("should be fews:1")
        root.critical("should be fews:0")
        root.removeHandler(fews_handler)

        f = file(logfile)
        lines = f.readlines()
        f.close()

        for target, current in zip(['<line level="3" ',
                                    '<line level="3" ',
                                    '<line level="2" ',
                                    '<line level="1" ',
                                    '<line level="0" ',
                                    ],
                                   lines[2:7]):
            self.assertTrue(current.startswith(target))
        os.unlink(logfile)

    def testClosingForcedly(self):
        root = logging.getLogger("")
        handle, logfile = tempfile.mkstemp(suffix=".xml")
        os.close(handle)
        fews_handler = DiagHandler(logfile)
        root.addHandler(fews_handler)
        root.debug("whatever")
        root.removeHandler(fews_handler)
        fews_handler.close()  # removing, so we must close it by hand

        f = file(logfile)
        lines = f.readlines()
        f.close()

        self.assertTrue(lines[-1].startswith("</Diag>"))
        os.unlink(logfile)

    def testClosingAtShutdown(self):
        root = logging.getLogger("")
        handle, logfile = tempfile.mkstemp(suffix=".xml")
        os.close(handle)
        fews_handler = DiagHandler(logfile)
        root.addHandler(fews_handler)
        root.debug("whatever")
        logging.shutdown()  # not removing the handler, the logging
                            # subsystem closes it.

        f = file(logfile)
        lines = f.readlines()
        f.close()

        self.assertTrue(lines[-1].startswith("</Diag>"))
        os.unlink(logfile)


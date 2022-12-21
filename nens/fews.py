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
# Copyright 2008, 2009 Mario Frasca
#*
#***********************************************************************
#* Library    : some specific fews objects
#*
#* Project    : various
#*
#* $Id: gp.py 24569 2011-10-03 07:06:16Z mario.frasca $
#*
#* initial programmer :  Mario Frasca
#* initial date       :  2011-11-14
#**********************************************************************

import logging


class DiagHandler(logging.FileHandler):
    """LogRecords Handler useful for creating correct fews diagnostics files.

    Adds an extra handler to the logging class which writes
    messages to a FEWS diagnostics file
    """

    class Formatter(logging.Formatter):
        def format(self, record):
            if self._fmt.find("%(fewslevel)") >= 0:
                record.fewslevel = (3 if record.levelno <= logging.INFO
                                    else 2 if record.levelno <= logging.WARNING
                                    else 1 if record.levelno <= logging.ERROR
                                    else 0)
            return logging.Formatter.format(self, record)

    def __init__(self, filename, format=None, *args, **kwargs):
        """create object and write prologue to diagnostics file
        """

        logging.FileHandler.__init__(self, filename, *args, **kwargs)
        print self.baseFilename
        if format == None:
            format = '<line level="%(fewslevel)d" description="LizardScripter :: %(asctime)s :: %(message)s"/>'
        self.setFormatter(self.Formatter(format))
        out = open(self.baseFilename, "w")
        out.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
        out.write('<Diag version="1.2" xmlns="..." xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="...">\n')
        out.close()
        self.is_open = True

    def emit(self, record):
        if self.is_open:
            logging.FileHandler.emit(self, record)

    def close(self):
        """add the closing tag to the diagnostics file
        """

        if self.is_open:
            out = open(self.baseFilename, "a")
            out.write("</Diag>\n")
            out.close()
            self.is_open = False

        logging.FileHandler.close(self)

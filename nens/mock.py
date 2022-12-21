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
#
#***********************************************************************
#* Library    : nens.mock
#* Purpose    : provides mock objects for unit testing
#*
#* Project    : all
#*
#* $Id$
#*
#* initial programmer :  Mario Frasca
#* initial date       :  20090402
#**********************************************************************

from __future__ import nested_scopes
__revision__ = "$Rev$"[6:-2]

import sys
if sys.version_info < (2, 3):
    False = 0
    True = 1

import logging
log = logging.getLogger('nens.mock')


def lint(filename):
    """executes pylint filtering just errors and warnings...
    """

    import sys
    sys_exit = sys.exit
    sys_stderr = sys.stderr

    sys.stderr = Stream()

    def noexit(retval):
        pass

    sys.exit = noexit

    import pylint.lint
    pylint.lint.Run(['--errors-only', filename])
    sys.exit = sys_exit
    sys.stderr = sys_stderr


class ZipFile:
    def __init__(self):
        self.names = []
        self.content = []
        pass

    def namelist(self):
        return self.names

    def writestr(self, zinfo_or_arcname, bytes):
        self.names.append(zinfo_or_arcname)
        self.content.append(bytes)

    pass


class Stream:
    """mock stream (file)

    can be written to and read from.
    check content in 'content' field"""
    def __init__(self, content=None):
        self.content = content
        if content:
            lines = (content + '\n').split('\n')[:-1]
            self.lines = [i + '\n' for i in lines[:-1]]
            self.lines.append(lines[-1])
        self.counter = -1

    def read(self, *args, **kwargs):
        result = self.content
        self.content = ""
        return result

    def seek(self, pos):
        assert(pos == 0)
        self.counter = -1

    def write(self, text):
        if self.content is None:
            self.content = []
        self.content.append(text)

    def readline(self):
        self.counter += 1
        if self.counter == len(self.lines):
            return ''
        return self.lines[self.counter]

    def readlines(self):
        return self.lines

    def __iter__(self):
        self.iter_counter = -1
        return self

    def next(self):
        self.iter_counter += 1
        if self.iter_counter == len(self.lines):
            raise StopIteration
        return self.lines[self.iter_counter]

    def close(self):
        return


class GpDispatch:
    """mock 9.2 geoprocessor, contains more mock ArcGIS objects
    """

    class Name:
        def __init__(self, name):
            self.name = name
            self.Name = name
            self.Type = ''
            self.type = ''

    class Fields:
        def __init__(self, keys):
            keys.sort()
            self.data = [GpDispatch.Name(i) for i in keys]

        def reset(self):
            self.pos = 0

        def next(self):
            if self.pos == len(self.data):
                return None
            result = self.data[self.pos]
            self.pos += 1
            return result

    class Cursor:
        def __init__(self, values):
            self.values = values
            self.pos = None

        def reset(self):
            self.pos = 0

        def next(self):
            if self.pos == len(self.values):
                return None
            result = GpDispatch.Row(self.values[self.pos])  # make container
            self.pos += 1
            return result

    class Row:
        def __init__(self, values):
            for k, v in values.items():
                self.__dict__[k] = v  # store as attribs

        def getvalue(self, key):
            return self.__dict__[key]
        pass

    def __init__(self, default_table={}, tables={}, files=[]):
        self.default_table = default_table
        self.receivedMessages = []
        self.tables = tables
        self.files = files

    def ListFields(self, table_name):
        table = self.tables.get(table_name, self.default_table)
        return self.Fields(table[0].keys())

    def SearchCursor(self, table_name):
        table = self.tables.get(table_name, self.default_table)
        return self.Cursor(table)

    def AddError(self, t):
        self.receivedMessages.append((logging.ERROR, t))

    def AddWarning(self, t):
        self.receivedMessages.append((logging.WARNING, t))

    def AddMessage(self, t):
        self.receivedMessages.append((logging.INFO, t))

    def Exists(self, fn):
        return fn in self.files

import logging


class Handler(logging.Handler):
    "a mock handler to test logging"
    def __init__(self, *argv, **kwargs):
        logging.Handler.__init__(self, *argv, **kwargs)
        self.content = []
        ## set a simple format, easy to parse while testing
        formatter = logging.Formatter('%(name)s|%(levelname)s|%(message)s')
        self.setFormatter(formatter)

    def emit(self, record):
        self.content.append(self.format(record))

    def flush(self):
        self.content = []


class Point:
    """class defining get_x and get_y

    object in this class has x and y
    """

    def __init__(self, x, y):
        self.x, self.y = x, y

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y


class Object:
    """if you need a placeholder

    create one, define its attributes, use it.
    """
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
    pass


class gdal:
    "misusing a class to simulate a namespace"

    class Band:
        """mock object for gdal.Band"""

        def __init__(self, data, nodata_value):
            import numpy
            translation = {numpy.ubyte: 1,
                           numpy.uint16: 2,
                           numpy.int16: 3,
                           numpy.uint32: 4,
                           numpy.int32: 5,
                           numpy.float32: 6,
                           numpy.float64: 7,
                           }
            self.data = data
            self.DataType = translation[data.dtype.type]
            self.nodata_value = nodata_value
            self.YSize = data.shape[0]
            self.XSize = data.shape[1]

        def GetNoDataValue(self):
            return self.nodata_value

        def ReadRaster(self, xoffset, yoffset, xsize, ysize, _1, _2, dataType):
            import numpy
            import struct
            packing_types = [(None, None),
                             ('c', numpy.ubyte),
                             ('H', numpy.uint16),
                             ('h', numpy.int16),
                             ('I', numpy.uint32),
                             ('i', numpy.int32),
                             ('f', numpy.float32),
                             ('d', numpy.float64)]
            pack_char, numpy_type = packing_types[dataType]
            values = self.data[yoffset:yoffset + ysize, xoffset:xoffset + xsize]
            return struct.pack(pack_char * self.XSize, *list(values.flat))
        pass

    class Dataset:
        """mock object for gdal.Dataset
        """

        def __init__(self, data, xllcorner, yllcorner, cellsize, nodata_value):
            self.data = data
            self.RasterYSize, self.RasterXSize = data.shape
            nrows = self.RasterYSize
            self.nodata_value = nodata_value
            self.geotransform = [xllcorner, cellsize, None, yllcorner + cellsize * nrows, None]

        def GetGeoTransform(self):
            "the location and size of the grid"
            return self.geotransform

        def GetDescription(self):
            "the location of the directory holding the header"
            return ""

        def GetRasterBand(self, band_no):
            return gdal.Band(self.data, self.nodata_value)


class Book:
    """mock.Book mocks xlrd.Book

    only a small part of the interface is implemented here

    >>> b = Book(data=[[['id', 'b', 'c'], [1, 2, 3], [2, 2, 9], [3, 1, 16]]])
    >>> b.count
    1
    >>> s = b.sheet_by_index(0)

    the 'header'
    >>> s.row_values(0)
    ['id', 'b', 'c']

    the first column, skipping the header
    >>> s.col_values(0, 1)
    [1, 2, 3]

    a single cell
    >>> s.cell(3,2) #doctest:+ELLIPSIS
    <....Cell instance at ...>
    >>> s.cell(3,2).value
    16
    >>> s.cell_value(3,2)
    16
    """

    def __init__(self, count=3, shape=(30, 50), data=None):
        """
        >>> b = Book()
        >>> b.count
        3
        >>> b.shape
        (30, 50)
        >>> b.data
        """
        self.count = count
        self.shape = shape
        self.data = data
        if self.data is not None:
            self.count = len(self.data)

    def sheet_by_index(self, index):
        """return the correspondig sheet

        imagine you have a book with only one sheet,
        >>> b = Book(count=1)
        >>> b.sheet_by_index(0) #doctest:+ELLIPSIS
        <....Sheet instance at ...>

        >>> b.sheet_by_index(-1)
        Traceback (most recent call last):
        ...
        IndexError
        >>> b.sheet_by_index(1)
        Traceback (most recent call last):
        ...
        IndexError
        """
        if self.data is not None:
            return Sheet(data=self.data[index])
        if index >= self.count or index < 0:
            raise IndexError()
        return Sheet(shape=self.shape)


class Sheet:
    """this is either the same default_value at all cells in range or
    a list (rows) of lists which should be the same length
    """
    def check_coords(self, rowx, colx):
        if self.data is not None:
            self.data[rowx][colx]
        if colx >= self.shape[1]:
            raise IndexError
        if rowx >= self.shape[0]:
            raise IndexError

    def __init__(self, shape=(30, 10), data=None, default_value=0):
        "shape is (row_no, col_no)"
        self.data = data
        self.default_value = default_value
        if data is not None:
            self.shape = (len(data), len(data[0]))
        else:
            self.shape = shape

    def col_values(self, colx, start_rowx=0, end_rowx=None):
        if end_rowx is None:
            end_rowx = self.shape[0]
        self.check_coords(start_rowx, colx)
        self.check_coords(end_rowx - 1, colx)
        if self.data is not None:
            return [self.data[i][colx] for i in range(start_rowx, end_rowx)]
        return [self.default_value] * (end_rowx - start_rowx)

    def cell_type(self, rowx, colx):
        self.check_coords(rowx, colx)
        if self.data is not None:
            if self.data[rowx][colx] == '':
                return 0
        return 1

    def cell_value(self, rowx, colx):
        return self.cell(rowx, colx).value

    def row_values(self, rowx, start_colx=0, end_colx=None):
        if end_colx is None:
            end_colx = self.shape[1]
        self.check_coords(rowx, start_colx)
        self.check_coords(rowx, end_colx - 1)
        if self.data is not None:
            return [self.data[rowx][i] for i in range(start_colx, end_colx)]
        return [self.default_value] * (end_colx - start_colx)

    def cell(self, rowx, colx):
        self.check_coords(rowx, colx)
        if self.data is not None:
            return Cell(self.data[rowx][colx])
        return Cell(self.default_value)


class Cell:
    def __init__(self, value):
        self.value = value
        pass

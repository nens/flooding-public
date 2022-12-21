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
#* $Id$
#*
#* initial programmer :  Mario Frasca
#* initial date       :  2008-07-28
#**********************************************************************

import unittest
import mock
import numpy

gdal = None
try:
    from osgeo import gdal
except ImportError:
    pass

from asc import AscGrid
from asc import ColorMapping


class GridFromFile(unittest.TestCase):
    data = """\
nCols        5
nRows        5
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
 -999 -0.2 0 -999 3.05
 -999 0 0 0.5 1.2
 -999 0 0 0 -999
 0 0 0 0 -999
 -999 1.1 1.4 0.1 0
"""
    outstr0 = """\
nCols        6
nRows        4
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
 0 0 0 0 0 0
 0 0 0 0 0 0
 0 0 0 0 0 0
 0 0 0 0 0 0
"""
    outstr1 = """\
nCols        6
nRows        4
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
 0.1 0.1 0.1 0.1 0.1 0.1
 0.1 0.1 0.1 0.1 0.1 0.1
 0.1 0.1 0.1 0.1 0.1 0.1
 0.1 0.1 0.1 0.1 0.1 0.1
"""

    def test00(self):
        "create object from scratch"

        obj = AscGrid(ncols=6, nrows=4, xllcorner=135000, yllcorner=455000, cellsize=100, nodata_value=-999, default_value=0.0)
        output = mock.Stream()
        obj.writeToStream(output)
        self.assertEqual(''.join(output.content), self.outstr0)

    def test01(self):
        "create object from scratch with defaults"

        obj = AscGrid(ncols=6, nrows=4, xllcorner=135000, yllcorner=455000, cellsize=100, nodata_value=-999, default_value=0.1)
        obj = AscGrid(ncols=6, nrows=4, xllcorner=135000, yllcorner=455000, cellsize=100, nodata_value=-999, default_value=obj)
        output = mock.Stream()
        obj.writeToStream(output)
        self.assertEqual(''.join(output.content), self.outstr1)

    def test1_reading_from_file(self):
        "metadata about the grid"
        obj = AscGrid(mock.Stream(self.data))
        self.assertEqual(obj.ncols, 5)
        self.assertEqual(obj.nrows, 5)
        self.assertEqual(obj.xllcorner, 135000)
        self.assertEqual(obj.yllcorner, 455000)
        self.assertEqual(obj.cellsize, 100)
        self.assertEqual(obj.nodata_value, -999)

    def test2_reading_from_file(self):
        "matrix of digital elevation model"
        obj = AscGrid(mock.Stream(self.data))
        self.assertEqual(len(obj.values), obj.nrows)
        self.assertEqual([len(item) for item in obj.values], [obj.ncols] * int(obj.nrows))

    def test30_reading_from_file(self):
        "matrix of digital elevation model - with comments line"
        obj = AscGrid(mock.Stream("/* qualcuno vuole dirti qualcosa che non ti interessa\n" + self.data))
        self.assertEqual(len(obj.values), obj.nrows)
        self.assertEqual([len(item) for item in obj.values], [obj.ncols] * int(obj.nrows))


class GridRecognizesObjects(unittest.TestCase):
    data = """\
nCols        5
nRows        5
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
 -999 -0.2 0 -999 3.05
 -999 0 0 0.5 1.2
 -999 0 0 0 -999
 0 0 0 0 -999
 -999 1.1 1.4 0.1 0
"""

    def test2_reading(self):
        "grid elevation model, valid pixel by row/col"

        obj = AscGrid(mock.Stream(self.data))
        self.assertEqual(obj[2, 1], -0.2)
        self.assertEqual(obj[3, 1], 0.0)
        self.assertEqual(obj[5, 1], 3.05)
        self.assertEqual(obj[1, 4], 0)

    def test3_pixel(self):
        "grid elevation model, non valid pixel inside of the grid."

        obj = AscGrid(mock.Stream(self.data))
        self.assertEqual(obj[1, 1], None)
        self.assertEqual(obj[4, 1], None)
        self.assertEqual(obj[1, 1], None)
        self.assertEqual(obj[1, 2], None)
        self.assertEqual(obj[1, 3], None)
        self.assertEqual(obj[1, 5], None)

    def test40_pixel_by_geocoords(self):
        "grid elevation model, (non)valid pixel by geographical coordinates"

        obj = AscGrid(mock.Stream(self.data))
        self.assertEqual(obj[135054, 455009], None)
        self.assertEqual(obj[135254, 455209], 0.0)
        self.assertEqual(obj[135154, 455049], 1.1)
        self.assertEqual(obj[135254, 455089], 1.4)

    def test45_pixel_by_geocoords(self):
        "grid elevation model, (non)valid pixel by Point"

        obj = AscGrid(mock.Stream(self.data))
        self.assertEqual(obj[mock.Point(135054, 455009)], None)
        self.assertEqual(obj[mock.Point(135254, 455209)], 0.0)
        self.assertEqual(obj[mock.Point(135154, 455049)], 1.1)
        self.assertEqual(obj[mock.Point(135254, 455089)], 1.4)

    def test50_pixel(self):
        "grid elevation model, pixel outside of the grid by geographical coordinates."

        obj = AscGrid(mock.Stream(self.data))
        self.assertEqual(obj[105054, 455009], False)
        self.assertEqual(obj[235054, 455009], False)
        self.assertEqual(obj[135054, 355009], False)
        self.assertEqual(obj[135000, 455600], False)
        self.assertEqual(obj[134900, 455000], False)

    def test55_pixel(self):
        "grid elevation model, pixel outside of the grid by Point."

        obj = AscGrid(mock.Stream(self.data))
        self.assertEqual(obj[mock.Point(105054, 455009)], False)
        self.assertEqual(obj[mock.Point(235054, 455009)], False)
        self.assertEqual(obj[mock.Point(135054, 355009)], False)
        self.assertEqual(obj[mock.Point(135000, 455600)], False)
        self.assertEqual(obj[mock.Point(134900, 455000)], False)

    def test6_pixel(self):
        "grid elevation model, pixel outside of the grid by row/col."

        obj = AscGrid(mock.Stream(self.data))
        self.assertEqual(obj[3, 20], False)
        self.assertEqual(obj[30, 5], False)

    def test70_reading_from_file(self):
        "reading data from inconsistent file - #205"
        input1 = """\
nCols        5
nRows        3
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
 -999.999 -0.2 0 -9999 3.05
 -99 -9 0 0.5 1.2
 -9999.99 0 0 0 -99999
"""
        obj = AscGrid(mock.Stream(input1))
        self.assertEqual(obj[1, 1], None)
        self.assertEqual(obj[1, 2], -99)
        self.assertEqual(obj[2, 2], -9)
        self.assertEqual(obj[1, 3], None)
        self.assertEqual(obj[4, 1], None)
        self.assertEqual(obj[5, 1], 3.05)
        self.assertEqual(obj[5, 3], None)


class GridModifyingContent(unittest.TestCase):
    data = """\
nCols        5
nRows        5
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
 -999 -0.2 0 -999 3.05
 -999 0 0 0.5 1.2
 -999 0 0 0 -999
 0 0 0 0 -999
 -999 1.1 1.4 0.1 0
"""

    def test1_setPixelValue(self):
        "set pixel value, to valid pixel by row/col"

        obj = AscGrid(mock.Stream(self.data))
        self.assertEqual(obj[2, 1], -0.2)
        obj[2, 1] = -0.1
        self.assertEqual(obj[2, 1], -0.1)

    def test2_setPixelValue(self):
        "setting pixel out of grid raises IndexError - geo"

        obj = AscGrid(mock.Stream(self.data))
        self.assertEqual(obj[100000, 455000], False)
        self.assertRaises(IndexError, obj.__setitem__, (100000, 455000), 1)

    def test3_setPixelValue(self):
        "setting pixel out of grid raises IndexError - row/col"

        obj = AscGrid(mock.Stream(self.data))
        self.assertEqual(obj[3, 20], False)
        self.assertRaises(IndexError, obj.__setitem__, (3, 20), 1)

    def test31_setPixelValue(self):
        "setting pixel out of grid raises IndexError - row/col"

        obj = AscGrid(mock.Stream(self.data))
        self.assertEqual(obj[3, 0], False)
        self.assertRaises(IndexError, obj.__setitem__, (3, 0), 1)

    def test5_setPixelValue(self):
        "setting valid pixel as invalid alters grid shape"

        obj = AscGrid(mock.Stream(self.data))
        self.assertEqual(obj[2, 1], -0.2)
        obj[2, 1] = None
        self.assertEqual(obj[2, 1], None)

    def test6_setPixelValue(self):
        "setting invalid pixel as valid alters grid shape"

        obj = AscGrid(mock.Stream(self.data))
        self.assertEqual(obj[1, 3], None)
        obj[1, 3] = 1
        self.assertEqual(obj[1, 3], 1)


class GridWritingToStream(unittest.TestCase):
    data_str = """\
nCols        5
nRows        5
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
 -999 -0.2 0 -999 3.05
 -999 0 0 0.5 1.2
 -999 0 0 0 -999
 0 0 0 0 -999
 -999 1.1 1.4 0.1 0
"""
    output_str = """\
nCols        5
nRows        5
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
 -999 -0.1 0 -999 1.05
 -999 0 0 0.5 0.9
 -999 0 0 0 -999
 0 0 0 0 -999
 -999 1.1 1.4 0.1 0
"""
    outputfloat_str = """\
nCols        5
nRows        5
xllCorner    135000.1
yllCorner    455000.01
CellSize     0.5
nodata_value -999
 -999 -0.2 0 -999 3.05
 -999 0 0 0.5 1.2
 -999 0 0 0 -999
 0 0 0 0 -999
 -999 1.1 1.4 0.1 0
"""

    def test1_writeUnaltered(self):
        "writing to stream, unaltered"
        obj = AscGrid(mock.Stream(self.data_str))
        output = mock.Stream()
        obj.writeToStream(output)
        self.assertEqual(''.join(output.content), self.data_str)

    def test2_writeAltered(self):
        "writing to stream, after altering some values"
        obj = AscGrid(mock.Stream(self.data_str))
        obj[2, 1] = -0.1
        obj[5, 1] = 1.05
        obj[4, 2] = 0.5
        obj[5, 2] = 0.9
        output = mock.Stream()
        obj.writeToStream(output)
        self.assertEqual(''.join(output.content), self.output_str)

    def test3_writeAltered(self):
        "writing to stream, non integer grid"
        obj = AscGrid(mock.Stream(self.data_str))
        obj.xllcorner += 0.1
        obj.yllcorner += 0.01
        obj.cellsize = 0.5
        output = mock.Stream()
        obj.writeToStream(output)
        self.assertEqual(''.join(output.content), self.outputfloat_str)

    def test70writing(self):
        "writing to a zip archive gives CRLF line terminators"
        obj = AscGrid(mock.Stream(self.data_str))
        output = mock.ZipFile()
        obj.writeToStream(output, 'name.asc')
        self.assertEqual(''.join(output.content), self.data_str.replace('\n', '\r\n'))

    def test71writing(self):
        "writing to a zip archive goes per default into grid/ dir"
        obj = AscGrid(mock.Stream(self.data_str))
        output = mock.ZipFile()
        obj.writeToStream(output, 'name.asc')
        self.assertEqual(output.namelist(), ['grid/name.asc'])

    def test72writing(self):
        "writing to a zip archive explicitly to root dir"
        obj = AscGrid(mock.Stream(self.data_str))
        output = mock.ZipFile()
        obj.writeToStream(output, '/name.asc')
        self.assertEqual(output.namelist(), ['name.asc'])

    def test76writing(self):
        "writing to a zip archive with explicit location"
        obj = AscGrid(mock.Stream(self.data_str))
        output = mock.ZipFile()
        obj.writeToStream(output, 'grid/name.asc')
        self.assertEqual(output.namelist(), ['grid/name.asc'])

    def test78writing(self):
        "writing to a zip archive with explicit list location"
        obj = AscGrid(mock.Stream(self.data_str))
        output = mock.ZipFile()
        obj.writeToStream(output, ['0', '1', '2', 'name.asc'])
        self.assertEqual(output.namelist(), ['0/1/2/name.asc'])


class CoordsConversion(unittest.TestCase):
    data = """\
nCols        5
nRows        5
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
 -999 -0.2 0 -999 3.05
 -999 0 0 0.5 1.2
 -999 0 0 0 -999
 0 0 0 0 -999
 -999 1.1 1.4 0.1 0
"""

    def test1_getPixel(self):
        "get sobek coords of pixel containing a given point"

        obj = AscGrid(mock.Stream(self.data))
        self.assertEqual(obj.get_col_row((135050, 455450)), (1, 1))
        self.assertEqual(obj.get_col_row((135178, 455089)), (2, 5))

    def test2_getPixel(self):
        "get geographical coords of middle point for pixel"

        obj = AscGrid(mock.Stream(self.data))
        self.assertEqual(obj.point((1, 1)), (135050, 455450))
        self.assertEqual(obj.point((2, 5)), (135150, 455050))

    def test3_getPixel(self):
        "get geographical coords of point for pixel, in % from lower left"

        obj = AscGrid(mock.Stream(self.data))
        self.assertEqual(obj.point((1, 1), (0.5, 0.5)), (135050, 455450))
        self.assertEqual(obj.point((2, 5), (0.78, 0.89)), (135178, 455089))

    def test4_getPixel(self):
        "get geographical coords of point in invalid pixel raises ValueError"

        obj = AscGrid(mock.Stream(self.data))
        self.assertRaises(ValueError, obj.point, (100050, 455450))

    def test5_getPixel(self):
        "get geographical coords of point in invalid pixel raises ValueError"

        obj = AscGrid(mock.Stream(self.data))
        self.assertRaises(ValueError, obj.point, (1, 45))


class ListFromIncFile(unittest.TestCase):

    data = """\
INC1.0
DOMAIN                        NUMBER   ID
                                 1   '24                                      '
MAIN DIMENSIONS                MMAX  NMAX
                               6   4
GRID                           DX      DY      X0      Y0
                               100.00     100.00   135050.00  455050.00
domain                        END
START TIME T0: 1991.01.07 00:00:00
CLASSES OF INCREMENTAL FILE    Waterdepth(m) Velocity(m/s)  Waterlevel(m) U-velocity(m/s)  V-velocity(m/s)
                                   0.500     -999     -999     -999     -999
                                   1.000     -999     -999     -999     -999
                                   2.000     -999     -999     -999     -999
ENDCLASSES
.000000 0 1 1
3 1 1
4 1 1
.500000 0 1 1
2 1 1
3 1 2
4 1 3
5 1 2
3 2 1
4 2 1
5 2 1
1.000000 0 1 1
1 1 2
2 1 3
3 1 3
5 1 3
6 1 1
1 2 1
2 2 1
5 2 3
5 3 3
1.500000 0 1 1
5 2 2
6 2 1
5 3 2
6 3 1
5 4 1
2.010000 0 1 1
1 1 1
2 1 2
3 1 2
4 1 2
5 1 2
6 1 2
1 2 2
2 2 2
3 2 2
4 2 2
1 3 1
3 3 1
4 3 1
 2.500000 0 1 1
2 1 1
3 1 1
4 1 1
5 1 1
6 1 1
1 2 1
2 2 1
3 2 1
4 2 1
5 2 1
2 3 1
5 3 1
3 4 1
4 4 1
"""

    output = [(0, """\
nCols        6
nRows        4
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
 -999 -999 -999 -999 -999 -999
 -999 -999 -999 -999 -999 -999
 -999 -999 -999 -999 -999 -999
 -999 -999 0.5 0.5 -999 -999
"""),
              (0.5, """\
nCols        6
nRows        4
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
 -999 -999 -999 -999 -999 -999
 -999 -999 -999 -999 -999 -999
 -999 -999 0.5 0.5 0.5 -999
 -999 0.5 1 2 1 -999
"""),
              (1, """\
nCols        6
nRows        4
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
 -999 -999 -999 -999 -999 -999
 -999 -999 -999 -999 2 -999
 0.5 0.5 0.5 0.5 2 -999
 1 2 2 2 2 0.5
"""),
              (1.5, """\
nCols        6
nRows        4
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
 -999 -999 -999 -999 0.5 -999
 -999 -999 -999 -999 1 0.5
 0.5 0.5 0.5 0.5 1 0.5
 1 2 2 2 2 0.5
"""),
              (2.01, """\
nCols        6
nRows        4
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
 -999 -999 -999 -999 0.5 -999
 0.5 -999 0.5 0.5 1 0.5
 1 1 1 1 1 0.5
 0.5 1 1 1 1 1
"""),
              (2.5, """\
nCols        6
nRows        4
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
 -999 -999 0.5 0.5 0.5 -999
 0.5 0.5 0.5 0.5 0.5 0.5
 0.5 0.5 0.5 0.5 0.5 0.5
 0.5 0.5 0.5 0.5 0.5 0.5
"""),
              ]

    output_hour = [(0, """\
nCols        6
nRows        4
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
 -999 -999 -999 -999 -999 -999
 -999 -999 -999 -999 -999 -999
 -999 -999 -999 -999 -999 -999
 -999 -999 0.5 0.5 -999 -999
"""),
                   (1, """\
nCols        6
nRows        4
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
 -999 -999 -999 -999 -999 -999
 -999 -999 -999 -999 2 -999
 0.5 0.5 0.5 0.5 2 -999
 1 2 2 2 2 0.5
"""),
                   (2.01, """\
nCols        6
nRows        4
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
 -999 -999 -999 -999 0.5 -999
 0.5 -999 0.5 0.5 1 0.5
 1 1 1 1 1 0.5
 0.5 1 1 1 1 1
"""),
                   ]

    input0 = """\
INC1.0
DOMAIN                        NUMBER   ID
                                 1   '24                                      '
MAIN DIMENSIONS                MMAX  NMAX
                               6   4
GRID                           DX      DY      X0      Y0
                               100.00     100.00   135050.00  455050.00
domain                        END
START TIME T0: 1991.01.07 00:00:00
CLASSES OF INCREMENTAL FILE    Waterdepth(m) Velocity(m/s)  Waterlevel(m) U-velocity(m/s)  V-velocity(m/s)
                                   0.500     -999     -999     -999     -999
                                   1.000     -999     -999     -999     -999
                                   2.000     -999     -999     -999     -999
ENDCLASSES
.000000 0 1 1
3 1 1
4 1 1
3 2 0
.100000 0 1 1
3 1 0
"""

    output00 = """\
nCols        6
nRows        4
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
 -999 -999 -999 -999 -999 -999
 -999 -999 -999 -999 -999 -999
 -999 -999 0 -999 -999 -999
 -999 -999 0.5 0.5 -999 -999
"""
    output01 = """\
nCols        6
nRows        4
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
 -999 -999 -999 -999 -999 -999
 -999 -999 -999 -999 -999 -999
 -999 -999 0 -999 -999 -999
 -999 -999 0 0.5 -999 -999
"""

    def test10(self):
        "inc - shape of grid"

        data = mock.Stream(self.data)
        asclist = AscGrid.listFromStream(data)
        self.assertEqual(len(asclist), 6)
        for timestamp, item in asclist:
            self.assertEqual(item.ncols, 6)
        for timestamp, item in asclist:
            self.assertEqual(item.nrows, 4)

    def test12(self):
        "inc - counting list of AscGrid objects"

        data = mock.Stream(self.data)
        asclist = AscGrid.listFromStream(data, just_count=True)
        self.assertEqual(asclist, 6)

    def test13(self):
        "inc - counting list of AscGrid objects, one per hour"

        data = mock.Stream(self.data)
        asclist = AscGrid.listFromStream(data, oneperhour=True, just_count=True)
        self.assertEqual(asclist, 3)

    def test14(self):
        "inc - counting asc data, returning one"

        data = mock.Stream(self.output[0][1])
        asclist = AscGrid.listFromStream(data, just_count=True)
        self.assertEqual(asclist, 1)

    def test20(self):
        "inc - reading list of AscGrid objects"

        data = mock.Stream(self.data)
        asclist = AscGrid.listFromStream(data)
        self.assertEqual(len(asclist), 6)
        for i in range(6):
            output = mock.Stream()
            asclist[i][1].writeToStream(output)
            self.assertEqual((i, asclist[i][0]), (i, self.output[i][0]))
            self.assertEqual((i, ''.join(output.content)), (i, self.output[i][1]))

    def test21(self):
        "inc - reading list of AscGrid objects - class '0' means hard coded 0.000"

        data = mock.Stream(self.input0)
        asclist = AscGrid.listFromStream(data)
        self.assertEqual(len(asclist), 2)
        output = mock.Stream()
        asclist[0][1].writeToStream(output)
        self.assertEqual(''.join(output.content), self.output00)
        output = mock.Stream()
        asclist[1][1].writeToStream(output)
        self.assertEqual(''.join(output.content), self.output01)

    def test23(self):
        "inc - reading list of AscGrid objects, DOS-separators"

        data = mock.Stream(self.data.replace('\n', '\r\n'))
        asclist = AscGrid.listFromStream(data)
        self.assertEqual(len(asclist), 6)
        for i in range(6):
            output = mock.Stream()
            asclist[i][1].writeToStream(output)
            self.assertEqual((i, asclist[i][0]), (i, self.output[i][0]))
            self.assertEqual((i, ''.join(output.content)), (i, self.output[i][1]))

    def test25(self):
        "inc - reading list of AscGrid objects to zipfile"

        data = mock.Stream(self.data)
        output = mock.ZipFile()
        step, asclist = AscGrid.listFromStream(data, output)
        self.assertEqual(asclist, 6)
        self.assertEqual('!!!'.join(output.content), '!!!'.join([i[1] for i in self.output]).replace('\n', '\r\n'))
        self.assertEqual(output.names[0], 'grid/0000.asc')
        self.assertEqual(output.names[5], 'grid/0005.asc')
        self.assertEqual(step, 0.5)

    def test26(self):
        "inc - reading list of AscGrid objects to zipfile, by name"

        data = mock.Stream(self.data)
        output = mock.ZipFile()
        step, asclist = AscGrid.listFromStream(data, output, "/tst%05d.asc")
        self.assertEqual(asclist, 6)
        self.assertEqual('!!!'.join(output.content), '!!!'.join([i[1] for i in self.output]).replace('\n', '\r\n'))
        self.assertEqual(output.names[0], 'tst00000.asc')
        self.assertEqual(output.names[5], 'tst00005.asc')

    def test30(self):
        "inc - reading list of AscGrid objects, one per hour"

        data = mock.Stream(self.data)
        asclist = AscGrid.listFromStream(data, oneperhour=True)
        self.assertEqual(len(asclist), 3)
        for i in range(3):
            output = mock.Stream()
            asclist[i][1].writeToStream(output)
            self.assertEqual((i, asclist[i][0]), (i, self.output_hour[i][0]))
            self.assertEqual((i, ''.join(output.content)), (i, self.output_hour[i][1]))

    def test40(self):
        "inc - accepting asc data, returning one AscGrid"

        data = mock.Stream(self.output[0][1])
        asclist = AscGrid.listFromStream(data)
        self.assertEqual(len(asclist), 1)
        output = mock.Stream()
        asclist[0][1].writeToStream(output)
        self.assertEqual(''.join(output.content), self.output[0][1])

    def test50(self):
        "inc - reading list of AscGrid objects, one per hour, using generator"

        data = mock.Stream(self.data)
        asclist = AscGrid.xlistFromStream(data, oneperhour=True)
        for i in range(3):
            output = mock.Stream()
            obj = asclist.next()
            obj[1].writeToStream(output)
            self.assertEqual((i, obj[0]), (i, self.output_hour[i][0]))
            self.assertEqual((i, ''.join(output.content)), (i, self.output_hour[i][1]))
        self.assertRaises(StopIteration, asclist.next)

    def test53(self):
        "inc - accepting asc data, returning one AscGrid, using generator"

        data = mock.Stream(self.output[0][1])
        asclist = AscGrid.xlistFromStream(data)
        output = mock.Stream()
        obj = asclist.next()
        obj[1].writeToStream(output)
        self.assertEqual(''.join(output.content), self.output[0][1])
        self.assertRaises(StopIteration, asclist.next)

    def test56(self):
        "inc - reading list of AscGrid objects, using generator"

        data = mock.Stream(self.data)
        asclist = AscGrid.xlistFromStream(data)
        for i in range(6):
            output = mock.Stream()
            obj = asclist.next()
            obj[1].writeToStream(output)
            self.assertEqual((i, obj[0]), (i, self.output[i][0]))
            self.assertEqual((i, ''.join(output.content)), (i, self.output[i][1]))
        self.assertRaises(StopIteration, asclist.next)


class ListFromFLSIncFile(unittest.TestCase):
    data = """\
/* run: 38da1, created at: 18:33:11, 23- 1-2003, time =    78.00     DELFT-FLS version 2.55, 14-july-2001
MAIN DIMENSIONS                  MMAX    NMAX
                                6   4
GRID                           DX    X0       Y0
                                   100.00   135050.00  455050.00
CLASSES OF INCREMENTAL FILE    H       C       Z       U       V
                                  0.500     -999     -999     -999     -999
                                   1.000     -999     -999     -999     -999
                                   2.000     -999     -999     -999     -999
ENDCLASSES
0.000 0 1
3 1 1
4 1 1
.500000 0 1
2 1 1
3 1 2
4 1 3
5 1 2
3 2 1
4 2 1
5 2 1
1.000000 0 1
1 1 2
2 1 3
3 1 3
5 1 3
6 1 1
1 2 1
2 2 1
5 2 3
5 3 3
1.500000 0 1
5 2 2
6 2 1
5 3 2
6 3 1
5 4 1
2.000000 0 1
1 1 1
2 1 2
3 1 2
4 1 2
5 1 2
6 1 2
1 2 2
2 2 2
3 2 2
4 2 2
1 3 1
3 3 1
4 3 1
 2.500000 0 1
2 1 1
3 1 1
4 1 1
5 1 1
6 1 1
1 2 1
2 2 1
3 2 1
4 2 1
5 2 1
2 3 1
5 3 1
3 4 1
4 4 1
"""
    output = ["""\
nCols        6
nRows        4
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
 %(v)s %(v)s %(v)s %(v)s %(v)s %(v)s
 %(v)s %(v)s %(v)s %(v)s %(v)s %(v)s
 %(v)s %(v)s %(v)s %(v)s %(v)s %(v)s
 %(v)s %(v)s 0.5 0.5 %(v)s %(v)s
""",
                  """\
nCols        6
nRows        4
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
 %(v)s %(v)s %(v)s %(v)s %(v)s %(v)s
 %(v)s %(v)s %(v)s %(v)s %(v)s %(v)s
 %(v)s %(v)s 0.5 0.5 0.5 %(v)s
 %(v)s 0.5 1 2 1 %(v)s
""",
                  """\
nCols        6
nRows        4
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
 %(v)s %(v)s %(v)s %(v)s %(v)s %(v)s
 %(v)s %(v)s %(v)s %(v)s 2 %(v)s
 0.5 0.5 0.5 0.5 2 %(v)s
 1 2 2 2 2 0.5
""",
                  """\
nCols        6
nRows        4
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
 %(v)s %(v)s %(v)s %(v)s 0.5 %(v)s
 %(v)s %(v)s %(v)s %(v)s 1 0.5
 0.5 0.5 0.5 0.5 1 0.5
 1 2 2 2 2 0.5
""",
                  """\
nCols        6
nRows        4
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
 %(v)s %(v)s %(v)s %(v)s 0.5 %(v)s
 0.5 %(v)s 0.5 0.5 1 0.5
 1 1 1 1 1 0.5
 0.5 1 1 1 1 1
""",
                  """\
nCols        6
nRows        4
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
 %(v)s %(v)s 0.5 0.5 0.5 %(v)s
 0.5 0.5 0.5 0.5 0.5 0.5
 0.5 0.5 0.5 0.5 0.5 0.5
 0.5 0.5 0.5 0.5 0.5 0.5
""",
              ]

    def test400(self):
        "FLS inc - shape of grid"

        data = mock.Stream(self.data)
        asclist = AscGrid.listFromStream(data)
        self.assertEqual(len(asclist), 6)
        for timestamp, item in asclist:
            self.assertEqual(item.ncols, 6)
        for timestamp, item in asclist:
            self.assertEqual(item.nrows, 4)

    def test401(self):
        "FLS - counting list of AscGrid objects"

        data = mock.Stream(self.data)
        asclist = AscGrid.listFromStream(data, just_count=True)
        self.assertEqual(asclist, 6)

    def test410(self):
        "FLS - reading list of AscGrid objects"

        data = mock.Stream(self.data)
        asclist = AscGrid.listFromStream(data)
        self.assertEqual(len(asclist), 6)
        for i in range(6):
            output = mock.Stream()
            asclist[i][1].writeToStream(output)
            self.assertEqual(''.join(output.content), self.output[i] % {'v': -999})

    def test412(self):
        "FLS - reading list of AscGrid objects with default value"

        data = mock.Stream(self.data)
        asclist = AscGrid.listFromStream(data, default_value=-5)
        self.assertEqual(len(asclist), 6)
        for i in range(6):
            output = mock.Stream()
            asclist[i][1].writeToStream(output)
            self.assertEqual(''.join(output.content), self.output[i] % {'v': -5})

    def test42(self):
        "FLS - reading list of AscGrid objects to zipfile"

        data = mock.Stream(self.data)
        output = mock.ZipFile()
        step, asclist = AscGrid.listFromStream(data, output)
        self.assertEqual(asclist, 6)
        self.assertEqual('!!!'.join(output.content), '!!!'.join(self.output).replace('\n', '\r\n') % {'v': -999})
        self.assertEqual(output.names[0], 'grid/0000.asc')
        self.assertEqual(output.names[5], 'grid/0005.asc')
        self.assertEqual(step, 0.5)

    def test43(self):
        "FLS - reading list of AscGrid objects to zipfile, by name"

        data = mock.Stream(self.data)
        output = mock.ZipFile()
        step, asclist = AscGrid.listFromStream(data, output, "/tst%05d.asc")
        self.assertEqual(asclist, 6)
        self.assertEqual('!!!'.join(output.content), '!!!'.join(self.output).replace('\n', '\r\n') % {'v': -999})
        self.assertEqual(output.names[0], 'tst00000.asc')
        self.assertEqual(output.names[5], 'tst00005.asc')


class TestColorMapping(unittest.TestCase):
    data = """\
leftbound,colour
0,FEE1E1
0.8,FE5956
0.9,FE4A47
2.3,860200
"""

    def test000_readingFromFile(self):
        "ColorMapping read from file"
        obj = ColorMapping(mock.Stream(self.data))
        self.assertEqual(len(obj.values), 4)
        self.assertEqual(obj.values[0], (0, (0xFE, 0xE1, 0xE1)))
        self.assertEqual(obj.values[-1], (2.3, (0x86, 0x02, 0x00)))

    def test100_getColorFromValue(self):
        "ColorMapping associates colour to a value - inside extremes"

        obj = ColorMapping(mock.Stream(self.data))
        self.assertEqual(obj.getColor(0.89), (0xfe, 0x59, 0x56))
        self.assertEqual(obj.getColor(0.91), (0xfe, 0x4a, 0x47))

    def test110_getColorFromValue(self):
        "ColorMapping associates colour to a value - left bounds go to previous color"

        obj = ColorMapping(mock.Stream(self.data))
        self.assertEqual(obj.getColor(0.8), (0xFE, 0xE1, 0xE1))
        self.assertEqual(obj.getColor(0.9), (0xFE, 0x59, 0x56))
        self.assertEqual(obj.getColor(2.3), (0xFE, 0x4A, 0x47))
        self.assertEqual(obj.getColor(0.0), (0x00, 0x00, 0x00))

    def test115_getColorFromValue(self):
        "ColorMapping associates colour to higher bound for all values above that"

        obj = ColorMapping(mock.Stream(self.data))
        self.assertEqual(obj.getColor(5), (0x86, 0x02, 0x00))
        self.assertEqual(obj.getColor(50), (0x86, 0x02, 0x00))
        self.assertEqual(obj.getColor(500), (0x86, 0x02, 0x00))

    def test120_getColorFromValue(self):
        "ColorMapping associates black to values less than lower bound"

        obj = ColorMapping(mock.Stream(self.data))
        self.assertEqual(obj.getColor(-49), (0x00, 0x00, 0x00))

    def test130_getColorFromValue(self):
        "ColorMapping associates black to None"

        obj = ColorMapping(mock.Stream(self.data))
        self.assertEqual(obj.getColor(None), (0x00, 0x00, 0x00))

    def test140_cantInitializeFromFileName(self):
        "ColorMapping cannot be initialized from a file name (AttributeError)"

        self.assertRaises(AttributeError, ColorMapping, "some_file_name")


class ImageConversion(unittest.TestCase):
    data = """\
/* run: 38da1, created at: 18:33:11, 23- 1-2003, time =    78.00     DELFT-FLS version 2.55, 14-july-2001
MAIN DIMENSIONS                  MMAX    NMAX
                                6   4
GRID                           DX    X0       Y0
                                   100.00   135050.00  455050.00
CLASSES OF INCREMENTAL FILE    H       C       Z       U       V
                                   1.000     -999     -999     -999     -999
                                   2.000     -999     -999     -999     -999
                                   3.000     -999     -999     -999     -999
                                   4.000     -999     -999     -999     -999
ENDCLASSES
0.000 0 1
3 3 0
3 1 1
4 1 1
.500000 0 1
2 1 1
3 1 2
4 1 3
5 1 2
3 2 1
4 2 1
5 2 1
1.000000 0 1
1 1 2
2 1 3
3 1 4
5 1 3
6 1 1
1 2 1
2 2 1
5 2 3
5 3 3
1.500000 0 1
5 2 2
6 2 1
5 3 2
6 3 1
5 4 1
2.000000 0 1
1 1 1
2 1 2
3 1 2
4 1 2
5 1 2
6 1 2
1 2 2
2 2 2
3 2 2
4 2 2
1 3 1
3 3 1
4 3 1
 2.500000 0 1
2 1 1
3 1 1
4 1 1
5 1 1
6 1 1
1 2 1
2 2 1
3 2 1
4 2 1
5 2 1
2 3 1
5 3 1
3 4 1
4 4 1
"""
    colors = """\
leftbound,colour
0,FEE1E1
1,FE5906
2,0EFA07
3,8602F0
"""

    def test51(self):
        "FLS - reading list of AscGrid objects - converting to RGBA images"
        colors = ColorMapping(mock.Stream(self.colors))
        data = mock.Stream(self.data)
        asclist = AscGrid.listFromStream(data)
        self.assertEqual(len(asclist), 6)
        expectAt = {
            # pixel-array-category
            # (2,1)-[3,3]-(000011)
            (2, 1): [(0x00, 0x00, 0x00, 0x00),  # 0
                     (0x00, 0x00, 0x00, 0x00),  # 0
                     (0x00, 0x00, 0x00, 0x00),  # 0
                     (0x00, 0x00, 0x00, 0x00),  # 0
                     (0xfe, 0xe1, 0xe1, 0xff),  # 1
                     (0xfe, 0xe1, 0xe1, 0xff),  # 1
                     ],
            # pixel-array-category
            # (4,2)-[5,2]-(013221)
            (4, 2): [(0x00, 0x00, 0x00, 0x00),  # 0
                     (0xfe, 0xe1, 0xe1, 0xff),  # 1
                     (0x0e, 0xfa, 0x07, 0xff),  # 3
                     (0xfe, 0x59, 0x06, 0xff),  # 2
                     (0xfe, 0x59, 0x06, 0xff),  # 2
                     (0xfe, 0xe1, 0xe1, 0xff),  # 1
                     ],
            # pixel-array-category
            # (2,3)-[3,1]-(124421)
            (2, 3): [(0xfe, 0xe1, 0xe1, 0xff),  # 1
                     (0xfe, 0x59, 0x06, 0xff),  # 2
                     (0x86, 0x02, 0xf0, 0xff),  # 4
                     (0x86, 0x02, 0xf0, 0xff),  # 4
                     (0xfe, 0x59, 0x06, 0xff),  # 2
                     (0xfe, 0xe1, 0xe1, 0xff),  # 1
                     ],
            }
        for i in range(6):
            image = asclist[i][1].asImage(colors, bits=24)
            self.assertEqual(image.mode, "RGBA")
            for coords, expected_colors in expectAt.items():
                self.assertEqual((coords, i, image.getpixel(coords)), (coords, i, expected_colors[i]))

    def test60(self):
        "FLS - reading list of AscGrid objects - converting to paletted images"
        colors = ColorMapping(mock.Stream(self.colors))
        data = mock.Stream(self.data)
        asclist = AscGrid.listFromStream(data)
        self.assertEqual(len(asclist), 6)
        expectAt = {(4, 2): [0, 0, 0, 0, 1, 1, ],
                    (4, 2): [0, 1, 3, 2, 2, 1, ],
                    (2, 3): [1, 2, 4, 4, 2, 1, ],
                    }
        for i in range(6):
            image = asclist[i][1].asImage(colors, bits=8)
            self.assertEqual(image.mode, "P")
            for coords, expected_colors in expectAt.items():
                self.assertEqual((coords, image.getpixel(coords)), (coords, expected_colors[i]))

    def test80(self):
        "FLS - reading list of AscGrid objects - converting to paletted images - buffered"
        colors = ColorMapping(mock.Stream(self.colors))
        data = mock.Stream(self.data)
        asclist = AscGrid.listFromStream(data)
        self.assertEqual(len(asclist), 6)
        expectAt = {(4, 2): [0, 0, 0, 0, 1, 1, ],
                    (4, 2): [0, 1, 3, 2, 2, 1, ],
                    (2, 3): [1, 2, 4, 4, 2, 1, ],
                    }
        for i in range(6):
            image = asclist[i][1].asImage(colors, bits=8)  # buffering
            image = asclist[i][1].asImage(colors, bits=8)  # using
            self.assertEqual(image.mode, "P")
            for coords, expected_colors in expectAt.items():
                self.assertEqual((coords, image.getpixel(coords)), (coords, expected_colors[i]))


class CanPickleGrid(unittest.TestCase):
    data = """\
nCols        5
nRows        5
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
 -999 -0.2 0 -999 3.05
 -999 0 0 0.5 1.2
 -999 0 0 0 -999
 0 0 0 0 -999
 -999 1.1 1.4 0.1 0
"""
    colors = """\
leftbound,colour
0.0,FEE1E1
1.0,FE5906
2.0,0EFA07
3.0,8602F0
"""

    def test00(self):
        "can pickle AscGrid without an image"
        out = mock.Stream()
        obj = AscGrid(mock.Stream(self.data))
        import pickle
        pickle.dump(obj, out)

    def test01(self):
        "can pickle AscGrid with/ an image"

        out = mock.Stream()
        obj = AscGrid(mock.Stream(self.data))
        colors = ColorMapping(mock.Stream(self.colors))
        obj.asImage(colors, bits=8)
        import pickle
        pickle.dump(obj, out)


class CanHandleTripleStars(unittest.TestCase):
    data = """\
/* run: 38da1, created at: 18:33:11, 23- 1-2003, time =    78.00     DELFT-FLS version 2.55, 14-july-2001
MAIN DIMENSIONS                  MMAX    NMAX
                                ***   4
GRID                           DX    X0       Y0
                                   100.00   135050.00  455050.00
CLASSES OF INCREMENTAL FILE    H       C       Z       U       V
                                  0.500     -999     -999     -999     -999
                                   1.000     -999     -999     -999     -999
                                   2.000     -999     -999     -999     -999
ENDCLASSES
0.000 0 1
3 1 1
4 1 1
.500000 0 1
2 1 1
3 1 2
4 1 3
5 1 2
3 2 1
4 2 1
5 2 1
1.000000 0 1
1 1 2
2 1 3
3 1 3
5 1 3
6 1 1
1 2 1
2 2 1
5 2 3
5 3 3
"""

    def test400(self):
        "can count even with *** and no extra knowledge"

        data = mock.Stream(self.data)
        asclist = AscGrid.listFromStream(data, just_count=True)
        self.assertEqual(asclist, 3)

    def test410(self):
        "can read *** if a default is given"

        data = mock.Stream(self.data)
        default_grid = mock.Object(ncols=10)
        asclist = AscGrid.listFromStream(data, default_grid=default_grid)
        self.assertEqual(len(asclist), 3)
        for timestamp, item in asclist:
            self.assertEqual(item.ncols, 10)
        for timestamp, item in asclist:
            self.assertEqual(item.nrows, 4)

    def test420(self):
        "without a default *** causes a TypeError"

        data = mock.Stream(self.data)
        self.assertRaises(TypeError, AscGrid.listFromStream, data)


class CalculateDotIncMaximumDifference(unittest.TestCase):
    data = """\
/* run: 38da1, created at: 18:33:11, 23- 1-2003, time =    78.00     DELFT-FLS version 2.55, 14-july-2001
MAIN DIMENSIONS                  MMAX    NMAX
                                  6   4
GRID                           DX    X0       Y0
                                   100.00   135050.00  455050.00
CLASSES OF INCREMENTAL FILE    H       C       Z       U       V
                                  0.500     -999     -999     -999     -999
                                   1.000     -999     -999     -999     -999
                                   2.000     -999     -999     -999     -999
ENDCLASSES
0.000 0 1
3 1 1
4 1 1
.500000 0 1
2 1 1
3 1 2
4 1 3
5 1 2
3 2 1
4 2 1
5 2 1
1.000000 0 1
1 1 2
2 1 2
3 1 3
5 1 3
6 1 1
1 2 1
2 2 1
5 2 3
5 3 3
"""
    outputNN = """\
nCols        6
nRows        4
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
-999 -999 -999 -999 -999 -999
-999 -999 -999 -999 2.0 -999
0.5 0.5 0.5 0.5 2.0 -999
1.0 1.0 2.0 2.0 2.0 0.5
"""
    outputN0 = """\
nCols        6
nRows        4
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
-999 -999 -999 -999 -999 -999
-999 -999 -999 -999 2.0 -999
0.5 0.5 0.5 0.5 1.5 -999
1.0 0.5 1.0 1.5 1.0 0.5
"""
    output0N = """\
nCols        6
nRows        4
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
0.0 0.0 0.0 0.0 0.0 0.0
0.0 0.0 0.0 0.0 2.0 0.0
0.5 0.5 0.5 0.5 1.5 0.0
1.0 0.5 1.0 1.5 1.0 0.5
"""
    output00 = """\
nCols        6
nRows        4
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
0.0 0.0 0.0 0.0 0.0 0.0
0.0 0.0 0.0 0.0 2.0 0.0
0.5 0.5 0.5 0.5 1.5 0.0
1.0 0.5 1.0 1.5 1.0 0.5
"""

    def test400(self):
        "correct metadata from inc file"

        data = mock.Stream(self.data)
        obj = AscGrid.maxIncrementsFromStream(data)

        self.assertEqual(obj.ncols, 6)
        self.assertEqual(obj.nrows, 4)
        self.assertEqual(obj.xllcorner, 135000)
        self.assertEqual(obj.yllcorner, 455000)
        self.assertEqual(obj.cellsize, 100)
        self.assertEqual(obj.nodata_value, -999)

    def test410(self):
        "maximum increments, from raw sequence"

        data = mock.Stream(self.data)
        obj = AscGrid.maxIncrementsFromStream(data)
        reference = [[None, None, None, None, None, None],
                     [None, None, None, None, 2.0, None],
                     [0.5, 0.5, 0.5, 0.5, 1.5, None],
                     [1.0, 0.5, 1.0, 1.5, 1.0, 0.5],
                     ]

        for col in range(1, obj.ncols + 1):
            for row in range(1, obj.nrows + 1):
                self.assertEqual(obj[col, row], reference[row - 1][col - 1], "[%d,%d]: %s != %s" % (col, row, obj[col, row], reference[row - 1][col - 1], ))

    def test420(self):
        "maximum increments, starts from None, ends in constant grid"

        data = mock.Stream(self.data)
        obj = AscGrid.maxIncrementsFromStream(data, end_in_constant=True)
        reference = AscGrid(mock.Stream(self.outputN0))

        for col in range(1, obj.ncols + 1):
            for row in range(1, obj.nrows + 1):
                self.assertEqual(obj[col, row], reference[col, row], "[%d,%d]: %s != %s" % (col, row, obj[col, row], reference[col, row], ))

    def test430(self):
        "maximum increments, starts from 0.0, ends with last grid"

        data = mock.Stream(self.data)
        obj = AscGrid.maxIncrementsFromStream(data, default_value=0.0)
        reference = AscGrid(mock.Stream(self.output0N))

        for col in range(1, obj.ncols + 1):
            for row in range(1, obj.nrows + 1):
                self.assertEqual(obj[col, row], reference[col, row], "[%d,%d]: %s != %s" % (col, row, obj[col, row], reference[col, row], ))

    def test440(self):
        "maximum increments, starts from 0.0, ends in repeated grid"

        data = mock.Stream(self.data)
        obj = AscGrid.maxIncrementsFromStream(data, default_value=0.0, end_in_constant=True)
        reference = AscGrid(mock.Stream(self.output00))

        for col in range(1, obj.ncols + 1):
            for row in range(1, obj.nrows + 1):
                self.assertEqual(obj[col, row], reference[col, row], "[%d,%d]: %s != %s" % (col, row, obj[col, row], reference[col, row], ))

    def test530(self):
        "maximum increments in time units, ends with last grid"

        data = mock.Stream(self.data)
        obj = AscGrid.maxIncrementsFromStream(data, pertimeunit=True)
        reference = [[None, None, None, None, None, None],
                     [None, None, None, None, 4.0, None],
                     [1.0, 1.0, 1.0, 1.0, 3.0, None],
                     [2.0, 1.0, 1.0, 3.0, 2.0, 1.0],
                     ]

        for col in range(1, obj.ncols + 1):
            for row in range(1, obj.nrows + 1):
                self.assertEqual(obj[col, row], reference[row - 1][col - 1], "[%d,%d]: %s != %s" % (col, row, obj[col, row], reference[row - 1][col - 1], ))

    def test630(self):
        "maximum increments in time units, ends with last grid, grouping per hour"

        data = mock.Stream(self.data)
        obj = AscGrid.maxIncrementsFromStream(data, oneperhour=True, pertimeunit=True)
        reference = [[None, None, None, None, None, None],
                     [None, None, None, None, 2.0, None],
                     [0.5, 0.5, 0.5, 0.5, 2.0, None],
                     [1.0, 1.0, 1.5, 1.5, 2.0, 0.5],
                     ]

        for col in range(1, obj.ncols + 1):
            for row in range(1, obj.nrows + 1):
                self.assertEqual(obj[col, row], reference[row - 1][col - 1], "[%d,%d]: %s != %s" % (col, row, obj[col, row], reference[row - 1][col - 1], ))


class ApplyFunctionToGrids(unittest.TestCase):
    data_inc = """\
/* run: 38da1, created at: 18:33:11, 23- 1-2003, time =    78.00     DELFT-FLS version 2.55, 14-july-2001
MAIN DIMENSIONS                  MMAX    NMAX
                                  6   4
GRID                           DX    X0       Y0
                                   100.00   135050.00  455050.00
CLASSES OF INCREMENTAL FILE    H       C       Z       U       V
                                  0.500     -999     -999     -999     -999
                                   1.000     -999     -999     -999     -999
                                   2.000     -999     -999     -999     -999
ENDCLASSES
0.000 0 1
3 1 1
4 1 1
.500000 0 1
2 1 1
3 1 2
4 1 3
5 1 2
3 2 1
4 2 1
5 2 1
1.000000 0 1
1 1 2
2 1 2
3 1 3
5 1 3
6 1 1
1 2 1
2 2 1
5 2 3
5 3 3
"""
    data_asc = """\
nCols        5
nRows        5
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
 -999 -0.2 0 -999 3.05
 -999 0 0 0.5 1.2
 -999 0 0 0 -999
 0 0 0 0 -999
 -999 1.1 1.4 0.1 0
"""

    def test000(self):
        "result of pixelwise unary function has correct metadata"

        i = AscGrid(mock.Stream(self.data_asc))
        obj = AscGrid.apply(lambda x: x, i)
        self.assertEqual(obj.ncols, 5)
        self.assertEqual(obj.nrows, 5)
        self.assertEqual(obj.xllcorner, 135000)
        self.assertEqual(obj.yllcorner, 455000)
        self.assertEqual(obj.cellsize, 100)
        self.assertEqual(obj.nodata_value, -999)

    def test010(self):
        "doubling pixelwise a 5x5 grid"

        i = AscGrid(mock.Stream(self.data_asc))
        obj = AscGrid.apply(lambda x: 2 * x, i)
        for row in range(1, obj.nrows + 1):
            for col in range(1, obj.ncols + 1):
                if i[col, row] is not None:
                    self.assertEqual(obj[col, row], 2 * i[col, row])
                else:
                    self.assertEqual(obj[col, row], None)

    def test100(self):
        "result of pixelwise binary function has correct metadata"

        i = [i[1] for i in AscGrid.listFromStream(mock.Stream(self.data_inc))]
        obj = AscGrid.apply(lambda x, y: x + y, i[0], i[1])
        self.assertEqual(obj.ncols, 6)
        self.assertEqual(obj.nrows, 4)
        self.assertEqual(obj.xllcorner, 135000)
        self.assertEqual(obj.yllcorner, 455000)
        self.assertEqual(obj.cellsize, 100)
        self.assertEqual(obj.nodata_value, -999)

    def test110(self):
        "adding two 6x4 grids"

        i = [i[1] for i in AscGrid.listFromStream(mock.Stream(self.data_inc))]
        obj = AscGrid.apply(lambda x, y: x + y, i[0], i[1])
        for row in range(1, obj.nrows + 1):
            for col in range(1, obj.ncols + 1):
                if i[0][col, row] is not None and i[1][col, row] is not None:
                    self.assertEqual(obj[col, row], i[0][col, row] + i[1][col, row])
                else:
                    self.assertEqual(obj[col, row], None)


class FirstTimestampWithValue(unittest.TestCase):
    data_inc = """\
/* run: 38da1, created at: 18:33:11, 23- 1-2003, time =    78.00     DELFT-FLS version 2.55, 14-july-2001
MAIN DIMENSIONS                  MMAX    NMAX
                                  6   4
GRID                           DX    X0       Y0
                                   100.00   135050.00  455050.00
CLASSES OF INCREMENTAL FILE    H       C       Z       U       V
                                  0.500     -999     -999     -999     -999
                                   1.000     -999     -999     -999     -999
                                   2.000     -999     -999     -999     -999
                                   0.000     -999     -999     -999     -999
                                   20.000     -999     -999     -999     -999
ENDCLASSES
50.000 0 1
2 1 4
3 1 1
4 1 1
50.500000 0 1
2 1 1
3 1 2
4 1 3
5 1 2
3 2 1
4 2 1
5 2 1
1 4 0
51.000000 0 1
1 1 2
2 1 2
3 1 3
5 1 3
6 1 1
1 2 1
2 2 1
5 2 3
5 3 3
4 1 1
"""
    data_timestamps_gt00_asc = """\
nCols        6
nRows        4
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
 -999 -999 -999 -999 -999 -999
 -999 -999 -999 -999 51 -999
 51 51 50.5 50.5 50.5 -999
 51 50.5 50 50 50.5 51
"""
    data_timestamps_ge05_asc = """\
nCols        6
nRows        4
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
 -999 -999 -999 -999 -999 -999
 -999 -999 -999 -999 51 -999
 51 51 50.5 50.5 50.5 -999
 51 50.5 50 50 50.5 51
"""
    data_timestamps_ge10_asc = """\
nCols        6
nRows        4
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
 -999 -999 -999 -999 -999 -999
 -999 -999 -999 -999 51 -999
 -999 -999 -999 -999 51 -999
 51 51 50.5 50.5 50.5 -999
"""
    data_timestamps_ge15_asc = """\
nCols        6
nRows        4
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
 -999 -999 -999 -999 -999 -999
 -999 -999 -999 -999 51 -999
 -999 -999 -999 -999 51 -999
 -999 -999 51 50.5 51 -999
"""
    data_timestamps_eq00_asc = """\
nCols        6
nRows        4
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
 50.5 -999 -999 -999 -999 -999
 -999 -999 -999 -999 -999 -999
 -999 -999 -999 -999 -999 -999
 -999 50 -999 -999 -999 -999
"""
    data_timestamps_eq05_asc = """\
nCols        6
nRows        4
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
 -999 -999 -999 -999 -999 -999
 -999 -999 -999 -999 -999 -999
 51 51 50.5 50.5 50.5 -999
 -999 50.5 50 50 -999 51
"""
    data_timestamps_eq10_asc = """\
nCols        6
nRows        4
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
 -999 -999 -999 -999 -999 -999
 -999 -999 -999 -999 -999 -999
 -999 -999 -999 -999 -999 -999
 51 51 50.5 -999 50.5 -999
"""
    data_timestamps_eq20_asc = """\
nCols        6
nRows        4
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
 -999 -999 -999 -999 -999 -999
 -999 -999 -999 -999 51 -999
 -999 -999 -999 -999 51 -999
 -999 -999 51 50.5 51 -999
"""
    data_levels_00_asc = """\
nCols        6
nRows        4
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
 -999 -999 -999 -999 -999 -999
 -999 -999 -999 -999 2 -999
 0.5 0.5 0.5 0.5 0.5 -999
 1 0.5 0.5 0.5 1 0.5
"""
    data_levels_10_asc = """\
nCols        6
nRows        4
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
 -999 -999 -999 -999 -999 -999
 -999 -999 -999 -999 2 -999
 -999 -999 -999 -999 2 -999
 1 1 1 2 1 -999
"""
    data_levels_15_asc = """\
nCols        6
nRows        4
xllCorner    135000
yllCorner    455000
CellSize     100
nodata_value -999
 -999 -999 -999 -999 -999 -999
 -999 -999 -999 -999 2 -999
 -999 -999 -999 -999 2 -999
 -999 -999 2 2 2 -999
"""

    def test000(self):
        "xlistFromStream with threshold, check the template"

        received = AscGrid.listFromStream(mock.Stream(self.data_inc), threshold=1.0)
        output = mock.Stream()
        received[0].writeToStream(output)
        self.assertEqual(''.join(output.content), "nCols        6\nnRows        4\nxllCorner    135000\nyllCorner    455000\nCellSize     100\nnodata_value -999\n -999 -999 -999 -999 -999 -999\n -999 -999 -999 -999 -999 -999\n -999 -999 -999 -999 -999 -999\n -999 -999 -999 -999 -999 -999\n")

    def test002(self):
        "xlistFromStream with threshold 1.0"

        received = AscGrid.listFromStream(mock.Stream(self.data_inc), threshold=1.0)
        self.assertEqual(received[1:], [(50.5, {1.0: [(3, 4), (5, 4)],
                                                2.0: [(4, 4)]}),
                                        (51.0, {1.0: [(1, 4), (2, 4)],
                                                2.0: [(5, 3), (5, 2)]})])

    def test004(self):
        "xlistFromStream with threshold 1.5"

        received = AscGrid.listFromStream(mock.Stream(self.data_inc), threshold=1.5)
        self.assertEqual(received[1:], [(50.5, {2.0: [(4, 4)]}),
                                        (51.0, {2.0: [(3, 4), (5, 4), (5, 3), (5, 2)]})])

    def test006(self):
        "xlistFromStream with threshold 0.0"

        received = AscGrid.listFromStream(mock.Stream(self.data_inc), threshold=0.0)
        self.assertEqual(received[1:], [(50.0, {0.5: [(3, 4), (4, 4)]}),
                                        (50.5, {0.5: [(2, 4), (3, 3), (4, 3), (5, 3)],
                                                1.0: [(5, 4)]}),
                                        (51.0, {0.5: [(6, 4), (1, 3), (2, 3)],
                                                1.0: [(1, 4)],
                                                2.0: [(5, 2)]})])

    def test010(self):
        "earliest timestamp for pixel reaching or exceeding value 1.0 (1.0 a possible grid value)"

        received = AscGrid.firstTimestampWithValue(mock.Stream(self.data_inc), threshold=1.0)

        timestamps, levels = received

        output = mock.Stream()
        timestamps.writeToStream(output)
        self.assertEqual(''.join(output.content), self.data_timestamps_ge10_asc)

    def test012(self):
        "first value for pixel reaching or exceeding value 1.0 (1.0 a possible grid value)"

        received = AscGrid.firstTimestampWithValue(mock.Stream(self.data_inc), threshold=1.0)

        timestamps, levels = received

        output = mock.Stream()
        levels.writeToStream(output)
        self.assertEqual(''.join(output.content), self.data_levels_10_asc)

    def test020(self):
        "earliest timestamp for pixel reaching or exceeding value 1.5 (1.5 is not a possible grid value)"

        received = AscGrid.firstTimestampWithValue(mock.Stream(self.data_inc), threshold=1.5)

        timestamps, levels = received

        output = mock.Stream()
        timestamps.writeToStream(output)
        self.assertEqual(''.join(output.content), self.data_timestamps_ge15_asc)

    def test022(self):
        "first value for pixel reaching or exceeding value 1.5 (1.5 is not a possible grid value)"

        received = AscGrid.firstTimestampWithValue(mock.Stream(self.data_inc), threshold=1.5)

        timestamps, levels = received

        output = mock.Stream()
        levels.writeToStream(output)
        self.assertEqual(''.join(output.content), self.data_levels_15_asc)

    def test030(self):
        "earliest timestamp for pixel EXCEEDING value 0.0 (for 0.0 reaching is not enough)"

        received = AscGrid.firstTimestampWithValue(mock.Stream(self.data_inc), threshold=0.0)

        timestamps, levels = received

        output = mock.Stream()
        timestamps.writeToStream(output)
        self.assertEqual(''.join(output.content), self.data_timestamps_gt00_asc)

    def test032(self):
        "first value for pixel EXCEEDING value 0.0 (for 0.0 reaching is not enough)"

        received = AscGrid.firstTimestampWithValue(mock.Stream(self.data_inc), threshold=0.0)

        timestamps, levels = received

        output = mock.Stream()
        levels.writeToStream(output)
        self.assertEqual(''.join(output.content), self.data_levels_00_asc)

    def test100(self):
        "list timestamps for pixel taking on each class value, with repetitions"

        received = AscGrid.listFromStream(mock.Stream(self.data_inc), threshold=False)
        self.assertEqual(received[1:], [(50.0, {0.0: [(2, 4)],
                                                0.5: [(3, 4), (4, 4)]}),
                                        (50.5, {0.0: [(1, 1)],
                                                0.5: [(2, 4), (3, 3), (4, 3), (5, 3)],
                                                1.0: [(3, 4), (5, 4)],
                                                2.0: [(4, 4)]}),
                                        (51.0, {0.5: [(6, 4), (1, 3), (2, 3), (4, 4)],
                                                1.0: [(1, 4), (2, 4)],
                                                2.0: [(3, 4), (5, 4), (5, 3), (5, 2)]})])

    def test104(self):
        "list of timestamps for pixel taking on each class value, no repetitions"

        received = AscGrid.listFromStream(mock.Stream(self.data_inc), threshold=True)
        self.assertEqual(received[1:], [(50.0, {0.0: [(2, 4)],
                                                0.5: [(3, 4), (4, 4)]}),
                                        (50.5, {0.0: [(1, 1)],
                                                0.5: [(2, 4), (3, 3), (4, 3), (5, 3)],
                                                1.0: [(3, 4), (5, 4)],
                                                2.0: [(4, 4)]}),
                                        (51.0, {0.5: [(6, 4), (1, 3), (2, 3)],
                                                1.0: [(1, 4), (2, 4)],
                                                2.0: [(3, 4), (5, 4), (5, 3), (5, 2)]})])

    def test120(self):
        "grids with first timestamps for each class value"

        expected = [(0.0, self.data_timestamps_eq00_asc),
                    (0.5, self.data_timestamps_eq05_asc),
                    (1.0, self.data_timestamps_eq10_asc),
                    (2.0, self.data_timestamps_eq20_asc),
                    ]
        received = AscGrid.firstTimestamp(mock.Stream(self.data_inc), threshold=True)

        for i_expected, i_received in zip(expected, received):
            output = mock.Stream()
            i_received[1].writeToStream(output)
            self.assertEqual(i_expected, (i_received[0], ''.join(output.content)))


class ExtractPercentiles(unittest.TestCase):

    def setUp(self):

        import random

        self.grid = AscGrid(ncols=80, nrows=80, xllcorner=150000, yllcorner=400000,
                            cellsize=100, nodata_value=-999)
        for row in range(80):
            for col in range(0, 80, 2):
                self.grid.values[row, col] = random.random() - 1
                self.grid.values[row, col + 1] = random.random() + 1
        self.grid.values[0, 0:2] = 0.0

    def test010(self):
        "extract 50th percentile of 80x80 grid, made easy"

        self.assertEqual(self.grid.scoreatpercentile(50), 0.0)


class ReadingGdalObject(unittest.TestCase):

    def setUp(self):
        global gdal
        self.oldgdal = gdal
        gdal = mock.gdal

    def tearDown(self):
        global gdal
        gdal = self.oldgdal

    def test000(self):
        "initializing from gdal.Dataset"

        v = numpy.ndarray((3, 4))
        v[:] = 0
        dataset_1 = mock.gdal.Dataset(v, 0, 0, 10, -999)
        g = AscGrid(dataset_1)
        output = mock.Stream()
        g.writeToStream(output)
        expect = """\
nCols        4
nRows        3
xllCorner    0
yllCorner    0
CellSize     10
nodata_value -999
 0 0 0 0
 0 0 0 0
 0 0 0 0
"""
        self.assertEqual(''.join(output.content), expect)

    def test010(self):
        "NoDataValues in gdal.Dataset become None"

        v = numpy.ndarray((3, 3))
        v[0, :] = [-999] * 3
        v[1, :] = [21, -999, 23]
        v[2, :] = [31, -999, 33]
        dataset_1 = mock.gdal.Dataset(v, 0, 0, 10, -999)
        g = AscGrid(dataset_1)
        self.assertEqual(g[1, 1], None)
        self.assertEqual(g[2, 2], None)
        self.assertEqual(g[3, 3], 33)

    def test100(self):
        "scoreatpercentile from gdal.Dataset without None"

        v = numpy.ndarray((3, 3))
        v[0, :] = [11, 12, 13]
        v[1, :] = [21, 22, 23]
        v[2, :] = [31, 32, 33]
        dataset_1 = mock.gdal.Dataset(v, 0, 0, 10, -999)
        g = AscGrid(dataset_1)
        self.assertEqual(g.scoreatpercentile(50), 22.0)

    def test110(self):
        "scoreatpercentile from gdal.Dataset with None"

        v = numpy.ndarray((3, 3))
        v[1, :] = [21, 22, 23]
        v[2, :] = [31, 32, 33]
        v[0, :] = [-999] * 3
        v[:, 1] = [-999] * 3
        dataset_1 = mock.gdal.Dataset(v, 0, 0, 10, -999)
        g = AscGrid(dataset_1)
        self.assertEqual(g.scoreatpercentile(50), 27.0)


class DoctestRunner(unittest.TestCase):
    def test0000(self):
        import doctest
        doctest.testmod(name=__name__[:-6])

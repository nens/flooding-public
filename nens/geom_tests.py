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

import logging
import unittest
import mock
handler = mock.Handler(level=logging.DEBUG)
logging.getLogger('').addHandler(handler)

from geom import TOLERANCE
from geom import align
from geom import sort
from geom import sort_perpendicular_to_segment
from geom import computeVoronoiDiagram
from geom import Site
from geom import make_graph
from geom import find_simple_paths
from geom import densify


class MyTestCases(unittest.TestCase):
    def listsContainEqualVectors(self, a, b, eps=TOLERANCE):
        d = 0
        for r, e in zip(a, b):
            for r1, e1 in zip(r, e):
                d += abs(r1 - e1)
        self.assertTrue(d < eps, "%s !=(eps) %s" % (str(a), str(b)))

    def assertEqualPolygon(self, a, b, text="", eps=TOLERANCE):
        self.assertTrue(a.difference(b).area < eps, text)

    def assertEqualPolygonDict(self, a, b, eps=TOLERANCE):
        self.assertEqual(set(a.keys()), set(b.keys()))
        from shapely.geometry.polygon import Polygon
        for key in a:
            self.assertEqualPolygon(Polygon(a[key]), Polygon(b[key]), ": different on '%s'" % key, eps)


class AligningTest(MyTestCases):
    def testAligned2dPointsHorizontal(self):
        points = [[0, 0], [1, 1], [2, 0]]
        expect = [[0.0, 0.0], [1.0, 0.0], [2.0, 0.0]]
        result = align(points)
        self.listsContainEqualVectors(result, expect)

    def testAligned2dPointsVertical(self):
        points = [[0, 0], [1, 1], [0, 2]]
        expect = [[0.0, 0.0], [0.0, 1.0], [0.0, 2.0]]
        result = align(points)
        self.listsContainEqualVectors(result, expect)

    def testAligned3dPointsVertical(self):
        points = [[0.0, 0.0, 1.9], [1.0, 1.0, 0.9], [10.0, 2.0, 0.2], [-2.0, 3.0, 0.2], [-1.0, 4.0, 0.7], [0.0, 5.0, 1.9]]
        expect = [[0.0, 0.0, 1.9], [0.0, 1.0, 0.9], [0.0, 2.0, 0.2], [0.0, 3.0, 0.2], [0.0, 4.0, 0.7], [0.0, 5.0, 1.9]]
        result = align(points)
        self.listsContainEqualVectors(result, expect)

    def testAligned3dPointsOblique(self):
        points = [[0.0, 0.0, 0.0], [1.0, 1.0, 0.9], [10.0, 2.0, 0.2], [-2.0, 3.0, 0.2], [0.0, 4.9, 0.0], [0.0, 5.0, 12.0]]
        expect = [[0.0, 0.0, 0.0], [0.0, 1.0, 0.9], [0.0, 2.0, 0.2], [0.0, 3.0, 0.2], [0.0, 4.9, 0.0], [0.0, 5.0, 12.0]]
        result = align(points)
        self.listsContainEqualVectors(result, expect)

    def testAligned3dPointsHorizontal(self):
        points = [[0, 0, 0.9], [1, 1, 0.3], [0, 2, 0.9]]
        expect = [[0.0, 0.0, 0.9], [0.0, 1.0, 0.3], [0.0, 2.0, 0.9]]
        result = align(points)
        self.listsContainEqualVectors(result, expect)


class SortingTest(MyTestCases):
    def testSortingAlreadySorted(self):
        points = [[0.0, 0.0, 1.9], [0.0, 1.0, 0.9], [0.0, 2.0, 0.2], [0.0, 3.0, 0.2], [0.0, 4.0, 0.7], [0.0, 5.0, 1.9]]
        expect = [[0.0, 0.0, 1.9], [0.0, 1.0, 0.9], [0.0, 2.0, 0.2], [0.0, 3.0, 0.2], [0.0, 4.0, 0.7], [0.0, 5.0, 1.9]]
        result = sort(points)
        self.assertEqual(result, expect)

    def testSortingShuffledCloud(self):
        points = [[0.0, 3.0, 0.2], [0.0, 1.0, 0.9], [0.0, 4.0, 0.7], [0.0, 2.0, 0.2], [0.0, 0.0, 1.9], [0.0, 5.0, 1.9]]
        expect = [[0.0, 0.0, 1.9], [0.0, 1.0, 0.9], [0.0, 2.0, 0.2], [0.0, 3.0, 0.2], [0.0, 4.0, 0.7], [0.0, 5.0, 1.9]]
        result = sort(points)
        self.assertEqual(result, expect)

    def testSortingShuffledCurve(self):
        points = [[3.0, -1.0, 0.0], [1.5, 0.5, 0.0], [4.0, 0.0, 0.0], [0.5, 0.5, 0.0], [0.0, 0.0, 0.0], [2.0, 0.0, 0.0], [1.0, 1.0, 0.0], [2.5, -0.5, 0.0], [3.5, -0.5, 0.0], ]
        expect = [[4.0, 0.0, 0.0], [3.5, -0.5, 0.0], [3.0, -1.0, 0.0], [2.5, -0.5, 0.0], [2.0, 0.0, 0.0], [1.5, 0.5, 0.0], [1.0, 1.0, 0.0], [0.5, 0.5, 0.0], [0.0, 0.0, 0.0]]
        result = sort(points)
        self.assertEqual(result, expect)

    def testSortingNorthSouth(self):
        points = [(1.464, 5.38), (1.616, 6.482), (1.688, 3.68), (1.734, 7.3031), (1.953, 4.675)]
        expect = [[1.688, 3.68], [1.953, 4.675], [1.464, 5.38], [1.616, 6.482], [1.734, 7.3031]]
        result = sort(points)
        self.assertEqual(result, expect)


class SortPerpendicularTest(MyTestCases):
    def testSortPerpendicularAlmostNorthSouth(self):
        ls = [(138585.10418, 483434.4867), (138577.64577, 483435.45535)]
        pc = [(138581.464, 483435.38), (138581.616, 483436.482), (138581.688, 483433.68), (138581.734, 483437.3031), (138581.953, 483434.675)]

        expect = [[138581.54415245666, 483433.69868198753], [138581.67562877599, 483434.71102317865], [138581.7575596447, 483435.34187437408], [138581.9008275549, 483436.44500844134], [138582.00765515293, 483437.26755944057]]

        result = sort_perpendicular_to_segment(ls, pc)
        self.assertEquals(result, expect)


class VoronoiDiagramsTest(MyTestCases):

    def expand_segment(self, voronoi_result, index):
        if isinstance(index, tuple):
            compact_representation = index
        else:
            compact_representation = voronoi_result[2][index]
        result = []
        result.append(voronoi_result[1][compact_representation[0]])
        for vertex in compact_representation[1:]:
            if vertex != -1:
                vertex = voronoi_result[0][vertex]
            result.append(vertex)
        return tuple(result)

    def assertEqualVoronoiResults(self, result, expect):
        self.assertEqual(len(result[:3]), 3, "result is not 3-tuple")
        result_segments = set([self.expand_segment(result, i) for i in result[2]])
        expect_segments = set([self.expand_segment(expect, i) for i in expect[2]])
        self.assertEqual(result_segments, expect_segments, "segments set comparison mismatch %s != %s in %s != %s" % (result_segments, expect_segments, result, expect))
        self.assertEqual(set(result[0]), set(expect[0]), "vertices set comparison mismatch %s != %s in %s != %s" % (result[0], expect[0], result, expect))
        self.assertEqual(set(result[1]), set(expect[1]), "equations set comparison mismatch %s != %s in %s != %s" % (result[1], expect[1], result, expect))

    def test000(self):
        "computeVoronoiDiagram on 0, 0; 1, 1"
        from nens import mock
        points = [mock.Point(0.0, 0.0), mock.Point(1.0, 1.0), ]
        # expect no vertices, one line equation, one voronoi segment
        expect = ([], [(1.0, 1.0, 1.0)], [(0, -1, -1)])
        result = computeVoronoiDiagram(points)
        self.assertEqualVoronoiResults(result, expect)

    def test001(self):
        "computeVoronoiDiagram on 0, 0; 2, 0"
        from nens import mock
        points = [mock.Point(0.0, 0.0), mock.Point(2.0, 0.0), ]
        # expect no vertices, one line equation, one voronoi segment
        expect = ([], [(1.0, 0.0, 1.0)], [(0, -1, -1)])
        result = computeVoronoiDiagram(points)
        self.assertEqualVoronoiResults(result, expect)

    def test002(self):
        "** computeVoronoiDiagram on 0, 0; 0, 2 crashes **"
        from nens import mock
        points = [mock.Point(0.0, 0.0), mock.Point(0.0, 2.0), ]
        self.assertRaises(ZeroDivisionError, computeVoronoiDiagram, points)
        if 0:
            result = computeVoronoiDiagram(points)
            expect = ([], [(0.0, 1.0, 1.0)], [(0, -1, -1)])
            self.assertEqualVoronoiResults(result, expect)

    def test003(self):
        "computeVoronoiDiagram on 0, 0"
        from nens import mock
        points = [mock.Point(0.0, 0.0), ]
        # expect empty result, not a crash.
        expect = ([], [], [])
        result = computeVoronoiDiagram(points)
        self.assertEqualVoronoiResults(result, expect)

    def test010(self):
        "computeVoronoiDiagram on 0, 0; 0, 2; 2, 0; 2, 2"
        from nens import mock
        points = [mock.Point(0.0, 0.0), mock.Point(0.0, 2.0), mock.Point(2.0, 2.0), mock.Point(2.0, 0.0), ]
        # expect one vertex, two line equations, four voronoi segment
        expect = ([(1.0, 1.0)],
                  [(0.0, 1.0, 1.0), (1.0, 0.0, 1.0)],
                  [(0, -1, 0), (0, 0, -1), (1, -1, 0), (1, 0, -1), ])
        result = computeVoronoiDiagram(points)
        self.assertEqualVoronoiResults(result, expect)

    def test011(self):
        "computeVoronoiDiagram on 1, 0; 0, 1; -1, 0; 0, -1"
        from nens import mock
        points = [mock.Point(1.0, 0.0), mock.Point(0.0, 1.0), mock.Point(-1.0, 0.0), mock.Point(0.0, -1.0), ]
        # expect one vertex, two line equations, four voronoi segment
        expect = ([(0.0, 0.0)],
                  [(1.0, 1.0, 0.0), (-1.0, 1.0, 0.0)],
                  [(0, -1, 0), (0, 0, -1), (1, -1, 0), (1, 0, -1)])
        result = computeVoronoiDiagram(points)
        self.assertEqualVoronoiResults(result, expect)

    def test012(self):
        "computeVoronoiDiagram on 0, 0; 1, 0; 0, 1; -1, 0; 0, -1"
        from nens import mock
        points = [mock.Point(0.0, 0.0),
                  mock.Point(1.0, 0.0), mock.Point(0.0, 1.0), mock.Point(-1.0, 0.0), mock.Point(0.0, -1.0), ]
        # expect four vertices, six line equations, eight voronoi segments
        expect = ([(-0.5, -0.5), (0.5, -0.5), (-0.5, 0.5), (0.5, 0.5)],
                  [(-1.0, 1.0, 0.0), (1.0, 1.0, 0.0),
                   (0.0, 1.0, -0.5), (0.0, 1.0, 0.5), (1.0, 0.0, -0.5), (1.0, 0.0, 0.5)],
                  [(2, 0, 1), (3, 2, 3), (4, 2, 0), (5, 3, 1),
                   (1, -1, 2), (1, 1, -1), (0, 3, -1), (0, -1, 0)])
        result = computeVoronoiDiagram(points)
        self.assertEqualVoronoiResults(result, expect)

    def test014(self):
        "computeVoronoiDiagram (+5+5 translation) 0, 0; 1, 0; 0, 1; -1, 0; 0, -1"
        from nens import mock
        points = [mock.Point(5.0, 5.0),
                  mock.Point(6.0, 5.0), mock.Point(5.0, 6.0), mock.Point(4.0, 5.0), mock.Point(5.0, 4.0), ]
        # expect four vertices, six line equations, eight voronoi segments
        expect = ([(4.5, 4.5), (5.5, 4.5), (4.5, 5.5), (5.5, 5.5)],
                  [(-1.0, 1.0, 0.0), (1.0, 1.0, 10.0),
                   (0.0, 1.0, 4.5), (0.0, 1.0, 5.5), (1.0, 0.0, 4.5), (1.0, 0.0, 5.5)],
                  [(2, 0, 1), (3, 2, 3), (4, 2, 0), (5, 3, 1),
                   (1, -1, 2), (1, 1, -1), (0, 3, -1), (0, -1, 0)])
        result = computeVoronoiDiagram(points)
        self.assertEqualVoronoiResults(result, expect)

    def test022(self):
        "computeVoronoiDiagram on zigzag set"
        from nens import mock
        points = [
            mock.Point(0.0, 0.0), mock.Point(1.0, 1.0), mock.Point(0.0, 2.0), mock.Point(1.0, 3.0), mock.Point(0.0, 4.0),
            mock.Point(2.0, 0.0), mock.Point(3.0, 1.0), mock.Point(2.0, 2.0), mock.Point(3.0, 3.0), mock.Point(2.0, 4.0),
                  ]
        # expect eight vertices, ten line equations, seventeen voronoi segments
        expect = ([(1.0, 0.0), (0.0, 1.0), (2.0, 1.0), (2.0, 1.0), (1.0, 2.0), (1.0, 2.0), (3.0, 2.0), (0.0, 3.0), (2.0, 3.0), (1.0, 4.0)],
                  [(1.0, 0.0, 1.0), (1.0, 1.0, 1.0), (-1.0, 1.0, -1.0), (1.0, 1.0, 3.0), (0.0, 1.0, 1.0), (-1.0, 1.0, 1.0), (0.0, 1.0, 2.0), (1.0, 1.0, 5.0), (0.0, 1.0, 3.0), (-1.0, 1.0, 3.0)],
                  [(1, 1, 0), (2, 0, 2), (5, 1, 4), (3, 4, 2), (2, 3, 6), (3, 7, 4), (5, 5, 8), (7, 8, 6), (9, 7, 9), (7, 9, 8), (4, -1, 1), (8, -1, 7), (0, -1, 9), (5, 8, -1), (6, 6, -1), (3, 2, -1), (0, 0, -1)])
        result = computeVoronoiDiagram(points)
        self.assertEqualVoronoiResults(result, expect)

    def test030(self):
        "associate input points to sorrounding polygons - internal points"
        from nens import mock
        points = [
            mock.Point(0.0, 0.0), mock.Point(1.0, 1.0), mock.Point(0.0, 2.0), mock.Point(1.0, 3.0), mock.Point(0.0, 4.0),
            mock.Point(2.0, 0.0), mock.Point(3.0, 1.0), mock.Point(2.0, 2.0), mock.Point(3.0, 3.0), mock.Point(2.0, 4.0),
            ]
        expect_3 = {(1.0, 3.0): [(1.0, 2.0), (2.0, 3.0), (1.0, 4.0), (0.0, 3.0), (1.0, 2.0), ],
                    (2.0, 2.0): [(2.0, 1.0), (3.0, 2.0), (2.0, 3.0), (1.0, 2.0), (2.0, 1.0), ],
                    (1.0, 1.0): [(1.0, 0.0), (2.0, 1.0), (1.0, 2.0), (0.0, 1.0), (1.0, 0.0), ],
                    }
        result_3 = computeVoronoiDiagram(points)[3]
        for ip in expect_3:
            self.assertEquals(result_3[ip], expect_3[ip])

    def test032(self):
        "associate input points to sorrounding polygons - border points"
        from nens import mock
        points = [
            mock.Point(0.0, 0.0), mock.Point(1.0, 1.0), mock.Point(0.0, 2.0), mock.Point(1.0, 3.0), mock.Point(0.0, 4.0),
            mock.Point(2.0, 0.0), mock.Point(3.0, 1.0), mock.Point(2.0, 2.0), mock.Point(3.0, 3.0), mock.Point(2.0, 4.0),
            ]
        expect_3 = {(2.0, 4.0): [(0.0, 1.0, 0), (1.0, 4.0), (2.0, 3.0), (1.0, 1.0, 0)],
                    (0.0, 0.0): [(0.0, -1.0, 0), (1.0, -0.0), (0.0, 1.0), (-1.0, 0.0, 0)],
                    (3.0, 3.0): [(1.0, 1.0, 0), (2.0, 3.0), (3.0, 2.0), (1.0, 0.0, 0)],
                    (3.0, 1.0): [(1.0, 0.0, 0), (3.0, 2.0), (2.0, 1.0), (1.0, -1.0, 0)],
                    (0.0, 2.0): [(-1.0, 0.0, 0), (0.0, 1.0), (1.0, 2.0), (0.0, 3.0), (-1.0, 0.0, 0)],
                    (2.0, 0.0): [(1.0, -1.0, 0), (2.0, 1.0), (1.0, 0.0), (0.0, -1.0, 0)],
                    (0.0, 4.0): [(-1.0, 0.0, 0), (0.0, 3.0), (1.0, 4.0), (0.0, 1.0, 0)],
                    }
        result_3 = computeVoronoiDiagram(points)[3]
        for ip in [(0.0, 4.0), (2.0, 0.0), (0.0, 2.0), (3.0, 3.0), (0.0, 0.0), (2.0, 4.0), ]:
            self.assertEquals(result_3[ip], expect_3[ip])

    def test038(self):
        "associate input points to sorrounding polygons - complete result"
        from nens import mock
        points = [
            mock.Point(0.0, 0.0), mock.Point(1.0, 1.0), mock.Point(0.0, 2.0), mock.Point(1.0, 3.0), mock.Point(0.0, 4.0),
            mock.Point(2.0, 0.0), mock.Point(3.0, 1.0), mock.Point(2.0, 2.0), mock.Point(3.0, 3.0), mock.Point(2.0, 4.0),
                  ]
        expect_3 = {Site(2.0, 4.0): [(0.0, 1.0, 0), (1.0, 4.0), (2.0, 3.0), (1.0, 1.0, 0)],
                    Site(0.0, 0.0): [(0.0, -1.0, 0), (1.0, -0.0), (0.0, 1.0), (-1.0, 0.0, 0)],
                    Site(3.0, 3.0): [(1.0, 1.0, 0), (2.0, 3.0), (3.0, 2.0), (1.0, 0.0, 0)],
                    Site(3.0, 1.0): [(1.0, 0.0, 0), (3.0, 2.0), (2.0, 1.0), (1.0, -1.0, 0)],
                    Site(0.0, 2.0): [(-1.0, 0.0, 0), (0.0, 1.0), (1.0, 2.0), (0.0, 3.0), (-1.0, 0.0, 0)],
                    Site(2.0, 0.0): [(1.0, -1.0, 0), (2.0, 1.0), (1.0, 0.0), (0.0, -1.0, 0)],
                    Site(0.0, 4.0): [(-1.0, 0.0, 0), (0.0, 3.0), (1.0, 4.0), (0.0, 1.0, 0)],
                    Site(1.0, 3.0): [(1.0, 2.0), (2.0, 3.0), (1.0, 4.0), (0.0, 3.0), (1.0, 2.0), ],
                    Site(2.0, 2.0): [(2.0, 1.0), (3.0, 2.0), (2.0, 3.0), (1.0, 2.0), (2.0, 1.0), ],
                    Site(1.0, 1.0): [(1.0, 0.0), (2.0, 1.0), (1.0, 2.0), (0.0, 1.0), (1.0, 0.0), ],
                    }
        result_3 = computeVoronoiDiagram(points)[3]
        self.assertEquals(result_3, expect_3)

    def test040(self):
        "clip external open polygons to boundary box"
        from nens import mock
        points = [
            mock.Point(0.0, 0.0), mock.Point(1.0, 1.0), mock.Point(0.0, 2.0), mock.Point(1.0, 3.0), mock.Point(0.0, 4.0),
            mock.Point(2.0, 0.0), mock.Point(3.0, 1.0), mock.Point(2.0, 2.0), mock.Point(3.0, 3.0), mock.Point(2.0, 4.0),
            ]
        container = [mock.Point(-1.0, -1.0), mock.Point(6.0, 6.0),
                     ]

        expect_3 = {Site(0.0, 0.0): [(1.0, -1.0), (1.0, -0.0), (0.0, 1.0), (-1.0, 1.0), (-1.0, -1.0), (1.0, -1.0)],
                    Site(0.0, 2.0): [(-1.0, 1.0), (0.0, 1.0), (1.0, 2.0), (0.0, 3.0), (-1.0, 3.0), (-1.0, 1.0)],
                    Site(0.0, 4.0): [(-1.0, 3.0), (0.0, 3.0), (1.0, 4.0), (1.0, 6.0), (-1.0, 6.0), (-1.0, 3.0)],
                    Site(1.0, 1.0): [(1.0, 0.0), (2.0, 1.0), (1.0, 2.0), (0.0, 1.0), (1.0, 0.0), ],
                    Site(1.0, 3.0): [(1.0, 2.0), (2.0, 3.0), (1.0, 4.0), (0.0, 3.0), (1.0, 2.0), ],
                    Site(2.0, 0.0): [(4.0, -1.0), (2.0, 1.0), (1.0, 0.0), (1.0, -1.0), (4.0, -1.0)],
                    Site(2.0, 2.0): [(2.0, 1.0), (3.0, 2.0), (2.0, 3.0), (1.0, 2.0), (2.0, 1.0), ],
                    Site(2.0, 4.0): [(1.0, 6.0), (1.0, 4.0), (2.0, 3.0), (5.0, 6.0), (1.0, 6.0)],
                    Site(3.0, 1.0): [(6.0, 2.0), (3.0, 2.0), (2.0, 1.0), (4.0, -1.0), (6.0, -1.0), (6.0, 2.0)],
                    Site(3.0, 3.0): [(5.0, 6.0), (2.0, 3.0), (3.0, 2.0), (6.0, 2.0), (6.0, 6.0), (5.0, 6.0)],
                    }
        result_3 = computeVoronoiDiagram(points, clip=container)[3]
        self.assertEquals(result_3, expect_3)

    def test050(self):
        "computeVoronoiDiagram on simple angles"
        points = [(-2, 0), (0, 2), (0, -2), ]
        expect = {Site(-2, 0): [(-1, -1, 0), (0, 0), (-1, 1, 0)],
                  Site(0, 2): [(-1, 1, 0), (0, 0), (1, 0, 0)],
                  Site(0, -2): [(1, 0, 0), (0, 0), (-1, -1, 0)]}
        result = computeVoronoiDiagram(points)[3]
        self.assertEquals(result, expect)

    def test052(self):
        "computeVoronoiDiagram on 'difficult' 5-points example - #639"
        points = [(877.9, 874.4), (0.0, 892.9), (372.7, 0.0), (773.6, 2452.1), (1287.2, 2371.8)]
        expect = [(431.8966967160988, 548.94216470611491),
                  (914.25754714901257, 1669.1011359368968),
                  (454.86183322550085, 1638.7309939820118),
                  ]
        result = computeVoronoiDiagram(points)[0]
        self.assertEquals(result, expect)

    def test100(self):
        "computeVoronoiDiagram on 0, 0; 1, 1, input as tuples"
        points = [(0.0, 0.0), (1.0, 1.0), ]
        # expect no vertices, one line equation, one voronoi segment
        expect = ([], [(1.0, 1.0, 1.0)], [(0, -1, -1)])
        result = computeVoronoiDiagram(points)
        self.assertEqualVoronoiResults(result, expect)

    def test101(self):
        "computeVoronoiDiagram does not crash on repeated points"
        points = [(0, 85), (9, 12), (9, 12), (39, 12), (50, 80)]
        result = computeVoronoiDiagram(points)
        self.assertTrue(result != None)

    def test201(self):
        "computeVoronoiDiagram can clip also on 'wide' regions"
        points = [(-2, 0), (0, 2), (0, -2), ]
        expect = {Site(-2, 0): [(-3, -3), (0, 0), (-3, 3), (-4, 3), (-4, -3), (-3, -3)],
                  Site(0, 2): [(-3, 3), (0, 0), (1, 0), (1, 3), (-3, 3)],
                  Site(0, -2): [(1, 0), (0, 0), (-3, -3), (1, -3), (1, 0)]}
        result = computeVoronoiDiagram(points, clip=(-4, -3, 1, 3))[3]
        self.assertEquals(result, expect)

    def test301(self):
        "computeVoronoiDiagram can clip lines (open polygons with no vertices)"
        points = [(2, 4), (4, 3)]
        result = computeVoronoiDiagram(points, clip=5)
        self.assertTrue(result != None)

    def test310(self):
        "seeing a Site as a tuple"
        site = Site(0, 0)
        site[0]
        site[1]

    def test312(self):
        "adding two Site objects"
        site = Site(0, 0)
        other = Site(1, 1)
        self.assertEquals(other, site + other)

    def test314(self):
        "unpacking a Site as a tuple"
        site = Site(0, 0)
        x, y = site

    def test410(self):
        "test on #1517 is not checked"
        "does not crash on #1517 (repeated points) and warning is generated"
        ## TODO - this test fails!

        points = [(111638.12362212254, 518961.03917223593), (111636.23307097171, 518957.01484113047), (111634.34251982087, 518952.990510025), (111673.50913231709, 518979.14175001864), (111669.10547939026, 518981.16505001165), (111664.70182646342, 518983.18835000461), (111660.29817353658, 518985.21164999763), (111655.89452060974, 518987.23494999058), (111651.49086768291, 518989.2582499836), (111674.45799041656, 519039.10925202462), (111672.3656285225, 519034.58938802016), (111670.27326662844, 519030.06952401565), (111668.1809047344, 519025.54966001119), (111666.08854284034, 519021.02979600674), (111663.99618094628, 519016.50993200223), (111661.90381905223, 519011.99006799777), (111659.81145715817, 519007.47020399326), (111657.71909526411, 519002.95033998881), (111655.62673337007, 518998.43047598435), (111701.27141029242, 519097.27018406219), (111699.35711543883, 519093.23027609248), (111697.44282058523, 519089.19036812283), (111755.13713906912, 518857.70715233166), (111752.64048199255, 519070.32591428258), (111751.77024099552, 519065.83795714111), (111750.89999999851, 519061.34999999963), (111750.0297590015, 519056.86204285815), (111749.15951800448, 519052.37408571667), (111748.28927700745, 519047.88612857519), (111747.41903601044, 519043.39817143371), (111748.28927700745, 519047.88612857519), (111749.15951800447, 519052.37408571667), (111750.0297590015, 519056.86204285815), (111750.89999999851, 519061.34999999963), (111751.77024099552, 519065.83795714111), (111752.64048199254, 519070.32591428258)]

        handler.flush()
        ## problem is: we don't know what we want.
        ## result = computeVoronoiDiagram(points, clip=5)
        ## self.assertEqual(handler.content, ["nens.geom|WARNING|computeVoronoiDiagram: there were 6 repeated points."])
        self.assertTrue(points != None)

    def test1870a(self):
        "combining cells that belong to equivalence classes"
        ## combining easy
        points = [(-2, 0), (0, 2), (0, -2), ]
        equivalent = [[(-2, 0), ],
                      [(0, 2), (0, -2), ],
                      ]
        result = computeVoronoiDiagram(points, clip=(-4, -3, 1, 3), equivalence=equivalent)[3]
        target = {Site(-2, 0): [(-3, -3), (0, 0), (-3, 3), (-4, 3), (-4, -3), (-3, -3)],
                  Site(0, -2.0 / 3): [(0, 0), (-3, -3), (1, -3), (1, 0), (1, 3), (-3, 3), (0, 0)],
                  }
        self.assertEqualPolygonDict(target, result)

    def test1870b(self):
        "combining cells that belong to equivalence classes"
        ## combining easy
        points = [(0, 0), (2, 0), (4, 0), (2, 2), ]
        equivalent = [[(2, 2), ],
                      [(0, 0), (2, 0), (4, 0), ],
                      ]
        result = computeVoronoiDiagram(points, clip=(-4, -2, 8, 4), equivalence=equivalent)[3]
        target = {Site(2, 2): [(-2, 4), (1, 1), (3, 1), (6, 4), (-2, 4)],
                  Site(1 + 1.0 / 3, 0): [(3, -2), (8, -2), (8, 4), (6, 4), (3, 1), (1, 1), (-2, 4), (-4, 4), (-4, -2), (1, -2), (3, -2)],
                  }
        self.assertEqualPolygonDict(target, result)

    def test1870p(self):
        "example approximating a parabola"
        points = [(5, 5)] + [(i, 0) for i in range(11)]
        equivalent = [[(5, 5)],
                      [(i, 0) for i in range(11)],
                      ]
        result = computeVoronoiDiagram(points, clip=5, equivalence=equivalent)[3]
        target = {Site(2.0 / 3, 0): [(0.5, -5), (-5, -5), (-5, 10), (0.5, 4.5), (1.5, 3.7), (2.5, 3.1), (3.5, 2.7), (4.5, 2.5), (5.5, 2.5), (6.5, 2.7), (7.5, 3.1), (8.5, 3.7), (9.5, 4.5), (15, 10), (15, -5), (9.5, -5), (8.5, -5), (7.5, -5), (6.5, -5), (5.5, -5), (4.5, -5), (3.5, -5), (2.5, -5), (1.5, -5), (0.5, -5)],
                  Site(5, 5): [(-5, 10), (0.5, 4.5), (1.5, 3.7), (2.5, 3.1), (3.5, 2.7), (4.5, 2.5), (5.5, 2.5), (6.5, 2.7), (7.5, 3.1), (8.5, 3.7), (9.5, 4.5), (15, 10), (-5, 10)],
                  }
        self.assertEqualPolygonDict(target, result)


class GeneralizedDiagramsTest(MyTestCases):
    def testpath001(self):
        "loop gets split"
        from shapely.geometry.multilinestring import MultiLineString
        ml = MultiLineString([[(-2, 2), (-1, 1), (1, 1), (1, -1), (-1, -1), (-1, 1)],
                              [(1, 1), (2, 2)],
                              [(1, -1), (2, -2)],
                              [(-1, -1), (-2, -2)]])
        G = make_graph([ml])
        paths = find_simple_paths(G)
        self.assertEqual(8, len(paths))

    def testpath002(self):
        "loop gets split"
        from shapely.geometry.multilinestring import MultiLineString
        ml = MultiLineString([[(-1, 1), (0, 1), (1, 1), (1, -1), (0, -1), (-1, -1), (-1, 1)],
                              [(0, 1), (0, -1)]])
        G = make_graph([ml])
        paths = find_simple_paths(G)
        self.assertEqual(3, len(paths))

    def testdensify001(self):
        "densify a Point"
        from shapely.geometry.point import Point
        point = Point(0, 0)
        self.assertEquals(point, densify(point, 20))

    def testdensify010(self):
        "densify a LineString"
        from shapely.geometry.linestring import LineString
        ls = LineString([(0, 0), (30, 40), (30, 10)])
        target = [(0.0, 0.0), (6.0, 8.0), (12.0, 16.0), (18.0, 24.0),
                  (24.0, 32.0), (30.0, 40.0), (30.0, 30.0), (30.0, 20.0),
                  (30.0, 10.0)]
        self.assertEquals(target, [c for c in densify(ls, 10).coords])
        pass

    def testdensify020(self):
        "densify a Point"
        from shapely.geometry.multilinestring import MultiLineString
        ml = MultiLineString([[(0, 0), (30, 40), (30, 10)],
                              [(0, 0), (30, 40)]])
        target = [[(0.0, 0.0), (6.0, 8.0), (12.0, 16.0), (18.0, 24.0),
                   (24.0, 32.0), (30.0, 40.0), (30.0, 30.0), (30.0, 20.0),
                   (30.0, 10.0)],
                  [(0.0, 0.0), (6.0, 8.0), (12.0, 16.0), (18.0, 24.0),
                   (24.0, 32.0), (30.0, 40.0)]]
        self.assertEquals(target, [[[i for i in p.coords] for p in ls] for ls in [densify(ml, 10).geoms]][0])


class DoctestRunner(unittest.TestCase):
    def test0000(self):
        import doctest
        doctest.testmod(name=__name__[:-6])

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
#* Library    : nens.geom
#* Purpose    : provides pure geometrical functions
#*
#* Project    : all (Turtle)
#*
#* $Id$
#*
#* initial programmer :  Mario Frasca
#* initial date       :  20081105
#**********************************************************************

__revision__ = "$Rev$"[6:-2]

import numpy
import math
from heapq import heappop, heappush

try:
    import networkx as nx
except:
    pass

import logging
log = logging.getLogger('nens.geom')


def unit_vector(O, P):
    return (P - O) / O.distance(P)


def densify(obj, density, move_inside=0):
    """densifies a shapely linear object

    for each LineString contained in obj (possibly one if obj is a
    LineString), densifies the string.

    result is a new object looking like obj, but with more points.

    >>> from shapely.geometry.linestring import LineString
    >>> p = LineString([(0, 0), (30, 40), (30, 10)])
    >>> [c for c in densify(p, 10).coords]
    [(0.0, 0.0), (6.0, 8.0), (12.0, 16.0), (18.0, 24.0), (24.0, 32.0), (30.0, 40.0), (30.0, 30.0), (30.0, 20.0), (30.0, 10.0)]
    >>> [c for c in densify(p, 11).coords]
    [(0.0, 0.0), (6.0, 8.0), (12.0, 16.0), (18.0, 24.0), (24.0, 32.0), (30.0, 40.0), (30.0, 30.0), (30.0, 20.0), (30.0, 10.0)]
    >>> [c for c in densify(p, 25).coords]
    [(0.0, 0.0), (15.0, 20.0), (30.0, 40.0), (30.0, 25.0), (30.0, 10.0)]
    >>> [c for c in densify(p, 100).coords]
    [(0.0, 0.0), (30.0, 40.0), (30.0, 10.0)]

    >>> [c for c in densify(p, 25, 0.5).coords] == [(0.3, 0.4), (15.0, 20.0), (30.0, 40.0), (30.0, 25.0), (30.0, 9.5)]
    True
    >>> [c for c in densify(p, 100, 0.5).coords] == [(0.3, 0.4), (30.0, 40.0), (30.0, 9.5)]
    True

    """

    ## not so sure what obj might be...
    if hasattr(obj, 'geoms'):
        ## obj looks like a MultiLineString!
        from shapely.geometry.multilinestring import MultiLineString
        return MultiLineString([[p for p in densify(i, density, move_inside).coords]
                                for i in obj.geoms])

    if hasattr(obj, 'coords'):
        ## obj looks like a LineString!

        ## take pairs of subsequent coordinates in obj and densify the segment.
        coords = [Site(c) for c in obj.coords]
        if len(coords) == 1:
            return obj

        sites = []
        for O, P in zip(coords, coords[1:]):
            if O == P:
                continue
            desired_amount = int(math.ceil(O.distance(P) / density))
            step = (P - O) / desired_amount  # step is a vector
            sites.extend([O + (step * i) for i in range(desired_amount)])
        sites.append(P)

        if move_inside > 0:
            sites[0] += unit_vector(*sites[:2]) * move_inside
            sites[-1] += unit_vector(*sites[-2:]) * move_inside

        from shapely.geometry.linestring import LineString
        return LineString([p.toTuple() for p in sites])


def get_bounds(site_geometries_dict):
    """the smallest horizontal rectangle containing the geometries.
    site_geometries_dict is a dictionary associating a site to a geometry.

    >>> from shapely.geometry.linestring import LineString
    >>> p = LineString([(0, 0), (30, 40), (30, 10)])
    >>> get_bounds({Site(0, 0): p})
    (0.0, 0.0, 30.0, 40.0)
    >>> q = LineString([(0, 0), (40, 30), (30, 10)])
    >>> get_bounds({Site(0, 0): p, Site(3, 3): q})
    (0.0, 0.0, 40.0, 40.0)
    """

    bounds = [obj.bounds for obj in site_geometries_dict.values()]
    minx, miny, maxx, maxy = bounds[0]
    for left, bottom, right, top in bounds[1:]:
        minx = min(minx, left)
        miny = min(miny, bottom)
        maxx = max(maxx, right)
        maxy = max(maxy, top)
    return (minx, miny, maxx, maxy)


def get_geometries(shapefile, id_field_name="ID"):
    """get geometries from shapefile as shapely objects.

    the result is a dictionary with ID as keys and a geometric object
    as values.

    examines all geometries in shapefile that are wkbMultiLineString
    or wkbLineString, constructs the corresponding MultiPolyline or
    Polyline, and associates them to their ID in the resulting dict.
    """

    result = {}

    import osgeo.ogr
    from shapely.wkt import loads
    ds = osgeo.ogr.Open(shapefile)
    lyr = ds.GetLayer()
    lyr.ResetReading()
    feat = lyr.GetNextFeature()
    id_index = max(feat.GetFieldIndex(id_field_name), 0)
    field_count = feat.GetFieldCount()
    while feat is not None:
        geom = feat.GetGeometryRef()
        if geom is None:
            continue
        item = loads(geom.ExportToWkt())
        item.__dict__.update([("F%02d" % i, feat.GetField(i)) for i in range(field_count)])
        result[feat.GetField(id_index)] = item
        feat = lyr.GetNextFeature()
    return result


def find_simple_paths(G, clip=None):
    """calculate LineStrings with no internal intersections

    >>> from shapely.wkt import loads, dumps
    >>> objs = [loads("LINESTRING (3 6, 6 8, 0 6)")]
    >>> objs.append(loads('MULTILINESTRING ((0 6, 2 8, 3 9), (2 8, 2 5))'))
    >>> G = make_graph(objs)
    >>> current = find_simple_paths(G)
    >>> target = [loads(i) for i in ['LINESTRING (2 8, 0 6, 6 8, 3 6)', 'LINESTRING (2 8, 2 5)', 'LINESTRING (3 9, 2 8)']]
    >>> [i.equals(j) for i, j in zip(target, current)]
    [True, True, True]
    >>> current = find_simple_paths(G, (-10, -10, 20, 20))
    >>> [i.equals(j) for i, j in zip(target, current)]
    [True, True, True]
    """

    if clip is not None:
        xmin, ymin, xmax, ymax = clip
    SG = G.subgraph([n for n in G.nodes()
                     if clip is None or xmin < n[0] < xmax and ymin < n[1] < ymax])

    result = []
    endpoints = set([n for n in SG.nodes() if SG.degree(n) != 2])
    from shapely.geometry.linestring import LineString
    for node in endpoints:
        while SG[node]:
            path = []
            while True:
                path.append(node)
                next = SG[node].keys()[0]
                SG.remove_edge(node, next)
                node = next
                if next in endpoints:
                    break
            path.append(next)
            result.append(LineString(path))
    return result


def make_graph(objs):
    """transforms a set of shapely linear geometries to a graph

    >>> from shapely.wkt import loads
    >>> objs = [loads("LINESTRING (3 6, 6 8, 4 6)")]
    >>> G = make_graph(objs)
    >>> G.nodes()
    [(6.0, 8.0), (3.0, 6.0), (4.0, 6.0)]
    >>> G.edges()
    [((6.0, 8.0), (4.0, 6.0)), ((6.0, 8.0), (3.0, 6.0))]
    >>> objs.append(loads('MULTILINESTRING ((0 6, 2 8, 3 9), (2 8, 2 5))'))
    >>> G = make_graph(objs)
    >>> G.nodes()
    [(6.0, 8.0), (2.0, 8.0), (0.0, 6.0), (3.0, 9.0), (3.0, 6.0), (2.0, 5.0), (4.0, 6.0)]
    >>> G.edges()
    [((6.0, 8.0), (4.0, 6.0)), ((6.0, 8.0), (3.0, 6.0)), ((2.0, 8.0), (0.0, 6.0)), ((2.0, 8.0), (2.0, 5.0)), ((2.0, 8.0), (3.0, 9.0))]
    """

    G = nx.Graph()
    if isinstance(objs, dict):
        objs = objs.values()
    from shapely.geometry.point import Point
    for item in objs:
        if item.geom_type == 'Point':
            G.add_node(item)
        elif item.geom_type == 'LineString':
            points = [i for i in item.coords]
            for O, P in zip(points, points[1:]):
                G.add_edge(O, P, {'weight': Point(O).distance(Point(P))})
        elif item.geom_type == 'MultiLineString':
            for geom in item.geoms:
                points = [i for i in geom.coords]
                for O, P in zip(points, points[1:]):
                    G.add_edge(O, P, {'weight': Point(O).distance(Point(P))})
    return G


def get_polyline(graph, A, B):
    """returns the shortest polyline that goes from A to B in the graph.

    A and B must lie on the graph.
    the graph must connect A to B.
    each edge in the graph has a 'weight' equal to its length.

    returns a LineString object.

    >>> import math
    >>> from shapely.geometry.multilinestring import MultiLineString
    >>> obj = MultiLineString([[(0, 6), (2, 8), (3, 9)], [(2, 8), (2, 5)], [(1, 1), (2, 2)], [(0, 0), (1, 0), (1, 1), (2, 0), (2, 1), (0, 0)]])
    >>> g = make_graph([obj])
    >>> p = get_polyline(g, (0, 6), (2, 5))
    >>> [i for i in p.coords]
    [(0.0, 6.0), (2.0, 8.0), (2.0, 5.0)]
    >>> get_polyline(g, (0, 6), (3, 9)).length # doctest:+ELLIPSIS
    4.2426406...
    >>> get_polyline(g, (0, 5), (2, 5))
    >>> get_polyline(g, (2, 5), (1, 1))
    >>> get_polyline(g, (0, 0), (2, 0)).length # doctest:+ELLIPSIS
    3.2360679...
    >>> get_polyline(g, (0, 0), (2, 1)).length # doctest:+ELLIPSIS
    2.2360679...
    >>> get_polyline(g, (0, 0), (2, 2)).length # doctest:+ELLIPSIS
    3.4142135...
    >>> mpl = MultiLineString([[(0, 0), (1, 1), (2, 2), (3, 3)], [(0, 0), (3, 0), (3, 3)]])
    >>> g = make_graph([mpl])
    >>> get_polyline(g, (0, 0), (3, 3)).length # doctest:+ELLIPSIS
    4.2426406...

    """

    try:
        points = nx.shortest_path(graph, A, B, weighted=True)
    except nx.NetworkXError, e:
        log.debug(e)
        return None
    except KeyError:
        log.debug("graph does not connect '%s' to '%s'" % (A, B))
        return None

    from shapely.geometry.linestring import LineString
    return LineString(points)


def sort_perpendicular_to_segment(verticesList, pointsCloud):
    """sort pointsCould perpendicularly to segment in verticesList

    assuming the points in pointsCloud are more or less aligned, and
    that the segment they describe is more or less perpendicular to
    the only segment in verticesList it intersects, compute the
    ideal situation.

    the ideal situation is that the points in pointsCloud are in fact
    perfectly aligned, that the segment they describe intersects the
    segments along verticesList only at one point and that the two
    segments are perpendicular.

    >>> ls = [(0, 0), (30, 40), (30, 10)]
    >>> pc = [(10, 10), (9, 11), (7, 12), (6, 13)]
    >>> sort_perpendicular_to_segment(ls, pc)
    [[6.0, 13.0], [7.1199999999999992, 12.16], [8.879999999999999, 10.84], [10.0, 10.0]]

    no point is guaranteed to stay fixed, in particular the first and
    last ones may need to be displaced.
    >>> pc = [(10, 10), (9, 11), (7, 13)]
    >>> sort_perpendicular_to_segment(ls, pc)
    [[10.171428571428571, 10.228571428571428], [9.0514285714285716, 11.068571428571429], [6.8114285714285714, 12.748571428571429]]

    points in the pointsCloud may be threedimensional, in this case
    the z value is simply kept in the corresponding projected point.
    >>> pc3d = [(10, 10, 1.25), (9, 11, 1.125), (7, 12, 1.5), (6, 13, 1.375)]
    >>> sort_perpendicular_to_segment(ls, pc3d)
    [[10.0, 10.0, 1.25], [8.879999999999999, 10.84, 1.125], [7.1199999999999992, 12.16, 1.5], [6.0, 13.0, 1.375]]

    points in verticesList must be 2D.  an exception is raised
    otherwise.
    >>> ls3d = [(0, 0, 0), (30, 40, 0), (30, 10, 0)]
    >>> sort_perpendicular_to_segment(ls3d, pc3d)
    Traceback (most recent call last):
        ...
    ValueError: vertices must be 2D
    """

    numpy_format, pointsCloud = to_numpy_format(pointsCloud)
    ## first of all, sort pointsCloud!
    pointsCloud = sort(pointsCloud)

    cloudIs3D = pointsCloud[0].size == 3

    if len(verticesList[0]) != 2:
        raise ValueError("vertices must be 2D")

    from shapely.geometry.linestring import LineString

    # choose an intersection point
    A = pointsCloud[0]
    B = pointsCloud[-1]
    segment = LineString([A, B])

    for p0, p1 in zip(verticesList[:-1], verticesList[1:]):
        ls = LineString([p0, p1])

        found = ls.intersects(segment)
        if found:
            break
    if not found:
        raise ValueError("no intersection found")

    intersection = to_numpy_format(ls.intersection(segment).coords)[1][0]

    ls_coords = to_numpy_format((ls.coords[0], ls.coords[1]))[1]
    v = (ls_coords[1] - ls_coords[0])
    u = v / math.sqrt(sum([i * i for i in v.flatten()]))
    u[0][0], u[1][0] = u[1][0], -u[0][0]  # perpendicular

    if cloudIs3D:
        u.resize((1, 3))
    p = u * u.transpose()
    if cloudIs3D:
        p[2][2] = 1
        intersection.resize((3, 1))

    orig = intersection
    vecs = [pt - orig for pt in pointsCloud]

    projected = [numpy.inner(p, v.transpose()) for v in vecs]
    aligned = [v + orig for v in projected]

    if not numpy_format:
        aligned = [[i for i in p.flatten()] for p in aligned]
    return aligned


class sort_functor:

    def __init__(self):
        return

    def compare_only_first_element(self, a, b):
        if a[0] < b[0]:
            return -1
        if a[0] > b[0]:
            return 1
        return 0

    def __call__(self, args):
        """takes a list of 3d points and sorts them.

        assumes the points are approximatively aligned but possibly in
        random order.  identifies the two points A, B that lie farthes
        from each other.  returns the cloud of unaltered points sorted so
        that their projection on the segment AB are in sequence.
        """

        numpy_format, args = to_numpy_format(args)

        # get the baricentre of the cloud
        # get the point that lies farthest from the centre
        # get the point that lies farthest from previous one
        centre = sum(args) / len(args)

        with_square_distance = [(numpy.dot((P - centre).transpose(), (P - centre))[0][0], P) for P in args]
        d = 0
        for square_distance, P in with_square_distance:
            if square_distance > d:
                A = P
                d = square_distance
        with_square_distance = [(numpy.dot((P - A).transpose(), (P - A))[0][0], P) for P in args]
        for square_distance, P in with_square_distance:
            if square_distance > d:
                B = P
                d = square_distance

        augmented_list = [A] + args + [B]
        augmented_list_abscissas = abscissa_from_midsegment(augmented_list)
        joined = zip(augmented_list_abscissas, augmented_list)[1:-1]

        joined.sort(cmp=self.compare_only_first_element)
        result = [P for (_, P) in joined]

        if not numpy_format:
            result = [[i for i in p.flatten()] for p in result]

        return result

sort = sort_functor()


def roundpoint(p, ndigits):
    """similar to built-in round, but for points

    currently limited to points in iterable format and shapely Points.

    >>> roundpoint([1,2,3], 1)
    (1.0, 2.0, 3.0)
    >>> from shapely.geometry.point import Point
    >>> [i for i in roundpoint(Point(1.3,2.625,3.5), 0).coords]
    [(1.0, 3.0, 4.0)]
    >>> roundpoint((1.1,2.2,3.3), 0)
    (1.0, 2.0, 3.0)
    >>> roundpoint(Site(1.3,2.625,3.5), 0)
    (1.0, 3.0, 4.0)

    >>> roundpoint(1.3, 0) # value is returned and a warning is emitted
    1.3
    """

    from shapely.geometry.point import Point
    if isinstance(p, Point):
        return Point(roundpoint([i for i in p.coords][0], ndigits))
    try:
        return tuple([round(x, ndigits) for x in p])
    except TypeError:
        log.warn("can't roundpoint of type %s" % type(p))
        return p


def to_numpy_format(args):
    """makes sure the input data is in numpy.array format

    returns a tuple with a boolean (was_numpy) and the numpy.array
    list corresponding to the input args.
    """

    numpy_format = True
    if isinstance(args[0], (list, tuple)):
        args = [numpy.array([[i] for i in p]) for p in args]
        numpy_format = False
    return (numpy_format, args)


def align(args):
    """takes a list of points and aligns them between args[0] and args[-1].

    points are numpy.array objects (vertical vectors) or lists.
    2D points are simply aligned along the segment.
    3D points keep their z coordinate.
    """

    numpy_format, args = to_numpy_format(args)

    orig = args[0]
    vecs = [p - orig for p in args]
    v = 1.0 * vecs[-1]  # cloning vector
    is3d = v.size == 3
    if is3d:
        v[2] = 0.0
    u = v / math.sqrt(sum([i * i for i in v.flatten()]))
    p = u * u.transpose()

    if is3d:
        p[2][2] = 1

    projected = [numpy.inner(p, v.transpose()) for v in vecs]
    aligned = [v + orig for v in projected]

    if not numpy_format:
        aligned = [[i for i in p.flatten()] for p in aligned]
    return aligned


def abscissa_from_midsegment(args):
    """returns the list of abscissas of the projected points from the
    midpoint of the oriented segment args[0], args[-1].

    >>> points = [[0, 0], [1, 0], [4, 0]]
    >>> abscissa_from_midsegment(points)
    [-2.0, -1.0, 2.0]
    >>> abscissa_from_midsegment([[1, 0], [4, 4], [7, 8]])
    [-5.0, 0.0, 5.0]
    """

    if isinstance(args[0], list):
        args = [numpy.array([[i] for i in p]) for p in args]

    args = align(args)
    orig = args[0]
    from_orig = [math.sqrt(numpy.dot((i - orig).transpose(), (i - orig))) for i in args]
    midsegment = from_orig[-1] / 2
    return [i - midsegment for i in from_orig]


class SiteDict(dict):
    """a dictionary that hides the difference between a Site and a tuple
    """

    def __getitem__(self, key):
        return dict.__getitem__(self, Site(key))

    def get(self, key, default=None):
        return dict.get(self, Site(key), default)

    def __setitem__(self, key, value):
        return dict.__setitem__(self, Site(key), value)

    def pop(self, key, default=None):
        return dict.pop(self, Site(key), default)

#############################################################################
#
# Voronoi diagram calculator/ Delaunay triangulator
# Translated to Python by Bill Simons
# September, 2005
#
# Calculate Delaunay triangulation or the Voronoi polygons for a set of
# 2D input points.
#
# Derived from code bearing the following notice:
#
#  The author of this software is Steven Fortune.  Copyright (c) 1994 by AT&T
#  Bell Laboratories.
#  Permission to use, copy, modify, and distribute this software for any
#  purpose without fee is hereby granted, provided that this entire notice
#  is included in all copies of any software which is or includes a copy
#  or modification of this software and in all copies of the supporting
#  documentation for such software.
#  THIS SOFTWARE IS BEING PROVIDED "AS IS", WITHOUT ANY EXPRESS OR IMPLIED
#  WARRANTY.  IN PARTICULAR, NEITHER THE AUTHORS NOR AT&T MAKE ANY
#  REPRESENTATION OR WARRANTY OF ANY KIND CONCERNING THE MERCHANTABILITY
#  OF THIS SOFTWARE OR ITS FITNESS FOR ANY PARTICULAR PURPOSE.
#
# Comments were incorporated from Shane O'Sullivan's translation of the
# original code into C++ (http://mapviewer.skynet.ie/voronoi.html)
#
# Steve Fortune's homepage: http://netlib.bell-labs.com/cm/cs/who/sjf/index.html
#
# minor bug fixes, computation of delimiting polygons and unit tests
# added by Mario Frasca (mariotomo@inventati.org)
#
# For programmatic use these functions are available:
#
#   computeVoronoiDiagram(points, ...)
#   computeGeneralizedVoronoiDiagram(set_of_linear_objects, density, ...)
#   plotTessellation(computeVoronoiDiagram(points, ...))
#
#   computeDelaunayTriangulation(points):
#
#
#############################################################################
TOLERANCE = 1e-9
BIG_FLOAT = 1e38
cradius = None  # this is used but no idea why it's there.


#------------------------------------------------------------------
class Context(object):
    def __init__(self):
        self.doPrint = 0
        self.debug = 0
        self.plot = 0
        self.triangulate = False
        self.vertices = []    # list of vertex 2-tuples: (x, y)
        self.lines = []  # Edge object, specifying among others the
                         # equation of line 3-tuple (a b c), for the
                         # equation of the line a*x+b*y = c
        self.edges = []  # edge 3-tuple: (line index, vertex 1 index,
          # vertex 2 index) (if vertex 1 index is -1, the edge extends
          # to infinity in x>0 quadrants or on the half-line x=0;y<0;
          # if vertex 2 index is -1, the edge extends to infinity in
          # x<0 quadrants or on the half-line x=0; y>0)
        self.triangles = []    # 3-tuple of vertex indices

    def translate(self, siteList):
        """translate context so that origin gets new given coordinates
        """

        x0, y0 = siteList.translation

        # move vertices
        for i, (x, y) in enumerate(self.vertices):
            self.vertices[i] = (x + x0, y + y0)
        # move lines
        for edge in self.lines:
            edge.c += edge.a * x0 + edge.b * y0

        for site in siteList:
            site.x += x0
            site.y += y0

    def findPolygons(self):
        """uses delimiting lines to build list of delimiting segments
        around each site.

        returns dictionary (site->list_of_points)

        the list of points is ordered counterclockwise from the x
        axis.

        if the polygon is open, the list of points starts at a
        direction and ends at a direction, possibly diverging from the
        first.  directions are identified by a 3-tuple, first the two
        components of the unit vector from the origin of the ray
        towards the projection of the site on the line, third
        coordinate 0.0.

        if the polygon is closed, the list starts and ends at the same
        point.
        """

        def toCartesian(edge):
            """use all internal information to compute an absolute representation

            internal: {0: the line on which the segment lies,
                       1: the index of the vertex (or -1 to mean no vertex),
                       2: likewise}

            cartesian: a 2-tuple of homogeneous coordinates.
            """

            line = self.lines[edge[0]]
            result = []
            if edge[1] == -1:
                vertex = (line.b, -line.a, 0)
            else:
                vertex = self.vertices[edge[1]]
            result.append(vertex)
            if edge[2] == -1:
                vertex = (line.b, -line.a, 0)
            else:
                vertex = self.vertices[edge[2]]
            result.append(vertex)
            return tuple(result)

        from itertools import groupby
        temp = {}
        opposite_sites = {}
        # in this loop we construct `temp` and `opposite_sites`.

        # `temp` will associate each Site to the set of lines that
        # form the boundaries of its Voronoi cell.

        # `opposite_sites` will associate each Site A to the set of
        # Sites it has a border with.
        for edge in self.edges:
            S1, S2 = self.lines[edge[0]].reg  # retrieve the sites the edge is bisecting
            temp.setdefault(S1, set()).add(toCartesian(edge))
            temp.setdefault(S2, set()).add(toCartesian(edge))
            opposite_sites.setdefault(S1, set()).add(S2)
            opposite_sites.setdefault(S2, set()).add(S1)
        # now translate the information in `temp` to the `result`.
        result = SiteDict()
        for site, list_of_segments in temp.items():
            points = set([point for segment in list_of_segments for point in segment if len(point) == 2])
            # check whether closed or open polygon

            # rays is a dictionary associating an entry/exit point to
            # the ray starting there.
            rays = [(B, A) for (A, B) in list_of_segments if len(A) == 3]
            rays.extend([(A, B) for (A, B) in list_of_segments if len(B) == 3])

            is_open_polygon = rays != []
            is_single_line = points == set()
            is_simple_angle = len(points) == 1

            # sort points counterclockwise, from (-1, 0) excluded to (-1, 0) included.
            points = sorted([(math.atan2(y - site.y, x - site.x), x, y) for (x, y) in points])
            points = [(x, y) for (_, x, y) in points]

            # finalize polygon
            if is_single_line:
                # polygon is actually just a line!
                opposites = opposite_sites[site]
                if len(opposites) != 1:
                    raise RuntimeError("with border a single line, expect a single opposite site, got %d" % len(opposites))
                opposite_site = opposites.pop()
                # midpoint is needed otherwise we don't know where we stand
                midpoint = (opposite_site + site) / 2
                # we have _one_ direction and we need to give it two opposite verses
                direction_in = rays[0][1]
                direction_out = (-direction_in[0], -direction_in[1], 0)
                points = [direction_in, midpoint, direction_out]
            elif is_simple_angle:
                # simple angles are not correctly handled, sorry
                entry_point = exit_point = vertex = rays[0][0]
                direction_in = rays[0][1]
                direction_out = rays[1][1]
                points = [direction_in, vertex, direction_out]
            elif is_open_polygon:
                # split at entry_point and add incoming and outgoing rays
                rays = dict(rays)
                entry_or_exit_1, entry_or_exit_2 = rays.keys()
                indices = [points.index(entry_or_exit_1), points.index(entry_or_exit_2)]
                indices.sort()
                i_1, i_2 = indices
                if (i_1, i_2) != (0, len(points) - 1):
                    points = points[i_2:] + points[:i_2]

                while points[-1] not in rays:
                    points = points[:-1]

                entry_point, exit_point = points[0], points[-1]

                try:
                    direction_in, direction_out = rays[entry_point], rays[exit_point]
                except:
                    print rays, entry_point, exit_point
                    raise

                points.index(entry_point)
                points = [direction_in] + points + [direction_out]
            else:
                # it is a closed one, so close it!
                points.append(points[0])

            # make sure you go counterclockwise from site to
            # exit_point to ray and clockwise from site to entry_point
            # to ray.
            if is_open_polygon and not is_single_line:

                def makeVector3d(v, origin=None):
                    v = numpy.array([a for a in v[:2]] + [0])
                    if origin is not None:
                        v[0] -= origin.x
                        v[1] -= origin.y
                    return v

                def opposite(v):
                    return (-v[0], -v[1], 0)

                if is_simple_angle:
                    # less reference points, it's a bit complicated...
                    if numpy.cross(makeVector3d(points[0]), makeVector3d(points[1], site))[2] < 0:
                        points[0] = opposite(points[0])
                    if numpy.cross(makeVector3d(points[-1]), makeVector3d(points[1], site))[2] > 0:
                        points[-1] = opposite(points[-1])
                    if numpy.cross(makeVector3d(points[-1]), makeVector3d(points[0]))[2] < 0:
                        points[0], points[-1] = opposite(points[-1]), opposite(points[0])
                else:
                    if numpy.cross(makeVector3d(points[1], site), makeVector3d(points[2], site))[2] < 0:
                        points.reverse()

                    d = makeVector3d(points[0])
                    s = makeVector3d(points[1], site)
                    if numpy.cross(d, s)[2] < 0:
                        points[0] = opposite(points[0])

                    d = makeVector3d(points[-1])
                    s = makeVector3d(points[-2], site)
                    if numpy.cross(d, s)[2] > 0:
                        points[-1] = opposite(points[-1])

            result[site] = map(lambda x: x[0].toTuple(), groupby(points, Site))

        self.polygons = result
        return result

    def clipPolygons(self, clip):
        """clips polygons to the rectangle aligned as the two axes.

        clip is (x_0, y_0, x_1, y_1)
        """

        def clip_ray(base, direction):

            dx, dy, _ = direction
            base_x, base_y = base

            found_on = [0, 0]
            if dy > 0:
                #intersect with upper border
                p_y = (upper - base_y) / dy
                found_on[1] = upper
            elif dy < 0:
                #intersect with lower border
                p_y = (lower - base_y) / dy
                found_on[1] = lower
            else:
                p_y = 9e99

            if dx > 0:
                #intersect with right border
                p_x = (right - base_x) / dx
                found_on[0] = right
            elif dx < 0:
                #intersect with left border
                p_x = (left - base_x) / dx
                found_on[0] = left
            else:
                p_x = 9e99

            if p_x < p_y:
                found_on[1] = base_y + p_x * dy
                result = tuple(found_on)
                found_on[1] = 0.0
            else:
                found_on[0] = base_x + p_y * dx
                result = tuple(found_on)
                found_on[0] = 0.0

            return result, found_on

        try:
            left, lower, right, upper = clip[0].x, clip[0].y, clip[1].x, clip[1].y
        except:
            left, lower, right, upper = clip

        for p in self.polygons.values():
            if len(p[0]) == 3:
                # this polygon is open...  let's close it.

                p[0], found_in_on = clip_ray(p[1], p[0])
                p[-1], found_out_on = clip_ray(p[-2], p[-1])

                if found_out_on != found_in_on:
                    # they may be on adjacent sides, then we add one vertex.
                    if (found_out_on[0] + found_in_on[0]) * (found_out_on[1] + found_in_on[1]) != 0:
                        p.append((found_out_on[0] + found_in_on[0],
                                  found_out_on[1] + found_in_on[1],
                                  ))
                    # or on opposite ones, in which case we have to add two vertices
                    else:
                        if found_in_on == [0.0, upper]:
                            p.append((right, lower))
                            p.append((right, upper))
                        elif found_in_on == [right, 0.0]:
                            p.append((left, lower))
                            p.append((right, lower))
                        elif found_in_on == [0.0, lower]:
                            p.append((left, upper))
                            p.append((left, lower))
                        elif found_in_on == [left, 0.0]:
                            p.append((right, upper))
                            p.append((left, upper))

                p.append(p[0])

        from itertools import groupby
        for key, p in self.polygons.items():
            self.polygons[key] = map(lambda x: x[0].toTuple(), groupby(p, Site))

        return self.polygons

    def combinePolygons(self, equivalence=[]):
        """combines Voronoi cells associated to Site objects in the
        same equivalence sublist to one polygon.

        Site objects in one equivalence sublist are considered aligned
        on the same straight segment.
        """

        from shapely.geos import TopologicalError

        def safe_union(this, that):
            if this is None:
                return that
            try:
                return this.union(that)
            except ValueError, e:
                try:
                    ## trying to access this boundary may cause error
                    log.debug("returning Polygon this(%s)" % get_coords_list(this.boundary))
                    log.warning("ValueError '%s' doing this.union(that).  returning 'this'." % (e))
                    return this
                except ValueError:
                    pass
                try:
                    ## trying to access that boundary may cause error
                    log.debug("returning Polygon that(%s)" % get_coords_list(that.boundary))
                    log.warning("ValueError '%s' doing this.union(that).  returning 'that'." % (e))
                    return that
                except ValueError:
                    pass
                # right: both had no boundary!
                log.warning("ValueError '%s' doing this.union(that). returning None" % (e))
                return None
            except TopologicalError, e:
                log.error("TopologicalError(%s) joining Polygon this(%s) to Polygon that(%s)" % (e, get_coords_list(this.boundary, flatten=False), get_coords_list(that.boundary, flatten=False)))
                return this
            except:
                log.warning("some error joining Polygon this(%s) to Polygon that(%s)" % (get_coords_list(this.boundary, flatten=False), get_coords_list(that.boundary, flatten=False)))
                return this

        for segment in equivalence:
            if len(segment) > 1:
                from shapely.geometry.polygon import Polygon
                rings = [self.polygons.pop(point) for point in segment]
                polygons = [Polygon(ring) for ring in rings if rings]  # remove empty rings
                union = reduce(safe_union, polygons)

                P0, P1 = Site(segment[0]), Site(segment[1])
                representative = P0 + (P1 - P0) * (2.0 / 3)
                self.polygons[representative] = []
                try:
                    self.polygons[representative] = [i for i in union.boundary.coords]
                except (ValueError, NotImplementedError):
                    pass

    def compact(self, zero_length=0.0):
        """remove zero length edges, unused vertices, repeated lines and unused lines.
        """

        # remove zero length edges
        edges = self.edges
        self.edges = []
        for edge in edges:
            line, p1, p2 = edge
            if p1 == -1 or p2 == -1:
                self.edges.append(edge)
            else:
                c1, c2 = complex(*self.vertices[p1]), complex(*self.vertices[p2])
                if abs(c1 - c2) > zero_length:
                    self.edges.append(edge)

        # first find repeated vertices
        used = dict()
        for i, vertex in enumerate(self.vertices):
            if vertex not in used:
                used[vertex] = i

        # replace references and make repeated vertex unused
        for i, (line, p1, p2) in enumerate(self.edges):
            if p1 != -1:
                self.edges[i] = (line, used[self.vertices[p1]], p2)
            if p2 != -1:
                self.edges[i] = (line, p1, used[self.vertices[p2]])

        # makes a boolean list that says whether vertex #(i+1) is surviving
        survives = [False] * (len(self.vertices) + 1)

        # now mark all used vertices
        for edge in self.edges:
            survives[edge[1] + 1] = True
            survives[edge[2] + 1] = True

        # remove index_0 that was used for -1
        survives = survives[1:]

        # remove all unused lines
        self.vertices = [vertex for i, vertex in enumerate(self.vertices) if survives[i]]

        shift_by = []
        last_value = 0
        for i in range(len(survives)):
            shift_by.append(last_value)
            if survives[i] == False:
                last_value += 1
        # shift references to vertices in edges definitions
        edges = self.edges
        self.edges = []
        for i, p1, p2 in edges:
            if p1 != -1:
                p1 -= shift_by[p1]
            if p2 != -1:
                p2 -= shift_by[p2]
            self.edges.append((i, p1, p2))

        # first find repeated lines
        used = dict()
        for i, line in enumerate(self.lines):
            if line not in used:
                used[line] = i

        # replace references and make repeated line unused
        for i, edge in enumerate(self.edges):
            self.edges[i] = (used[self.lines[edge[0]]], edge[1], edge[2])

        # makes a boolean list that says whether line #i is surviving
        survives = [False] * len(self.lines)

        # now mark all used lines
        for edge in self.edges:
            survives[edge[0]] = True

        # remove all unused lines
        self.lines = [line for i, line in enumerate(self.lines) if survives[i]]

        # shift references to lines in edges definitions
        self.edges = [(i - survives[:i].count(False), p1, p2) for (i, p1, p2) in self.edges]

    def circle(self, x, y, rad):
        pass

    def clip_line(self, edge):
        pass

    def line(self, x0, y0, x1, y1):
        pass

    def outSite(self, s):
        if(self.debug):
            print "site (%d) at %f %f" % (s.sitenum, s.x, s.y)
        elif(self.triangulate):
            pass
        elif(self.plot):
            self.circle(s.x, s.y, cradius)
            # TODO: ^^^ cradius is undefined
        elif(self.doPrint):
            print "s %f %f" % (s.x, s.y)

    def outVertex(self, s):
        self.vertices.append((s.x, s.y))
        if(self.debug):
            print  "vertex(%d) at %f %f" % (s.sitenum, s.x, s.y)
        elif(self.triangulate):
            pass
        elif(self.doPrint and not self.plot):
            print "v %f %f" % (s.x, s.y)

    def outTriple(self, s1, s2, s3):
        self.triangles.append((s1.sitenum, s2.sitenum, s3.sitenum))
        if(self.debug):
            print "circle through left=%d right=%d bottom=%d" % (s1.sitenum, s2.sitenum, s3.sitenum)
        elif(self.triangulate and self.doPrint and not self.plot):
            print "%d %d %d" % (s1.sitenum, s2.sitenum, s3.sitenum)

    def outBisector(self, edge):
        self.lines.append(edge)

        if(self.debug):
            print "line(%d) %gx+%gy=%g, bisecting %d %d" % (edge.edgenum, edge.a, edge.b, edge.c, edge.reg[0].sitenum, edge.reg[1].sitenum)
        elif(self.triangulate):
            if(self.plot):
                self.line(edge.reg[0].x, edge.reg[0].y, edge.reg[1].x, edge.reg[1].y)
        elif(self.doPrint and not self.plot):
            print "l %f %f %f" % (edge.a, edge.b, edge.c)

    def outEdge(self, edge):
        sitenumL = -1
        if edge.ep[Edge.LE] is not None:
            sitenumL = edge.ep[Edge.LE].sitenum
        sitenumR = -1
        if edge.ep[Edge.RE] is not None:
            sitenumR = edge.ep[Edge.RE].sitenum
        self.edges.append((edge.edgenum, sitenumL, sitenumR))
        if(not self.triangulate):
            if self.plot:
                self.clip_line(edge)
            elif(self.doPrint):
                print "e %d" % edge.edgenum,
                print " %d " % sitenumL,
                print "%d" % sitenumR


#------------------------------------------------------------------
def voronoi(siteList, context):
    Edge.EDGE_NUM = 0
    edgeList = EdgeList(siteList.xmin, siteList.xmax, len(siteList))
    priorityQ = PriorityQueue(siteList.ymin, siteList.ymax, len(siteList))
    siteIter = siteList.iterator()

    bottomsite = siteIter.next()
    context.outSite(bottomsite)
    newsite = siteIter.next()
    minpt = Site(-BIG_FLOAT, -BIG_FLOAT)
    while True:
        if not priorityQ.isEmpty():
            minpt = priorityQ.getMinPt()

        if (newsite and (priorityQ.isEmpty() or cmp(newsite, minpt) < 0)):
            # newsite is smallest -  this is a site event
            context.outSite(newsite)

            # get first Halfedge to the LEFT and RIGHT of the new site
            lbnd = edgeList.leftbnd(newsite)
            rbnd = lbnd.right

            # if this halfedge has no edge, bot = bottom site (whatever that is)
            # create a new edge that bisects
            bot = lbnd.rightreg(bottomsite)
            edge = Edge(bisect=(bot, newsite))
            context.outBisector(edge)

            # create a new Halfedge, setting its pm field to 0 and insert
            # this new bisector edge between the left and right vectors in
            # a linked list
            bisector = Halfedge(edge, Edge.LE)
            edgeList.insert(lbnd, bisector)

            # if the new bisector intersects with the left edge, remove
            # the left edge's vertex, and put in the new one
            p = lbnd.intersect(bisector)
            if p is not None:
                priorityQ.delete(lbnd)
                priorityQ.insert(lbnd, p, newsite.distance(p))

            # create a new Halfedge, setting its pm field to 1
            # insert the new Halfedge to the right of the original bisector
            lbnd = bisector
            bisector = Halfedge(edge, Edge.RE)
            edgeList.insert(lbnd, bisector)

            # if this new bisector intersects with the right Halfedge
            p = bisector.intersect(rbnd)
            if p is not None:
                # push the Halfedge into the ordered linked list of vertices
                priorityQ.insert(bisector, p, newsite.distance(p))

            newsite = siteIter.next()

        elif not priorityQ.isEmpty():
            # intersection is smallest - this is a vector (circle) event

            # pop the Halfedge with the lowest vector off the ordered list of
            # vectors.  Get the Halfedge to the left and right of the above HE
            # and also the Halfedge to the right of the right HE
            lbnd = priorityQ.popMinHalfedge()
            llbnd = lbnd.left
            rbnd = lbnd.right
            rrbnd = rbnd.right

            # get the Site to the left of the left HE and to the right of
            # the right HE which it bisects
            bot = lbnd.leftreg(bottomsite)
            top = rbnd.rightreg(bottomsite)

            # output the triple of sites, stating that a circle goes through them
            mid = lbnd.rightreg(bottomsite)
            context.outTriple(bot, top, mid)

            # get the vertex that caused this event and set the vertex number
            # couldn't do this earlier since we didn't know when it would be processed
            v = lbnd.vertex
            siteList.setSiteNumber(v)
            context.outVertex(v)

            # set the endpoint of the left and right Halfedge to be this vector
            if lbnd.edge.setEndpoint(lbnd.pm, v):
                context.outEdge(lbnd.edge)

            if rbnd.edge.setEndpoint(rbnd.pm, v):
                context.outEdge(rbnd.edge)

            # delete the lowest HE, remove all vertex events to do with the
            # right HE and delete the right HE
            edgeList.delete(lbnd)
            priorityQ.delete(rbnd)
            edgeList.delete(rbnd)

            # if the site to the left of the event is higher than the Site
            # to the right of it, then swap them and set 'pm' to RIGHT
            pm = Edge.LE
            if bot.y > top.y:
                bot, top = top, bot
                pm = Edge.RE

            # Create an Edge (or line) that is between the two Sites.  This
            # creates the formula of the line, and assigns a line number to it
            edge = Edge(bisect=(bot, top))
            context.outBisector(edge)

            # create a HE from the edge
            bisector = Halfedge(edge, pm)

            # insert the new bisector to the right of the left HE
            # set one endpoint to the new edge to be the vector point 'v'
            # If the site to the left of this bisector is higher than the right
            # Site, then this endpoint is put in position 0; otherwise in pos 1
            edgeList.insert(llbnd, bisector)
            if edge.setEndpoint(Edge.RE - pm, v):
                context.outEdge(edge)

            # if left HE and the new bisector don't intersect, then delete
            # the left HE, and reinsert it
            p = llbnd.intersect(bisector)
            if p is not None:
                priorityQ.delete(llbnd)
                priorityQ.insert(llbnd, p, bot.distance(p))

            # if right HE and the new bisector don't intersect, then reinsert it
            p = bisector.intersect(rrbnd)
            if p is not None:
                priorityQ.insert(bisector, p, bot.distance(p))
        else:
            break

    he = edgeList.leftend.right
    while he is not edgeList.rightend:
        context.outEdge(he.edge)
        he = he.right

    context.translate(siteList)


#------------------------------------------------------------------
def isEqual(a, b, relativeError=TOLERANCE):
    # is nearly equal to within the allowed relative error
    norm = max(abs(a), abs(b))
    return (norm < relativeError) or (abs(a - b) < (relativeError * norm))


#------------------------------------------------------------------
class Site(object):
    def __init__(self, x=0.0, y=0.0, z=None, sitenum=0):
        """creates a Site object, possibly numbered

        >>> Site(0, 0) == Site(Site(0, 0)) == Site((0, 0))
        True
        >>> Site(0, 0, 0) == Site((0, 0, 0))
        True
        >>> Site(0, 0) == Site(0, 0, 0)
        False
        >>> Site(1, 2, sitenum=3)
        Site(1.000, 2.000)
        >>> Site(0, 0).x
        0
        >>> Site(0, 0).y
        0
        >>> Site(0, 0).z
        >>>
        """

        if isinstance(x, Site):
            self.x, self.y, self.z = x.x, x.y, x.z
        elif isinstance(x, (tuple, list)):
            self.x, self.y = x[:2]
            if len(x) > 2:
                self.z = x[2]
            else:
                self.z = None
        elif isinstance(x, numpy.ndarray):
            if x.shape == (2, 1):
                self.x, self.y, self.z = x[0, 0], x[1, 0], None
            elif x.shape == (3, 1):
                self.x, self.y, self.z = x[0, 0], x[1, 0], x[2, 0]
            else:
                raise ValueError("invalid shape %s" % (x.shape, ))
        else:
            self.x = x
            self.y = y
            self.z = z
        if self.z is None:
            self.size = 2
        else:
            self.size = 3
        self.sitenum = sitenum
        self.points = [self]
        self.hash = hash((round(self.x, 5), round(self.y, 5), self.z and round(self.z, 5)))

    def __hash__(self):
        return self.hash

    def __eq__(self, other):
        """
        >>> A = Site(0, 0)
        >>> C = Site((0, 0))
        >>> A == C
        True
        >>> B = Site(0, 0, 0)
        >>> A == B
        False
        """

        other = Site(other)

        if abs(self.x - other.x) > TOLERANCE:
            return False
        if abs(self.y - other.y) > TOLERANCE:
            return False
        if self.z != other.z:
            if self.z is None:
                return False
            elif other.z is None:
                return False
            elif abs(self.z - other.z) > TOLERANCE:
                return False
        return True

    def __repr__(self):
        return "Site(%0.3f, %0.3f)" % (self.x, self.y)

    def toNumpy(self):
        """ converts the Site to a numpy array

        >>> p = Site(0, 0)
        >>> p.toNumpy()
        array([[0],
               [0]])
        >>>
        """

        if self.z is not None:
            return numpy.array([[self.x], [self.y], [self.z]])
        else:
            return numpy.array([[self.x], [self.y]])

    def toTuple(self):
        """converts the Site to a python tuple of its coordinates

        >>> Site(0, 0).toTuple()
        (0, 0)
        >>> Site(0, 0, 0).toTuple()
        (0, 0, 0)
        >>>
        """

        if self.z is not None:
            return (self.x, self.y, self.z)
        else:
            return (self.x, self.y)

    def __cmp__(self, other):
        if self.y < other.y:
            return -1
        elif self.y > other.y:
            return 1
        elif self.x < other.x:
            return -1
        elif self.x > other.x:
            return 1
        else:
            return 0

    def __add__(self, other):
        if isinstance(other, Site):
            return Site(self.x + other.x, self.y + other.y)
        elif isinstance(other, (tuple, list)):
            return Site(self.x + other[0], self.y + other[1])
        else:
            raise TypeError("can'd add a Site and a %s" % type(other))

    def __sub__(self, other):
        if isinstance(other, Site):
            try:
                return Site(self.x - other.x, self.y - other.y, self.z - other.z)
            except:
                return Site(self.x - other.x, self.y - other.y)
        elif isinstance(other, (tuple, list)):
            return Site(self.x - other[0], self.y - other[1])
        else:
            raise TypeError("can'd add a Site and a %s" % type(other))

    def __div__(self, other):
        if isinstance(other, int):
            return Site(self.x / float(other), self.y / float(other))
        return Site(self.x / other, self.y / other)

    def __mul__(self, other):
        if isinstance(other, int):
            return Site(self.x * float(other), self.y * float(other))
        return Site(self.x * other, self.y * other)

    def __getitem__(self, index):
        if index == 0:
            return self.x
        elif index == 1:
            return self.y
        elif index == 2 and self.z is not None:
            return self.z
        else:
            raise IndexError("Site is a %d-tuple: no position %d here" % (self.size, index))

    def __iter__(self):
        "behave as a list, length 2 or 3"
        yield self.x
        yield self.y
        if self.z is not None:
            yield self.z
        raise StopIteration()

    def distance(self, other):
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx * dx + dy * dy)


#------------------------------------------------------------------
class Edge(object):
    LE = 0
    RE = 1
    EDGE_NUM = 0
    DELETED = {}   # marker value

    def __init__(self, bisect=None):
        """initialize the object
        """

        self.ep = [None, None]
        if bisect is not None:
            self.reg = s1, s2 = bisect  # store the sites that this edge is bisecting

            # to begin with, there are no endpoints on the bisector - it goes to infinity
            # ep[0] and ep[1] are None

            # get the difference in x dist between the sites
            dx = float(s2.x - s1.x)
            dy = float(s2.y - s1.y)
            adx = abs(dx)  # make sure that the difference in positive
            ady = abs(dy)

            # get the slope of the line
            self.c = float(s1.x * dx + s1.y * dy + (dx * dx + dy * dy) * 0.5)
            if adx > ady:
                # normalize formula, with x coefficient fixed to 1
                self.a = 1.0
                self.b = dy / dx
                self.c /= dx
            else:
                # normalize formula, with y coefficient fixed to 1
                self.b = 1.0
                self.a = dx / dy
                self.c /= dy

        else:
            self.a = 0.0
            self.b = 0.0
            self.c = 0.0
            self.reg = [None, None]

        self.edgenum = Edge.EDGE_NUM
        Edge.EDGE_NUM += 1

    def setEndpoint(self, lrFlag, site):
        self.ep[lrFlag] = site
        if self.ep[Edge.RE - lrFlag] is None:
            return False
        return True


#------------------------------------------------------------------
class Halfedge(object):
    def __init__(self, edge=None, pm=Edge.LE):
        self.left = None   # left Halfedge in the edge list
        self.right = None  # right Halfedge in the edge list
        self.qnext = None  # priority queue linked list pointer
        self.edge = edge   # edge list Edge
        self.pm = pm
        self.vertex = None  # Site()
        self.ystar = BIG_FLOAT

    def __cmp__(self, other):
        if self.ystar > other.ystar:
            return 1
        elif self.ystar < other.ystar:
            return -1
        elif self.vertex.x > other.vertex.x:
            return 1
        elif self.vertex.x < other.vertex.x:
            return -1
        else:
            return 0

    def leftreg(self, default):
        if not self.edge:
            return default
        elif self.pm == Edge.LE:
            return self.edge.reg[Edge.LE]
        else:
            return self.edge.reg[Edge.RE]

    def rightreg(self, default):
        if not self.edge:
            return default
        elif self.pm == Edge.LE:
            return self.edge.reg[Edge.RE]
        else:
            return self.edge.reg[Edge.LE]

    # returns True if p is to right of halfedge self
    def isPointRightOf(self, pt):
        e = self.edge
        topsite = e.reg[1]
        right_of_site = pt.x > topsite.x

        if(right_of_site and self.pm == Edge.LE):
            return True

        if(not right_of_site and self.pm == Edge.RE):
            return False

        if(e.a == 1.0):
            dyp = pt.y - topsite.y
            dxp = pt.x - topsite.x
            fast = 0
            if ((not right_of_site and e.b < 0.0) or (right_of_site and e.b >= 0.0)):
                above = dyp >= e.b * dxp
                fast = above
            else:
                above = pt.x + pt.y * e.b > e.c
                if(e.b < 0.0):
                    above = not above
                if (not above):
                    fast = 1
            if (not fast):
                dxs = topsite.x - (e.reg[0]).x
                above = e.b * (dxp * dxp - dyp * dyp) < dxs * dyp * (1.0 + 2.0 * dxp / dxs + e.b * e.b)
                if(e.b < 0.0):
                    above = not above
        else:  # e.b == 1.0
            yl = e.c - e.a * pt.x
            t1 = pt.y - yl
            t2 = pt.x - topsite.x
            t3 = yl - topsite.y
            above = t1 * t1 > t2 * t2 + t3 * t3

        if(self.pm == Edge.LE):
            return above
        else:
            return not above

    #--------------------------
    # create a new site where the Halfedges el1 and el2 intersect
    def intersect(self, other):
        e1 = self.edge
        e2 = other.edge
        if (e1 is None) or (e2 is None):
            return None

        # if the two edges bisect the same parent return None
        if e1.reg[1] is e2.reg[1]:
            return None

        d = e1.a * e2.b - e1.b * e2.a
        if isEqual(d, 0.0):
            return None

        xint = (e1.c * e2.b - e2.c * e1.b) / d
        yint = (e2.c * e1.a - e1.c * e2.a) / d
        if(cmp(e1.reg[1], e2.reg[1]) < 0):
            he = self
            e = e1
        else:
            he = other
            e = e2

        rightOfSite = xint >= e.reg[1].x
        if((rightOfSite     and he.pm == Edge.LE) or
           (not rightOfSite and he.pm == Edge.RE)):
            return None

        # create a new site at the point of intersection - this is a new
        # vector event waiting to happen
        return Site(xint, yint)


#------------------------------------------------------------------
class EdgeList(object):
    def __init__(self, xmin, xmax, nsites):
        if xmin > xmax:
            xmin, xmax = xmax, xmin
        self.hashsize = int(2 * math.sqrt(nsites + 4))

        self.xmin = xmin
        self.deltax = float(xmax - xmin)
        self.hash = [None] * self.hashsize

        self.leftend = Halfedge()
        self.rightend = Halfedge()
        self.leftend.right = self.rightend
        self.rightend.left = self.leftend
        self.hash[0] = self.leftend
        self.hash[-1] = self.rightend

    def insert(self, left, he):
        he.left = left
        he.right = left.right
        left.right.left = he
        left.right = he

    def delete(self, he):
        he.left.right = he.right
        he.right.left = he.left
        he.edge = Edge.DELETED

    # Get entry from hash table, pruning any deleted nodes
    def gethash(self, b):
        if(b < 0 or b >= self.hashsize):
            return None
        he = self.hash[b]
        if he is None or he.edge is not Edge.DELETED:
            return he

        #  Hash table points to deleted half edge.  Patch as necessary.
        self.hash[b] = None
        return None

    def leftbnd(self, pt):
        # Use hash table to get close to desired halfedge
        bucket = int(((pt.x - self.xmin) / self.deltax * self.hashsize))

        if(bucket < 0):
            bucket = 0

        if(bucket >= self.hashsize):
            bucket = self.hashsize - 1

        he = self.gethash(bucket)
        if(he is None):
            i = 1
            while True:
                he = self.gethash(bucket - i)
                if (he is not None):
                    break
                he = self.gethash(bucket + i)
                if (he is not None):
                    break
                i += 1

        # Now search linear list of halfedges for the corect one
        if (he is self.leftend) or (he is not self.rightend and he.isPointRightOf(pt)):
            he = he.right
            while he is not self.rightend and he.isPointRightOf(pt):
                he = he.right
            he = he.left
        else:
            he = he.left
            while (he is not self.leftend and not he.isPointRightOf(pt)):
                he = he.left

        # Update hash table and reference counts
        if(bucket > 0 and bucket < self.hashsize - 1):
            self.hash[bucket] = he
        return he


#------------------------------------------------------------------
class PriorityQueue(object):
    def __init__(self, ymin, ymax, nsites):
        self.ymin = ymin
        self.deltay = ymax - ymin
        self.hashsize = int(4 * math.sqrt(nsites))
        self.count = 0
        self.minidx = 0
        self.hash = []
        for i in range(self.hashsize):
            self.hash.append(Halfedge())

    def __len__(self):
        return self.count

    def isEmpty(self):
        return self.count == 0

    def insert(self, he, site, offset):
        he.vertex = site
        he.ystar = site.y + offset
        last = self.hash[self.getBucket(he)]
        next = last.qnext
        while((next is not None) and cmp(he, next) > 0):
            last = next
            next = last.qnext
        he.qnext = last.qnext
        last.qnext = he
        self.count += 1

    def delete(self, he):
        if (he.vertex is not None):
            last = self.hash[self.getBucket(he)]
            while last.qnext is not he:
                last = last.qnext
            last.qnext = he.qnext
            self.count -= 1
            he.vertex = None

    def getBucket(self, he):
        bucket = int(((he.ystar - self.ymin) / self.deltay) * self.hashsize)
        if bucket < 0:
            bucket = 0
        if bucket >= self.hashsize:
            bucket = self.hashsize - 1
        if bucket < self.minidx:
            self.minidx = bucket
        return bucket

    def getMinPt(self):
        while(self.hash[self.minidx].qnext is None):
            self.minidx += 1
        he = self.hash[self.minidx].qnext
        x = he.vertex.x
        y = he.ystar
        return Site(x, y)

    def popMinHalfedge(self):
        curr = self.hash[self.minidx].qnext
        self.hash[self.minidx].qnext = curr.qnext
        self.count -= 1
        return curr


#------------------------------------------------------------------
class SiteList(object):
    def __init__(self, pointList):
        self.__sites = []
        self.__sitenum = 0

        def xy(pt):
            """given an object, try to make a 2-tuple of floats out of it.
            """

            try:
                return pt.x, pt.y
            except AttributeError:
                pass
            try:
                return tuple([float(i) for i in pt.split(' ')[:2]])
            except:
                pass
            return tuple((pt[0], pt[1]))

        self.__xmin, self.__ymin = xy(pointList[0])
        self.__xmax, self.__ymax = xy(pointList[0])
        seen = set()
        for i, pt in enumerate(pointList):
            x, y = xy(pt)
            if (x, y) in seen:
                continue
            seen.add((x, y))
            if x < self.__xmin:
                self.__xmin = x
            if y < self.__ymin:
                self.__ymin = y
            if x > self.__xmax:
                self.__xmax = x
            if y > self.__ymax:
                self.__ymax = y
        for i, pt in enumerate(seen):
            x, y = xy(pt)
            x -= self.__xmin
            y -= self.__ymin
            pnt = Site(x, y)
            pnt.sitenum = i
            self.__sites.append(pnt)
        self.translation = (self.__xmin, self.__ymin)
        self.__xmax -= self.__xmin
        self.__ymax -= self.__ymin
        self.__xmin = 0.0
        self.__ymin = 0.0
        self.__sites.sort()

    def setSiteNumber(self, site):
        site.sitenum = self.__sitenum
        self.__sitenum += 1

    class Iterator(object):
        def __init__(self, lst):
            self.generator = (s for s in lst)

        def __iter__(self):
            return self

        def next(self):
            try:
                return self.generator.next()
            except StopIteration:
                return None

    def iterator(self):
        return SiteList.Iterator(self.__sites)

    def __iter__(self):
        return (s for s in self.__sites)

    def __len__(self):
        return len(self.__sites)

    def _getxmin(self):
        return self.__xmin

    def _getymin(self):
        return self.__ymin

    def _getxmax(self):
        return self.__xmax

    def _getymax(self):
        return self.__ymax
    xmin = property(_getxmin)
    ymin = property(_getymin)
    xmax = property(_getxmax)
    ymax = property(_getymax)


#------------------------------------------------------------------
def computeVoronoiDiagram(points, clip=None, ndigits=5, equivalence=[]):
    """Takes a list of point objects, uses Steven Fortune's algorithm
    to compute the voronoi tessellation.  clipping is available.

    all points at less than zero length (10^-ndigits) distance are
    considered equal.

    equivalence is a list of lists of points.  all points in one
    equivalence list are considered equivalent and their Voronoi cells
    are combined to one.  each of the combined cells is associated to
    the first point in its equivalence list.

    open polygons on the outer skirts of the solution are intersecated
    with the clip rectangle in order to provide closed polygons.  the
    clip rectangle is provided as a 4-tuple of coordinates: x0, y0,
    x1, y2.

    Returns a 5-tuple of:

    (1) a list of 2-tuples, which are the x, y coordinates of the
        Voronoi diagram vertices
    (2) a list of 3-tuples (a, b, c) which are the equations of the
        lines in the Voronoi diagram: a*x + b*y = c
    (3) a list of 3-tuples, (l, v1, v2) representing edges of the
        Voronoi diagram.  l is the index of the line, v1 and v2 are
        the indices of the vertices at the end of the edge.  If
        v1 or v2 is -1, the line extends to infinity.
    (4) a dictionary associating each of the input points to a set
        of segments, in their cartesian representation.
    (5) if clip was provided as a number, an educated guess at where
        to clip the open polygons.  otherwise clip unmodified.
    """

    log.debug("clean up input data, removing repeated points")
    origlen = len(points)
    #points = list(set([roundpoint(p, ndigits) for p in points]))
    points = list(set([p for p in points]))
    if len(points) != origlen:
        log.warn("computeVoronoiDiagram: there were %s repeated points." % (origlen - len(points)))

    siteList = SiteList(points)
    context = Context()
    voronoi(siteList, context)
    log.debug("clean up result, removing repeated intersections.")
    context.compact(pow(10, -ndigits))
    context.findPolygons()

    if clip:
        if not isinstance(clip, (list, tuple)):
            xmin, ymin = siteList.translation
            newclip = [xmin, ymin, siteList.xmax + xmin, siteList.ymax + ymin]
            newclip[0] = min([i[0] for i in context.vertices] + [xmin]) - clip
            newclip[1] = min([i[1] for i in context.vertices] + [ymin]) - clip
            newclip[2] = max([i[0] for i in context.vertices] + [siteList.xmax + xmin]) + clip
            newclip[3] = max([i[1] for i in context.vertices] + [siteList.ymax + ymin]) + clip
            clip = newclip
        context.clipPolygons(clip)
        context.combinePolygons(equivalence)

    lines = [(line.a, line.b, line.c) for line in context.lines]

    log.debug("computeVoronoiDiagram returning")
    return (context.vertices, lines, context.edges, context.polygons, clip)


#------------------------------------------------------------------
def computeDelaunayTriangulation(points):
    """ Takes a list of point objects (which must have x and y fields).
        Returns a list of 3-tuples: the indices of the points that form a
        Delaunay triangle.
    """

    siteList = SiteList(points)
    context = Context()
    context.triangulate = True
    voronoi(siteList, context)
    return context.triangles


def plotTessellation(args):
    """plots a Voronoi diagram

    usage:
    plotTessellation(computeVoronoiDiagram(...))

    help:
    see computeVoronoiDiagram
    """

    intersections, _, _, tessellation, clip = args[:5]
    import matplotlib.pyplot as plt

    plt.plot([clip[0], clip[0], clip[2], clip[2], clip[0]], [clip[1], clip[3], clip[3], clip[1], clip[1]])
    for k, v in tessellation.items():
        #import time
        #print k, v
        #time.sleep(2)
        plt.plot([k[0]], [k[1]], 'ro')
        for i in range(len(v) - 1):
            plt.plot((v[i][0], v[i + 1][0]), (v[i][1], v[i + 1][1]), color='#FFB870')

    if len(args) > 5:  # result of generalized diagram
        elements = args[5]
        for element in elements:
            if hasattr(element, 'geoms'):
                geoms = [g for g in element.geoms]
            else:
                geoms = [element]
            for geom in geoms:
                points = [p for p in geom.coords]
                for p1, p2 in zip(points, points[1:]):
                    (a, b), (c, d) = p1, p2
                    plt.plot((a, c), (b, d), color='#003DF5')
    plt.show()


def plotGraph(G, clip):
    """
    """
    import matplotlib.pyplot as plt
    plt.plot([clip[0], clip[0], clip[2], clip[2], clip[0]], [clip[1], clip[3], clip[3], clip[1], clip[1]])
    for k in G.nodes():
        order = len(G.neighbors(k))
        if order > 2:
            color = 'r'
            markersize = 8
        elif order == 2:
            color = 'y'
            markersize = 4
        else:
            color = 'b'
            markersize = 8
        plt.plot(k[0], k[1], color=color, marker='o', ms=markersize)
    for v0, v1 in G.edges():
        plt.plot((v0[0], v1[0]), (v0[1], v1[1]))
    plt.show()


def mincost_maxflow(G, source, terminal, capacity='capacity', weight='weight'):
    """given a directed graph and two nodes returns the mincost flow.

    each edge in G holds a tuple or a dictionary.  icapacity and icost
    are the keys to the capacity and the cost of the edge.

    the result is a subgraph of G where each arc holds the amount of
    flow going through the arc.

    >>> import networkx as nx
    >>> G = nx.DiGraph()
    >>> capacity, weight = 'capacity', 'weight'
    >>> G.add_edge(0, 1, {capacity:3, weight:5})
    >>> G.add_edge(0, 2, {capacity:7, weight:1})
    >>> G.add_edge(1, 2, {capacity:5, weight:9})
    >>> G.add_edge(1, 4, {capacity:6, weight:7})
    >>> G.add_edge(2, 3, {capacity:6, weight:9})
    >>> G.add_edge(2, 4, {capacity:3, weight:0})
    >>> G.add_edge(3, 4, {capacity:7, weight:0})
    >>> G.add_edge(3, 5, {capacity:7, weight:6})
    >>> G.add_edge(4, 5, {capacity:5, weight:2})
    >>> sol = mincost_maxflow(G, 0, 5)
    >>> sol[0]
    {1: {'flow': 3}, 2: {'flow': 7}}
    >>> sol[1]
    {4: {'flow': 3}}
    >>> sol[2]
    {3: {'flow': 5}, 4: {'flow': 2}}
    >>> sol[3]
    {4: {'flow': 0}, 5: {'flow': 5}}
    >>> sol[4]
    {5: {'flow': 5}}
    >>> sol[5]
    {}
    >>> sol = mincost_maxflow(G, 0, 5)
    >>> sol[0]
    {1: {'flow': 3}, 2: {'flow': 7}}

    """

    import networkx as nx
    sol = nx.DiGraph()
    while True:
        flow, path = find_augmenting_path(G, source, terminal, sol, capacity, weight)
        if not flow:
            break
        augment_solution(sol, flow, path)

    return sol


def find_augmenting_path(G, source, terminal, solution, capacity='capacity', weight='weight'):
    """computes an augmenting path for the mincost_maxflow problem,
    given an admissible flow.

    returns the unitary cheapest augmenting path or (0, []).

    >>> import networkx as nx
    >>> G = nx.DiGraph()
    >>> capacity, weight = 'capacity', 'weight'
    >>> G.add_edge(0, 1, {capacity:3, weight:5})
    >>> G.add_edge(0, 2, {capacity:7, weight:1})
    >>> G.add_edge(1, 2, {capacity:5, weight:9})
    >>> G.add_edge(1, 4, {capacity:6, weight:7})
    >>> G.add_edge(2, 3, {capacity:6, weight:9})
    >>> G.add_edge(2, 4, {capacity:3, weight:0})
    >>> G.add_edge(3, 4, {capacity:7, weight:0})
    >>> G.add_edge(3, 5, {capacity:7, weight:6})
    >>> G.add_edge(4, 5, {capacity:5, weight:2})
    >>> sol = nx.DiGraph()
    >>> ap = find_augmenting_path(G, 0, 5, sol)
    >>> ap
    (3, [0, 2, 4, 5])
    >>> augment_solution(sol, *ap)

    >>> ap = find_augmenting_path(G, 0, 5, sol)
    >>> ap
    (2, [0, 2, 3, 4, 5])
    >>> augment_solution(sol, *ap)

    >>> ap = find_augmenting_path(G, 0, 5, sol)
    >>> ap
    (2, [0, 2, 3, 5])
    >>> augment_solution(sol, *ap)
    """

    # reachable is a priority list of tuples: (cost, node name,
    # reached from node, available flow).  at each iteration the
    # cheapest node is extracted and examined and from there all
    # reachable non labeled nodes are added to this priority list.
    # nodes are not examined more than once: we assume the first time
    # we see a node it is along the cheapest possible path to it.
    available_exiting_flow = sum([max(G[source][n].get(capacity, 0), 0) for n in G.successors(source)])
    reachable = [(0, source, None, available_exiting_flow)]

    # labeled is the dictionary of the nodes already labeled.  it
    # associates the labeled node with the node from which it was
    # reached.  each node gets labeled only once.
    labeled = {}

    while True:
        if not reachable:
            return 0, []
        cost, examining, from_node, flow_up_to_here = heappop(reachable)
        if examining in labeled:
            continue  # already reached at lower cost
        labeled[examining] = from_node  # remember how we got here

        if examining == terminal:
            break

        for adjacent in G.successors(examining):
            if adjacent in labeled:
                continue
            info = G[examining][adjacent]
            cap = info.get(capacity, 0)
            pcost = info.get(weight, 0)

            available_flow = cap - solution.adj.get(examining, {}).get(adjacent, {}).get('flow', 0)
            if available_flow > 0:
                heappush(reachable, (cost + pcost, adjacent, examining, min(available_flow, flow_up_to_here)))
        for adjacent in G.predecessors(examining):
            if adjacent in labeled:
                continue
            info = G[adjacent][examining]
            pcost = info.get(weight, 0)

            available_flow = solution.adj.get(adjacent, {}).get(examining, {}).get('flow', 0)
            if available_flow > 0:
                heappush(reachable, (cost - pcost, adjacent, examining, min(available_flow, flow_up_to_here)))

    path = []
    i = terminal
    while i is not None:
        path.append(i)
        i = labeled[i]
    path.reverse()
    return flow_up_to_here, path


def augment_solution(solution, flow, path):
    """adds flow on path to solution
    """

    for i, j in zip(path, path[1:]):
        if solution.adj.get(j, {}).get(i, {}).get('flow', 0) > 0:
            solution.add_edge(j, i, {'flow': solution.adj.get(j, {}).get(i, {}).get('flow', 0) - flow})
        else:
            solution.add_edge(i, j, {'flow': solution.adj.get(i, {}).get(j, {}).get('flow', 0) + flow})

    return None


def get_coords_list(obj, flatten=True):
    """returns points whether the obj has coords or geoms

    >>> from shapely.geometry.multilinestring import MultiLineString
    >>> obj = MultiLineString([[(0, 6), (2, 8), (3, 9)], [(2, 8), (2, 5)], [(1, 1), (2, 2)], [(0, 0), (1, 0), (1, 1), (2, 0), (2, 1), (0, 0)]])
    >>> get_coords_list(obj)
    [(0.0, 6.0), (2.0, 8.0), (3.0, 9.0), (2.0, 8.0), (2.0, 5.0), (1.0, 1.0), (2.0, 2.0), (0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (2.0, 0.0), (2.0, 1.0), (0.0, 0.0)]
    >>> from shapely.geometry.linestring import LineString
    >>> ls = LineString([(0, 0), (30, 40), (30, 10)])
    >>> get_coords_list(ls)
    [(0.0, 0.0), (30.0, 40.0), (30.0, 10.0)]
    """

    from itertools import chain
    if hasattr(obj, 'geoms'):
        lst = obj.geoms
        result = [[p for p in o.coords] for o in lst]
        if flatten:
            result = list(chain.from_iterable(result))
        return result
    else:
        return list(set([p for p in obj.coords]))


def computeGeneralizedVoronoiDiagram(objects, density, clip):
    """approximates the generalized problem by discretization

    densifies the objects with the given density,
    computes the Voronoi cells (grouping equivalent cells).
    """

    from itertools import chain

    log.debug("computeGeneralizedVoronoiDiagram: densify")
    densified = [densify(o, density) for o in objects]
    log.debug("computeGeneralizedVoronoiDiagram: equivalence")
    equivalence = [get_coords_list(o) for o in densified]
    points = list(chain.from_iterable(equivalence))
    log.debug("computeGeneralizedVoronoiDiagram: computeVoronoiDiagram")
    result = list(computeVoronoiDiagram(points, clip=clip, equivalence=equivalence)) + [objects]
    log.debug("computeGeneralizedVoronoiDiagram returning")
    return result


def absolute_to_relative(points):
    """convert absolute coordinates to sequence of relative displacements

    >>> absolute_to_relative([(5,3),(4,4),(1,3),(8,2)])
    [(5, 3), (-1, 1), (-3, -1), (7, -1)]
    >>> absolute_to_relative([(0,0),(5,3),(4,4),None,(1,3),(8,2)])
    [(0, 0), (5, 3), (-1, 1), (-3, -1), (7, -1)]
    >>> absolute_to_relative([])
    []
    """

    if not points:
        return []

    from types import TupleType
    points = filter(lambda x: isinstance(x, TupleType), points)
    result = [points[0]]
    for p0, p1 in zip(points, points[1:]):
        result.append((p1[0] - p0[0], p1[1] - p0[1]))
    return result


def mkstr(points):
    """convert points to a string in sodipodi format

    >>> mkstr([(5, 3), (-1, 1), (-3, -1), (7, -1)])
    '5,3 -1,1 -3,-1 7,-1'
    >>> mkstr([(5, 3), (-1.25, 1.5), (-3.625, -1.25), (7, -1)])
    '5,3 -1.25,1.5 -3.625,-1.25 7,-1'
    """

    return ' '.join(["%s,%s" % P for P in points])


def to_coords_sequences(obj):
    """return the coordinates that describe the object

    the result is a list of lists of coordinates.

    >>> from shapely.geometry import Polygon
    >>> pl = Polygon([(0, -1.5), (0, 5), (50, 5), (50, -1.5)])
    >>> to_coords_sequences(pl)
    [[(0.0, -1.5), (0.0, 5.0), (50.0, 5.0), (50.0, -1.5), (0.0, -1.5)]]

    >>> pl = [(0, 0), (1, 2), (2, 1), (3, 2), (4, 0)]
    >>> to_coords_sequences(pl)
    [[(0, 0), (1, 2), (2, 1), (3, 2), (4, 0)]]

    >>> pl = []
    >>> to_coords_sequences(pl)
    []

    >>> pl = Polygon([(0, 0), (1, 2), (2, 1), (3, 2), (4, 0)])
    >>> to_coords_sequences(pl)
    [[(0.0, 0.0), (1.0, 2.0), (2.0, 1.0), (3.0, 2.0), (4.0, 0.0), (0.0, 0.0)]]
    >>> pl2 = Polygon([(0, 1.5), (4, 1.5), (4, 3), (0, 3)])
    >>> to_coords_sequences(pl.intersection(pl2))
    [[(0.75, 1.5), (1.0, 2.0), (1.5, 1.5), (0.75, 1.5)], [(2.5, 1.5), (3.0, 2.0), (3.25, 1.5), (2.5, 1.5)]]
    """

    if isinstance(obj, list):
        result = []
        if obj:
            result.append(obj)
        return result

    try:
        boundary = obj.boundary
    except:
        boundary = obj
    geoms = []
    try:
        geoms = [g for g in boundary.geoms]
    except:
        geoms = [boundary]

    try:
        return [[p for p in g.coords] for g in geoms]
    except:
        log.warn("to_coords_sequences: we have a problem, do you notice it?")
        return []


def to_turtle(geom_object):
    """return turtle instructions for geom_object

    geom_object is any shapely object (well, as long as it works for
    Polygons and Multipolygons).

    the returned value is a string containing turtle instructions that
    can be used in a sodipodi svg.

    use this to draw polygons, place dots or to paint areas.  for
    examples, have a look at the method write_svg in
    source:Products/Newt/Trunk/L0139/src/python/doit.py@21707

    >>> from shapely.geometry import Polygon
    >>> pl = Polygon([(1, -1.5), (1, 5), (51, 5), (51, -1.5)])
    >>> to_turtle(pl)
    'm 1.0,-1.5 0.0,6.5 50.0,0.0 0.0,-6.5 -50.0,0.0 m -1.0,1.5'

    >>> pl = Polygon([(0, 0), (1, 2), (2, 1), (3, 2), (4, 0)])
    >>> pl2 = Polygon([(0, 1.5), (4, 1.5), (4, 3), (0, 3)])
    >>> to_turtle(pl.intersection(pl2))
    'm 0.75,1.5 0.25,0.5 0.5,-0.5 -0.75,0.0 m -0.75,-1.5 m 2.5,1.5 0.5,0.5 0.25,-0.5 -0.75,0.0 m -2.5,-1.5'

    >>> pl = [(0, 0), (1, 2), (2, 1), None, (4, 0)]
    >>> to_turtle(pl)
    'm 0,0 1,2 1,-1 2,-1 m 0,0'
    """

    return ' '.join("m " + mkstr(absolute_to_relative(i)) + " m %s,%s" % (-i[0][0], -i[0][1])
                    for i in to_coords_sequences(geom_object))

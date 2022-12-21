#!/usr/bin/env python
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
# Copyright 2009 Mario Frasca
#
#***********************************************************************
#* Library    : some mathematical utilities
#*
#* Project    : various
#*
#* $Id$
#*
#* initial programmer :  Mario Frasca
#* initial date       :  2009-07-17
#**********************************************************************

__revision__ = "$Rev$"[6:-2]

import logging
log = logging.getLogger('nens.math')

import math


class Memoize:
    """Memoize(fn) - an instance which acts like fn but memoizes its arguments.

       Will only work on functions with non-mutable arguments.
    """
    def __init__(self, fn):
        self.fn = fn
        self.memo = {}

    def __call__(self, *args):
        if args not in self.memo:
            self.memo[args] = self.fn(*args)
        return self.memo[args]


def Tn(n, x):
    if n == 0:
        return 1.0
    elif n == 1:
        return float(x)
    else:
        return (2.0 * x * Tn(n - 1, x)) - Tn(n - 2, x)


class Chebyshev:
    """a linear combination of chebyshev polynomials

    initialize:
      - fit data (given the data, optionally the degree)
      - approximate a function (give the function and the degree)
      - from n coefficients (you want exactly this combination.

    use:
      - evaluation.
      - inverse evaluation.
    """

    def __init__(self, data=None, function=None, degree=None, coefficients=None):
        self.Tn = Memoize(Tn)
        if coefficients is not None:
            self.coefficients = coefficients
            self.degree = len(coefficients) - 1
            self.range = (-1.0, 1.0)
            self.halfwidth = 1.0
            assert(self.degree > 1)
        elif data is not None:
            self.fit(data, degree)
        elif function is not None:
            self.approximate(function)

    def fit(self, data, degree=None):
        """fit the data by a 'minimal squares' linear combination of chebyshev polinomials.

        cfr: Conte, de Boor; elementary numerical analysis; Mc Grow Hill (6.2: Data Fitting)
        """

        import numpy
        import numpy.linalg

        if degree is None:
            degree = 5

        data = sorted(data)
        self.range = start, end = (min(data)[0], max(data)[0])
        self.halfwidth = (end - start) / 2.0
        vec_x = [(x - start - self.halfwidth) / self.halfwidth for (x, y) in data]
        vec_f = [y for (x, y) in data]

        mat_phi = [numpy.array([self.Tn(i, x) for x in vec_x]) for i in range(degree + 1)]
        mat_A = numpy.inner(mat_phi, mat_phi)
        vec_b = numpy.inner(vec_f, mat_phi)

        self.coefficients = numpy.linalg.solve(mat_A, vec_b)
        self.degree = degree

    def approximate(self, function, degree):
        """interpolate the function at the chebyshev points for the chosen degree
        """
        pass

    def define(self, coefficients):
        self.coefficients = coefficients
        self.degree = len(coefficients) - 1
        assert(self.degree > 1)
        pass

    def evaluate(self, x):
        """evaluate me at x using the Clenshaw algorithm

        http://en.wikipedia.org/wiki/Clenshaw_algorithm
        """

        x = (x - self.range[0] - self.halfwidth) / self.halfwidth

        b_2 = float(self.coefficients[self.degree])
        b_1 = 2 * x * b_2 + float(self.coefficients[self.degree - 1])

        for i in range(2, self.degree):
            b_1, b_2 = 2.0 * x * b_1 + self.coefficients[self.degree - i] - b_2, b_1
        else:
            b_0 = x * b_1 + self.coefficients[0] - b_2

        return b_0

    def __call__(self, x):
        return self.evaluate(x)

    def inverse_evaluate(self, y):
        pass


def erf(x):
    """evaluate the 'error function'.

    based on Abramowitz and Stegun 7.1.26
    (http://www.math.sfu.ca/~cbm/aands/frameindex.htm)
    """

    # save the sign of x
    sign = 1
    if x < 0:
        sign = -1
    x = abs(x)

    # constants
    a1 = 0.254829592
    a2 = -0.284496736
    a3 = 1.421413741
    a4 = -1.453152027
    a5 = 1.061405429
    p = 0.3275911

    # A&S formula 7.1.26
    t = 1.0 / (1.0 + p * x)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-x * x)
    return sign * y  # erf(-x) = -erf(x)


def norm_cdf(x):
    """approximate the normal cumulative distribution function

    based on the error function and the relationship
    x 2 sqrt * norm_cdf 2 * 1 - x erf ==

    >>> norm_cdf(0) # doctest: +ELLIPSIS
    0.50000...
    >>> norm_cdf(-1) # doctest: +ELLIPSIS
    0.15865...
    >>> norm_cdf(1) # doctest: +ELLIPSIS
    0.84134...
    """

    return (erf(x / math.sqrt(2)) + 1) / 2

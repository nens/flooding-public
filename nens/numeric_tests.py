import unittest

from numeric import Chebyshev
from numeric import Tn
from numeric import norm_cdf


class MathTest(unittest.TestCase):
    def assertAlmostEquals(self, x1, x2):
        self.assertEquals(round(x1, 8), round(x2, 8))


class TestEvaluation(MathTest):
    def test01(self):
        "evaluation of [0.2, 1.5, 0.3, 0.07]|0.2"
        p = Chebyshev(coefficients=[0.2, 1.5, 0.3, 0.07])
        self.assertAlmostEquals(p.evaluate(0.2), sum([p.coefficients[i] * Tn(i, 0.2) for i in range(4)]))

    def test02(self):
        "evaluation of [0.2, 1.5, 0.3, 0.07]|0.4"
        p = Chebyshev(coefficients=[0.2, 1.5, 0.3, 0.07])
        self.assertAlmostEquals(p.evaluate(0.4), sum([p.coefficients[i] * Tn(i, 0.4) for i in range(4)]))

    def test03(self):
        "evaluation of [0.2, 1.5, 0.3, 0.07]|0.6"
        p = Chebyshev(coefficients=[0.2, 1.5, 0.3, 0.07])
        self.assertAlmostEquals(p.evaluate(0.6), sum([p.coefficients[i] * Tn(i, 0.6) for i in range(4)]))

    def test04(self):
        "evaluation of [0.2, 1.5, 0.3, 0.07]|0.95"
        p = Chebyshev(coefficients=[0.2, 1.5, 0.3, 0.07])
        self.assertAlmostEquals(p.evaluate(0.95), sum([p.coefficients[i] * Tn(i, 0.95) for i in range(4)]))


class TestFitting(MathTest):
    def test000(self):
        "fit a constant with a constant"
        data = [(-0.75, 1), (0.75, 1)]
        p = Chebyshev(data=data, degree=0)
        self.assertEquals(p.degree, 0)
        self.assertEquals(p.coefficients[0], 1)

    def test001(self):
        "fit a constant (with errors) with a constant"
        data = [(-0.75, 1.1), (0.75, 0.9)]
        p = Chebyshev(data=data, degree=0)
        self.assertEquals(p.degree, 0)
        self.assertEquals(p.coefficients[0], 1)

    def test002(self):
        "fit a constant (with errors) with a constant"
        data = [(-0.75, 1.1), (-0.5, 1.15), (0.5, 0.85), (0.75, 0.9)]
        p = Chebyshev(data=data, degree=0)
        self.assertEquals(p.degree, 0)
        self.assertEquals(p.coefficients[0], 1)

    def test012(self):
        "fit a constant (with errors) with degree 1"
        data = [(-0.75, 1.1), (-0.5, 0.9), (0.5, 0.9), (0.75, 1.1)]
        p = Chebyshev(data=data, degree=1)
        self.assertEquals(p.degree, 1)
        self.assertAlmostEquals(p.coefficients[0], 1)
        self.assertAlmostEquals(p.coefficients[1], 0)

    def test014(self):
        "straight line fit, with periodic errors"
        import math
        data = [(-1.0 + i / 10.0, y) for (i, y) in enumerate([i / 10.0 + math.cos(float(i)) / 8 for i in range(-10, 11)])]
        p = Chebyshev(data=data, degree=1)
        self.assertAlmostEquals(p.degree, 1)
        self.assertAlmostEquals(p.coefficients[1], 1.0)

        data = [(-1.0 + i / 10.0, y) for (i, y) in enumerate([i / 10.0 + math.sin(float(i)) / 8 for i in range(-10, 11)])]
        p = Chebyshev(data=data, degree=1)
        self.assertAlmostEquals(p.degree, 1)
        self.assertAlmostEquals(p.coefficients[0], 0.0)

    def test019(self):
        "straight line data fit, figure 6.5"
        data = [(-1.0 + i / 5.0, y) for (i, y) in enumerate([0.0, 0.6, 1.77, 1.92, 3.31, 3.52, 4.59, 5.31, 5.79, 7.06, 7.17])]
        p = Chebyshev(data=data, degree=1)
        self.assertEquals(p.degree, 1)
        self.assertAlmostEquals(p.coefficients[0], 3.730909090909091)
        self.assertAlmostEquals(p.coefficients[1], 3.7186363636363629)

    def test020(self):
        "second degree fit of exact second degree polynomial"
        def f(x):
            return -3 * x * x + 2.4 * x - 1.5

        vec_x = [float(i) / 10 - 1 for i in range(21)]
        data = [(x, f(x)) for x in vec_x]
        p = Chebyshev(data=data, degree=2)
        self.assertEquals(p.degree, 2)
        for x in vec_x:
            self.assertAlmostEquals(p.evaluate(x), f(x))
        for calculated, expected in zip(p.coefficients, [-3., 2.4, -1.5]):
            self.assertAlmostEquals(calculated, expected)

    def test120(self):
        "second degree fit of exact second degree polynomial, range (1, 3)"
        def f(x):
            x = x - 2.0
            return -3 * x * x + 2.4 * x - 1.5

        vec_x = [float(i) / 5 + 1 for i in range(11)]
        data = [(x, f(x)) for x in vec_x]
        p = Chebyshev(data=data, degree=2)
        self.assertEquals(p.range, (1.0, 3.0))
        self.assertEquals(p.degree, 2)
        for calculated, expected in zip(p.coefficients, [-3., 2.4, -1.5]):
            self.assertAlmostEquals(calculated, expected)
        for x in vec_x:
            self.assertAlmostEquals(p.evaluate(x), f(x))


class DoctestRunner(unittest.TestCase):
    def test0000(self):
        import doctest
        doctest.testmod(name=__name__[:-6])


class NormCdf(unittest.TestCase):
    def test0001(self):
        self.assertTrue(abs(0.5 - norm_cdf(0)) < 0.000000001)

    def test0002(self):
        self.assertTrue(abs(0.15865 - norm_cdf(-1)) < 0.00001)

    def test0003(self):
        self.assertTrue(abs(0.84134 - norm_cdf(1)) < 0.00001)

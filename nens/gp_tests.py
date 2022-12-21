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
import logging
import sys
import types
from gp import gp_iterator
from gp import join_dicts
from gp import get_table
from gp import check_constraints
from gp import named_in_conversion
from gp import join_on_foreign_key
from gp import reverse_dict
from gp import replace_notavalue
from gp import GpHandler
from gp import join_on_primary_key
from gp import gp_as_dict
from gp import split_constraints
from gp import loggable_name
from gp import get_table_def
from gp import validfilename
from gp import firstAvailableFilename


class IteratorTest(unittest.TestCase):
    def test0iterator(self):
        "testing iterator"
        c = mock.GpDispatch.Cursor([{'key1': 'v1', 'key2': 'v2'},
                                    {'key1': 'v1', 'key2': 'v3'},
                                    {'key1': 'v1', 'key2': 'v4'},
                                    ])
        for i in gp_iterator(c):
            self.assertEqual(i.key1, "v1")

    def test1iterator(self):
        "iterators are subscriptable"
        c = mock.GpDispatch.Cursor([{'key1': 'v1', 'key2': 'v2'},
                                    {'key1': 'v1', 'key2': 'v3'},
                                    {'key1': 'v1', 'key2': 'v4'},
                                    ])
        it = gp_iterator(c)
        self.assertEqual(it[2].key2, "v4")

    def test2iterator(self):
        "iterators are only forward subscriptable"
        c = mock.GpDispatch.Cursor([{'key1': 'v1', 'key2': 'v2'},
                                    {'key1': 'v1', 'key2': 'v3'},
                                    {'key1': 'v1', 'key2': 'v4'},
                                    ])
        it = gp_iterator(c)
        self.assertEqual(it[0].key2, "v2")
        self.assertEqual(it[2].key2, "v4")
        self.assertRaises(IndexError, it.__getitem__, 0)


class DictJoinTest(unittest.TestCase):
    def test0dictjoin(self):
        "testing join on dictionary lists"
        pass

    def test1dictjoin(self):
        "simple case"
        dl1 = [{1:1, 2:2}, {1:4, 2:3}]
        dl2 = [{1:1, 3:2}, {1:4, 3:3}]
        key = 1
        result = [{1:1, 2:2, 3:2}, {1:4, 2:3, 3:3}]
        self.assertEqual(join_dicts(dl1, dl2, key), result)

    def test2dictjoin(self):
        "second overwrites first"
        dl1 = [{1:1, 2:2}, {1:4, 2:3}]
        dl2 = [{1:1, 3:2}, {1:4, 3:3, 2:2}]
        key = 1
        result = [{1:1, 2:2, 3:2}, {1:4, 2:2, 3:3}]
        self.assertEqual(join_dicts(dl1, dl2, key), result)

    def test3dictjoin(self):
        "does not force fields"
        dl1 = [{1:1, 2:2}, {1:4, 2:3}]
        dl2 = [{1:1, 3:2}, {1:4}]
        key = 1
        result = [{1:1, 2:2, 3:2}, {1:4, 2:3}]
        self.assertEqual(join_dicts(dl1, dl2, key), result)

    def test4dictjoin(self):
        "silently ignores elements from second list if non matching"
        dl1 = [{1:1, 2:2}, {1:4, 2:3}]
        dl2 = [{1:1, 3:2}, {1:4, 3:3}, {1:5, 3:9}]
        key = 1
        result = [{1:1, 2:2, 3:2}, {1:4, 2:3, 3:3}]
        self.assertEqual(join_dicts(dl1, dl2, key), result)

    def test5dictjoin(self):
        "silently ignores missing elements from second list"
        dl1 = [{1:1, 2:2}, {1:4, 2:3}]
        dl2 = [{1:1, 3:2}, {1:5, 3:9}]
        key = 1
        result = [{1:1, 2:2, 3:2}, {1:4, 2:3, }]
        self.assertEqual(join_dicts(dl1, dl2, key), result)

    def test6dictjoin(self):
        "simple case with different key on second list"
        dl1 = [{1:1, 2:2}, {1:4, 2:3}]
        dl2 = [{5:1, 3:2}, {5:4, 3:9}]
        key1 = 1
        key2 = 5
        result = [{1:1, 5:1, 2:2, 3:2}, {1:4, 5:4, 2:3, 3:9}]
        self.assertEqual(join_dicts(dl1, dl2, key1, key2), result)

    def test7dictjoin(self):
        "join is case insensitive and returns lower case keys"
        dl1 = [{'abc':1, 2:2}, {'abc':4, 2:3}]
        dl2 = [{'abc':1, 3:2}, {'abc':4, 3:9}]
        key1 = 'Abc'
        result = [{'abc':1, 2:2, 3:2}, {'abc':4, 2:3, 3:9}]
        self.assertEqual(join_dicts(dl1, dl2, key1), result)


class GetTableTest(unittest.TestCase):
    def test0gettable(self):
        "get table from geoprocessor returns lower case keys"
        tableIn = [
            {'Abc': 123, 'eee': 414, 'DEF': 256, 'test': 987, 'Finis': 999},
            {'Abc': 124, 'eee': 424, 'DEF': 356, 'test': 887, 'Finis': 999},
            {'Abc': 125, 'eee': 434, 'DEF': 456, 'test': 787, 'Finis': 999},
            {'Abc': 126, 'eee': 444, 'DEF': 556, 'test': 687, 'Finis': 999},
            {'Abc': 127, 'eee': 454, 'DEF': 656, 'test': 587, 'Finis': 999},
            {'Abc': 128, 'eee': 464, 'DEF': 756, 'test': 487, 'Finis': 999},
            {'Abc': 129, 'eee': 474, 'DEF': 856, 'test': 387, 'Finis': 999},
            ]
        tableExpect = [
            {'abc': 123, 'eee': 414, 'def': 256, 'test': 987, 'finis': 999},
            {'abc': 124, 'eee': 424, 'def': 356, 'test': 887, 'finis': 999},
            {'abc': 125, 'eee': 434, 'def': 456, 'test': 787, 'finis': 999},
            {'abc': 126, 'eee': 444, 'def': 556, 'test': 687, 'finis': 999},
            {'abc': 127, 'eee': 454, 'def': 656, 'test': 587, 'finis': 999},
            {'abc': 128, 'eee': 464, 'def': 756, 'test': 487, 'finis': 999},
            {'abc': 129, 'eee': 474, 'def': 856, 'test': 387, 'finis': 999},
            ]
        gp = mock.GpDispatch(default_table=tableIn)
        # first check that the mock gp respects upper/lower case
        fields = [i.name for i in gp_iterator(gp.ListFields(''))]
        self.assertEqual(fields, ['Abc', 'DEF', 'Finis', 'eee', 'test'])
        # then check that our library converts to lower case
        tableOut = get_table(gp, "nomeACaso")
        self.assertEqual(tableOut, tableExpect)
        pass

    def test1gettable(self):
        "get table with field name translation - as dict"
        tableIn = [
            {'Abc': 123, 'eee': 414, 'DEF': 256, 'test': 987, 'Finis': 999},
            {'Abc': 124, 'eee': 424, 'DEF': 356, 'test': 887, 'Finis': 999},
            {'Abc': 125, 'eee': 434, 'DEF': 456, 'test': 787, 'Finis': 999},
            {'Abc': 126, 'eee': 444, 'DEF': 556, 'test': 687, 'Finis': 999},
            {'Abc': 127, 'eee': 454, 'DEF': 656, 'test': 587, 'Finis': 999},
            {'Abc': 128, 'eee': 464, 'DEF': 756, 'test': 487, 'Finis': 999},
            {'Abc': 129, 'eee': 474, 'DEF': 856, 'test': 387, 'Finis': 999},
            ]
        tableExpect = [
            {'st': 123, 'nd': 414, 'rd': 256, 'th': 987, 'finis': 999},
            {'st': 124, 'nd': 424, 'rd': 356, 'th': 887, 'finis': 999},
            {'st': 125, 'nd': 434, 'rd': 456, 'th': 787, 'finis': 999},
            {'st': 126, 'nd': 444, 'rd': 556, 'th': 687, 'finis': 999},
            {'st': 127, 'nd': 454, 'rd': 656, 'th': 587, 'finis': 999},
            {'st': 128, 'nd': 464, 'rd': 756, 'th': 487, 'finis': 999},
            {'st': 129, 'nd': 474, 'rd': 856, 'th': 387, 'finis': 999},
            ]
        conversion = {'st': 'abc',
                      'nd': 'eee',
                      'rd': 'def',
                      'th': 'test',
                      }
        gp = mock.GpDispatch(default_table=tableIn)
        # check that our library converts to lower case
        tableOut = get_table(gp, "nomeACaso", conversion=conversion)
        self.assertEqual(tableOut, tableExpect)
        pass

    def test2gettable(self):
        "get table with field name translation - as tuple of pairs"
        tableIn = [
            {'Abc': 123, 'eee': 414, 'DEF': 256, 'test': 987, 'Finis': 999},
            {'Abc': 124, 'eee': 424, 'DEF': 356, 'test': 887, 'Finis': 999},
            {'Abc': 125, 'eee': 434, 'DEF': 456, 'test': 787, 'Finis': 999},
            {'Abc': 126, 'eee': 444, 'DEF': 556, 'test': 687, 'Finis': 999},
            {'Abc': 127, 'eee': 454, 'DEF': 656, 'test': 587, 'Finis': 999},
            {'Abc': 128, 'eee': 464, 'DEF': 756, 'test': 487, 'Finis': 999},
            {'Abc': 129, 'eee': 474, 'DEF': 856, 'test': 387, 'Finis': 999},
            ]
        tableExpect = [
            {'st': 123, 'nd': 414, 'rd': 256, 'th': 987, 'finis': 999},
            {'st': 124, 'nd': 424, 'rd': 356, 'th': 887, 'finis': 999},
            {'st': 125, 'nd': 434, 'rd': 456, 'th': 787, 'finis': 999},
            {'st': 126, 'nd': 444, 'rd': 556, 'th': 687, 'finis': 999},
            {'st': 127, 'nd': 454, 'rd': 656, 'th': 587, 'finis': 999},
            {'st': 128, 'nd': 464, 'rd': 756, 'th': 487, 'finis': 999},
            {'st': 129, 'nd': 474, 'rd': 856, 'th': 387, 'finis': 999},
            ]
        conversion = (('st', 'abc'),
                      ('nd', 'eee'),
                      ('rd', 'def'),
                      ('th', 'test'),
                      )
        gp = mock.GpDispatch(default_table=tableIn)
        # check that our library converts to lower case
        tableOut = get_table(gp, "nomeACaso", conversion=conversion)
        self.assertEqual(tableOut, tableExpect)
        pass

    def test30gettable(self):
        "get table with field name translation - with multiple values on right hand side"
        tableIn1 = [
            {'Abc': 123, 'eee': 414, 'DEF': 256, 'test': 987, 'Finis': 999},
            {'Abc': 124, 'eee': 424, 'DEF': 356, 'test': 887, 'Finis': 999},
            ]
        tableIn2 = [
            {'rst': 123, 'eee': 414, 'DEF': 256, 'test': 987, 'Finis': 999},
            {'rst': 124, 'eee': 424, 'DEF': 356, 'test': 887, 'Finis': 999},
            ]
        tableExpect = [
            {'st': 123, 'nd': 414, 'rd': 256, 'th': 987, 'finis': 999},
            {'st': 124, 'nd': 424, 'rd': 356, 'th': 887, 'finis': 999},
            ]
        conversion = (('st', 'abc,rst'),
                      ('nd', 'eee'),
                      ('rd', 'def'),
                      ('th', 'test'),
                      )
        gp = mock.GpDispatch(default_table=tableIn1)
        tableOut = get_table(gp, "nomeACaso", conversion=conversion)
        self.assertEqual(tableOut, tableExpect)
        gp = mock.GpDispatch(default_table=tableIn2)
        tableOut = get_table(gp, "nomeACaso", conversion=conversion)
        self.assertEqual(tableOut, tableExpect)
        pass

    def test31gettable(self):
        "get table with field name translation - discard fields"
        tableIn1 = [
            {'Abc': 123, 'eee': 414, 'DEF': 256, 'test': 987, 'Finis': 999},
            {'Abc': 124, 'eee': 424, 'DEF': 356, 'test': 887, 'Finis': 999},
            ]
        tableExpect = [
            {'st': 123, 'th': 987, 'finis': 999},
            {'st': 124, 'th': 887, 'finis': 999},
            ]
        conversion = (('st', 'abc'),
                      ('-', 'eee,def'),
                      ('th', 'test'),
                      )
        gp = mock.GpDispatch(default_table=tableIn1)
        tableOut = get_table(gp, "nomeACaso", conversion=conversion)
        self.assertEqual(tableOut, tableExpect)
        pass

    def test32gettable(self):
        "get table with field name translation - discard fields - on individual lines"
        tableIn1 = [
            {'Abc': 123, 'eee': 414, 'DEF': 256, 'test': 987, 'Finis': 999},
            {'Abc': 124, 'eee': 424, 'DEF': 356, 'test': 887, 'Finis': 999},
            ]
        tableExpect = [
            {'st': 123, 'th': 987, 'finis': 999},
            {'st': 124, 'th': 887, 'finis': 999},
            ]
        conversion = (('st', 'abc'),
                      ('-', 'eee'),
                      ('-', 'def'),
                      ('th', 'test'),
                      )
        gp = mock.GpDispatch(default_table=tableIn1)
        tableOut = get_table(gp, "nomeACaso", conversion=conversion)
        self.assertEqual(tableOut, tableExpect)
        pass

    def test33gettable(self):
        "get table with field name translation - using defaults verbatim"
        tableIn1 = [
            {'Abc': 123, 'eee': 414, 'DEF': 256, 'test': 987, 'Finis': 999},
            {'Abc': 124, 'eee': 424, 'DEF': 356, 'test': 887, 'Finis': 999},
            ]
        tableExpect = [
            {'st': 123, 'th': 987, 'qw': "some text", "num": 123.0, },
            {'st': 124, 'th': 887, 'qw': "some text", "num": 123.0, },
            ]
        conversion = (('st', 'abc'),
                      ('-', 'eee,def,finis'),
                      ('th', 'test'),
                      )
        defaults = (('st', 'abc'),
                    ('qw', 'some text'),
                    ('num', 123.0),
                    ('th', 'test'),
                    )
        gp = mock.GpDispatch(default_table=tableIn1)
        tableOut = get_table(gp, "nomeACaso", conversion=conversion, defaults=defaults)
        self.assertEqual(tableOut, tableExpect)
        pass

    def test34gettable(self):
        "get table with field name translation - using defaults and evaluating them"
        tableIn1 = [
            {'Abc': 123, 'eee': 414, 'DEF': 256, 'test': 987, 'Finis': 999},
            {'Abc': 124, 'eee': 424, 'DEF': 356, 'test': 887, 'Finis': 999},
            ]
        tableExpect = [
            {'st': 123, 'th': 987, 'qw': "some text", "num": 123.0, },
            {'st': 124, 'th': 887, 'qw': "some text", "num": 123.0, },
            ]
        conversion = (('st', 'abc'),
                      ('-', 'eee,def,finis'),
                      ('th', 'test'),
                      )
        defaults = (('st', 'abc'),
                    ('qw', "'some text'"),
                    ('num', '123.0'),
                    ('th', 'test'),
                    )
        gp = mock.GpDispatch(default_table=tableIn1)
        tableOut = get_table(gp, "nomeACaso", conversion=conversion, defaults=defaults, evaluate=True)
        self.assertEqual(tableOut, tableExpect)
        pass

    def test40gettable(self):
        "get table with field name translation - mixed case"
        tableIn = [
            {'Abc': 123, 'eee': 414, 'DEF': 256, 'test': 987, 'Finis': 999},
            {'Abc': 124, 'eee': 424, 'DEF': 356, 'test': 887, 'Finis': 999},
            {'Abc': 125, 'eee': 434, 'DEF': 456, 'test': 787, 'Finis': 999},
            {'Abc': 126, 'eee': 444, 'DEF': 556, 'test': 687, 'Finis': 999},
            {'Abc': 127, 'eee': 454, 'DEF': 656, 'test': 587, 'Finis': 999},
            {'Abc': 128, 'eee': 464, 'DEF': 756, 'test': 487, 'Finis': 999},
            {'Abc': 129, 'eee': 474, 'DEF': 856, 'test': 387, 'Finis': 999},
            ]
        tableExpect = [
            {'st': 123, 'nd': 414, 'rd': 256, 'th': 987, 'finis': 999},
            {'st': 124, 'nd': 424, 'rd': 356, 'th': 887, 'finis': 999},
            {'st': 125, 'nd': 434, 'rd': 456, 'th': 787, 'finis': 999},
            {'st': 126, 'nd': 444, 'rd': 556, 'th': 687, 'finis': 999},
            {'st': 127, 'nd': 454, 'rd': 656, 'th': 587, 'finis': 999},
            {'st': 128, 'nd': 464, 'rd': 756, 'th': 487, 'finis': 999},
            {'st': 129, 'nd': 474, 'rd': 856, 'th': 387, 'finis': 999},
            ]
        conversion = (('ST', 'aBc'),
                      ('Nd', 'eeE'),
                      ('rd', 'Def'),
                      ('th', 'TEST'),
                      )
        gp = mock.GpDispatch(default_table=tableIn)
        # check that our library converts to lower case
        tableOut = get_table(gp, "nomeACaso", conversion=conversion)
        self.assertEqual(tableOut, tableExpect)
        pass

    def test41gettable(self):
        "get table with value translation - through translation dictionaries"
        tableIn = [
            {'st': 123, 'nd': 133},
            {'st': 124, 'nd': 262},
            {'st': 125, 'nd': 384},
            ]
        tableExpect = [
            {'st': 123, 'nd': 414, },
            {'st': 124, 'nd': 424, },
            {'st': 125, 'nd': 434, },
            ]
        dictionaries = {'nd': {'414': '133', '424': '262', '434': '384'},
                        }
        gp = mock.GpDispatch(default_table=tableIn)
        # check that our library converts to lower case
        tableOut = get_table(gp, "nomeACaso", dictionaries=dictionaries)
        self.assertEqual(tableOut, tableExpect)
        pass

    def test42gettable(self):
        "get table with value translation - through translation dictionaries"
        tableIn = [
            {'st': 123, 'nd': 'rechthoek'},
            {'st': 124, 'nd': 'ovaal'},
            {'st': 125, 'nd': 'RECHTHOEK'},
            ]
        tableExpect = [
            {'st': 123, 'nd': 1, },
            {'st': 124, 'nd': 2, },
            {'st': 125, 'nd': 1, },
            ]
        dictionaries = {'nd': {'1': 'rechthoek', '2': 'ovaal'},
                        }
        gp = mock.GpDispatch(default_table=tableIn)
        # check that our library converts to lower case
        tableOut = get_table(gp, "nomeACaso", dictionaries=dictionaries)
        self.assertEqual(tableOut, tableExpect)
        pass

    def test8dictjoin(self):
        "get with multiple valued translation and join on that key"
        dl1 = [{'abc':1, 'qwe':2}, {'abc':4, 'qwe':3}]
        dl2 = [{'abg':1, 'asd':2}, {'abg':4, 'asd':9}]
        conversion = (('st', 'abc,abg'),
                      ('nd', 'qwe'),
                      ('rd', 'asd'),
                      )
        gp = mock.GpDispatch(default_table=dl1)
        tb1 = get_table(gp, "nomeACaso", conversion=conversion)
        gp = mock.GpDispatch(default_table=dl2)
        tb2 = get_table(gp, "nomeACaso", conversion=conversion)
        key1 = 'st'
        result = [{'st':1, 'nd':2, 'rd':2}, {'st':4, 'nd':3, 'rd':9}]
        self.assertEqual(join_dicts(tb1, tb2, key1), result)

    def test9_gettable(self):
        "get with field name translation containing table - full"
        tableIn = [{}, ]
        for i in range(11):
            tableIn[0]["lv_%i" % i] = i
        conversion = {'levels': '[lv_%i][0,10]', }
        expectContains = {'levels': dict([(i, i) for i in range(11)])}
        gp = mock.GpDispatch(default_table=tableIn)
        # check that our library converts to lower case
        tableOut = get_table(gp, "nomeACaso", conversion=conversion)
        tableOut[0]['levels']
        self.assertEqual(expectContains['levels'], tableOut[0]['levels'])
        pass

    def testa_gettable(self):
        "get with field name translation containing table - with step"
        tableIn = [{}, ]
        for i in range(5):
            tableIn[0]["lv_%i" % (i * 25)] = i
        conversion = {'levels': '[lv_%i][0,100,25]', }
        tableExpect = [
            {'levels': dict([(i * 25, i) for i in range(5)])},
            ]
        gp = mock.GpDispatch(default_table=tableIn)
        # check that our library converts to lower case
        tableOut = get_table(gp, "nomeACaso", conversion=conversion)
        self.assertEqual(tableOut[0]['levels'], tableExpect[0]['levels'])
        pass

    def testb_gettable(self):
        "get with field name translation containing table - with holes"
        tableIn = [{}, ]
        for i in range(11):
            if i in [2, 3, 5, 7]:
                continue
            tableIn[0]["lv_%i" % i] = i
        conversion = {'levels': '[lv_%i][0,10]', }
        tableExpect = [
            {'levels': dict([(i, i) for i in range(11) if i not in [2, 3, 5, 7]])},
            ]
        gp = mock.GpDispatch(default_table=tableIn)
        # check that our library converts to lower case
        tableOut = get_table(gp, "nomeACaso", conversion=conversion)
        self.assertEqual(tableOut[0]['levels'], tableExpect[0]['levels'])
        pass

    def testc_gettable(self):
        "get with field name translation containing table - with step and holes"
        tableIn = [{}, ]
        for i in range(5):
            if i == 2:
                continue
            tableIn[0]["lv_%i" % (i * 25)] = i
        conversion = {'levels': '[lv_%i][0,100,25]', }
        tableExpect = [
            {'levels': dict([(i * 25, i) for i in range(5) if i != 2])},
            ]
        gp = mock.GpDispatch(default_table=tableIn)
        # check that our library converts to lower case
        tableOut = get_table(gp, "nomeACaso", conversion=conversion)
        self.assertEqual(tableOut[0]['levels'], tableExpect[0]['levels'])
        pass

    def testd_gettable(self):
        "get table with name clash in translation"
        tableIn = [
            {'Abc': 123, 'eee': 414, },
            {'Abc': 124, 'eee': 424, },
            {'Abc': 125, 'eee': 434, },
            {'Abc': 126, 'eee': 444, },
            {'Abc': 127, 'eee': 454, },
            {'Abc': 128, 'eee': 464, },
            {'Abc': 129, 'eee': 474, },
            ]
        conversion = (('ST', 'aBc'),
                      ('extra', 'abc'),
                      ('Nd', 'eeE'),
                      )
        tableExpect = [
            {'st': 123, 'extra': 123, 'nd': 414, },
            {'st': 124, 'extra': 124, 'nd': 424, },
            {'st': 125, 'extra': 125, 'nd': 434, },
            {'st': 126, 'extra': 126, 'nd': 444, },
            {'st': 127, 'extra': 127, 'nd': 454, },
            {'st': 128, 'extra': 128, 'nd': 464, },
            {'st': 129, 'extra': 129, 'nd': 474, },
            ]
        gp = mock.GpDispatch(default_table=tableIn)
        tableOut = get_table(gp, "nomeACaso", conversion=conversion)
        self.assertEqual(tableOut, tableExpect)
        pass


class DictionaryReversalTest(unittest.TestCase):
    def test0_reverse(self):
        "reversing a normal dictionary"
        d = {1: 2, 2: 3, 3: 4}
        r = reverse_dict(d)
        e = {2: [1], 3: [2], 4: [3]}
        self.assertEqual(e, r)

    def test1_reverse(self):
        "reversing a dictionary with string keys"
        d = {'1': 2, '2': 3, '3': 4}
        r = reverse_dict(d)
        e = {2: ['1'], 3: ['2'], 4: ['3']}
        self.assertEqual(e, r)

    def test2_reverse(self):
        "reversing a dictionary with string values"
        d = {1: '2', 2: '3', 3: '4'}
        r = reverse_dict(d)
        e = {'2': [1], '3': [2], '4': [3]}
        self.assertEqual(e, r)

    def test3_reverse(self):
        "reversing a dictionary with multiple valued string values"
        d = {1: '2', 2: '3', 3: '4,5,6'}
        r = reverse_dict(d)
        e = {'2': [1], '3': [2], '4': [3], '5': [3], '6': [3]}
        self.assertEqual(e, r)

    def test4_reverse(self):
        "reversing a normal dictionary in list format"
        d = [(1, 2), (2, 3), (3, 4)]
        r = reverse_dict(d)
        e = {2: [1], 3: [2], 4: [3]}
        self.assertEqual(e, r)

    def test5_reverse(self):
        "reversing a dictionary in list format with multiple valued string values"
        d = [(1, '2'), (2, '3'), (3, '4,5,6')]
        r = reverse_dict(d)
        e = {'2': [1], '3': [2], '4': [3], '5': [3], '6': [3]}
        self.assertEqual(e, r)

    def test6_reverse(self):
        "reversing a dictionary in list format with multiply defined forward keys"
        d = [(1, '2'), (1, '3'), (1, '4,5,6')]
        r = reverse_dict(d)
        e = {'2': [1], '3': [1], '4': [1], '5': [1], '6': [1]}
        self.assertEqual(e, r)

    def test7_reverse(self):
        "reversing a dictionary with multiply defined backwards keys"
        d = [(1, '2'), (2, '1'), (3, '1')]
        r = reverse_dict(dict(d))
        e = {'1': [2, 3], '2': [1]}
        self.assertEqual(e, r)

    def test8_reverse(self):
        "reversing a dictionary with multiply defined forward and backwards keys"
        d = [(1, '2,1'), (2, '3,1'), (3, '4,5,1')]
        r = reverse_dict(dict(d))
        e = {'1': [1, 2, 3], '2': [1], '3': [2], '4': [3], '5': [3], }
        self.assertEqual(e, r)


class NotAValueTest(unittest.TestCase):
    def test0not_a_value(self):
        "second parameter is a list"
        d = {1: 1, 2: 2, 3: 3}
        replace_notavalue(d, [1, 3])
        self.assertEqual(d[1], None)
        self.assertEqual(d[2], 2)
        self.assertEqual(d[3], None)

    def test1not_a_value(self):
        "second parameter is a dictionary"
        d = {1: 1, 2: 2, 3: 3}
        replace_notavalue(d, {'label': 3})
        self.assertEqual(d[1], 1)
        self.assertEqual(d[2], 2)
        self.assertEqual(d[3], None)

    def test2not_a_value(self):
        "second parameter is a single value"
        d = {1: 1, 2: 2, 3: 3}
        replace_notavalue(d, 3)
        self.assertEqual(d[1], 1)
        self.assertEqual(d[2], 2)
        self.assertEqual(d[3], None)

    def test3not_a_value(self):
        "returns the modified dictionary"
        d = {1: 1, 2: 2, 3: 3}
        r = replace_notavalue(d, 3)
        self.assertEqual(d, r)


class GpLoggingHandler(unittest.TestCase):
    "also have a look at http://code.env.duke.edu/projects/mget/browser/MGET/Trunk/PythonPackage/src/GeoEco/Logging.py?rev=15"

    def test01(self):
        "can create the handler"
        gp = mock.GpDispatch()
        h = GpHandler(geoprocessor=gp)
        self.assertTrue(h != None)

    def test02(self):
        "can set the level of the handler"
        gp = mock.GpDispatch()
        h = GpHandler(geoprocessor=gp)
        h.setLevel(logging.WARNING)
        self.assertEqual(h.level, logging.WARNING)

    def test03(self):
        "can attach the handler to the root logger"
        gp = mock.GpDispatch()
        h = GpHandler(level=logging.ERROR, geoprocessor=gp)
        rootlog = logging.getLogger('')
        rootlog.addHandler(h)
        pass

    def test04(self):
        "handler ignores a logging message of lower log_level"
        gp = mock.GpDispatch()
        h = GpHandler(level=logging.ERROR, geoprocessor=gp)
        rootlog = logging.getLogger('')
        loclog = logging.getLogger('nens.gp.test')
        rootlog.addHandler(h)
        loclog.debug('test')
        self.assertEqual(gp.receivedMessages, [])

    def test05(self):
        "handler at loglevel DEBUG sends ERROR to GP.AddError"
        gp = mock.GpDispatch()
        h = GpHandler(level=logging.DEBUG, geoprocessor=gp, format="%(message)s")
        rootlog = logging.getLogger('')
        loclog = logging.getLogger('nens.gp.test')
        rootlog.addHandler(h)
        loclog.error('test')
        self.assertEqual(gp.receivedMessages, [(logging.ERROR, 'test')])

    def test06(self):
        "handler at loglevel DEBUG sends WARNING to GP.AddWarning"
        gp = mock.GpDispatch()
        h = GpHandler(level=logging.DEBUG, geoprocessor=gp, format="%(message)s")
        rootlog = logging.getLogger('')
        loclog = logging.getLogger('nens.gp.test')
        rootlog.addHandler(h)
        loclog.warning('test')
        self.assertEqual(gp.receivedMessages, [(logging.WARNING, 'test')])
        pass

    def test07(self):
        "handler at loglevel DEBUG sends INFO to GP.AddMessage"
        gp = mock.GpDispatch()
        h = GpHandler(level=logging.DEBUG, geoprocessor=gp, format="%(message)s")
        rootlog = logging.getLogger('')
        loclog = logging.getLogger('nens.gp.test')
        rootlog.addHandler(h)
        loclog.setLevel(logging.INFO)
        loclog.info('test')
        self.assertEqual(gp.receivedMessages, [(logging.INFO, 'test')])
        pass

    def test08(self):
        "handler at loglevel DEBUG sends DEBUG to GP.AddMessage"
        gp = mock.GpDispatch()
        h = GpHandler(level=logging.DEBUG, geoprocessor=gp, format="%(message)s")
        rootlog = logging.getLogger('')
        loclog = logging.getLogger('nens.gp.test')
        rootlog.addHandler(h)
        loclog.setLevel(logging.DEBUG)
        loclog.debug('test')
        self.assertEqual(gp.receivedMessages, [(logging.INFO, 'test')])
        pass

    def test09(self):
        "handler has INFO default loglevel"
        gp = mock.GpDispatch()
        h = GpHandler(geoprocessor=gp, format="%(message)s")
        rootlog = logging.getLogger('')
        loclog = logging.getLogger('nens.gp.test')
        rootlog.addHandler(h)
        loclog.setLevel(logging.DEBUG)
        loclog.debug('test-ignored')
        loclog.info('test')
        self.assertEqual(gp.receivedMessages, [(logging.INFO, 'test')])
        pass


class AddingObjectsToATable(unittest.TestCase):
    root = [
        {'id': 1, 'nm': 414, },
        {'id': 2, 'nm': 414, },
        {'id': 3, 'nm': 414, },
        ]
    branches = [
        {'id': 1, 'x': 123, 'y': 414, 'z': 256, },
        {'id': 1, 'x': 124, 'y': 424, 'z': 356, },
        {'id': 1, 'x': 125, 'y': 434, 'z': 456, },
        {'id': 1, 'x': 126, 'y': 444, 'z': 556, },
        {'id': 2, 'x': 127, 'y': 454, 'z': 656, },
        {'id': 2, 'x': 128, 'y': 464, 'z': 756, },
        {'id': 2, 'x': 129, 'y': 474, 'z': 856, },
        ]
    branches_2 = [
        {'id': 1, 'x': 24, 'y': 42, 'z': 3, },
        {'id': 1, 'x': 23, 'y': 41, 'z': 2, },
        {'id': 1, 'x': 25, 'y': 43, 'z': 4, },
        {'id': 2, 'x': 28, 'y': 46, 'z': 7, },
        {'id': 1, 'x': 26, 'y': 44, 'z': 5, },
        {'id': 2, 'x': 27, 'y': 45, 'z': 6, },
        {'id': 2, 'x': 29, 'y': 47, 'z': 8, },
        ]

    def test01(self):
        "a new object contains no tables"
        gp = mock.GpDispatch(default_table=self.root)
        root_dict = get_table(gp, "nomeACaso")
        self.assertTrue(root_dict != None)

        pass

    def test20(self):
        "adding objects to an object (unnamed)"
        gp = mock.GpDispatch(default_table=self.root)
        root_dict = get_table(gp, "nomeACaso")
        gp = mock.GpDispatch(default_table=self.branches)
        join_on_foreign_key(gp, root_dict, key=None, fields=['x', 'y', 'z'], table="nomeACaso", pk='id')
        self.assertEqual(root_dict[0].get(None), [[123, 414, 256, ], [124, 424, 356, ], [125, 434, 456, ], [126, 444, 556, ], ])
        self.assertEqual(root_dict[1].get(None), [[127, 454, 656, ], [128, 464, 756, ], [129, 474, 856, ], ])

    def test21(self):
        "adding objects to an object (named)"
        gp = mock.GpDispatch(default_table=self.root)
        root_dict = get_table(gp, "nomeACaso")
        gp = mock.GpDispatch(default_table=self.branches)
        join_on_foreign_key(gp, root_dict, key='uno', fields=['x', 'y', 'z'], table="nomeACaso", pk='id')
        gp = mock.GpDispatch(default_table=self.branches_2)
        join_on_foreign_key(gp, root_dict, key='due', fields=['x', 'y', 'z'], table="nomeACaso", pk='id')
        self.assertEqual(root_dict[0].get('uno'), [[123, 414, 256], [124, 424, 356], [125, 434, 456], [126, 444, 556]])
        self.assertEqual(root_dict[1].get('uno'), [[127, 454, 656, ], [128, 464, 756, ], [129, 474, 856, ], ])
        self.assertEqual(root_dict[0].get('due'), [[24, 42, 3], [23, 41, 2], [25, 43, 4], [26, 44, 5]])
        self.assertEqual(root_dict[1].get('due'), [[28, 46, 7], [27, 45, 6], [29, 47, 8]])

    def test31(self):
        "adding objects to an object (named), sorted by value"
        gp = mock.GpDispatch(default_table=self.root)
        root_dict = get_table(gp, "nomeACaso")
        gp = mock.GpDispatch(default_table=self.branches)
        join_on_foreign_key(gp, root_dict, key='uno', fields=['x', 'y', 'z'], table="nomeACaso", pk='id', sort_on=0)
        gp = mock.GpDispatch(default_table=self.branches_2)
        join_on_foreign_key(gp, root_dict, key='due', fields=['x', 'y', 'z'], table="nomeACaso", pk='id', sort_on=0)
        self.assertEqual(root_dict[0].get('uno'), [[123, 414, 256], [124, 424, 356], [125, 434, 456], [126, 444, 556]])
        self.assertEqual(root_dict[1].get('uno'), [[127, 454, 656, ], [128, 464, 756, ], [129, 474, 856, ], ])
        self.assertEqual(root_dict[0].get('due'), [[23, 41, 2], [24, 42, 3], [25, 43, 4], [26, 44, 5]])
        self.assertEqual(root_dict[1].get('due'), [[27, 45, 6], [28, 46, 7], [29, 47, 8]])

    def test30(self):
        "adding objects to an object (unnamed) - and finding empty list"
        gp = mock.GpDispatch(default_table=self.root)
        root_dict = get_table(gp, "nomeACaso")
        gp = mock.GpDispatch(default_table=self.branches)
        join_on_foreign_key(gp, root_dict, key=None, fields=['x', 'y', 'z'], table="nomeACaso", pk='id')
        self.assertEqual(root_dict[2].get(None), [])


class RecognizingNullValues(unittest.TestCase):
    branches = [
        {'id': 123, 'x': 123, 'y': 414, 'z': 256, },
        {'id': 123, 'x': None, 'y': 424, 'z': 356, },
        {'id': 124, 'x': 125, 'y':-9999, 'z': 456, },
        {'id': 124, 'x': 126, 'y': 444, 'z':-9999.9999, },
        ]
    tableIn = [
        {'id': 123, 'eee':-9999, 'def': 256, 'test': 987, },
        {'id': 124, 'eee':-9999, 'def':-9999.9999, 'test': 887, },
        {'id': 125, 'eee': 434, 'def': 456, 'test': None, },
        ]
    tableExpect = [
        {'id': 123, 'eee': None, 'def': 256, 'test': 987, },
        {'id': 124, 'eee': None, 'def': None, 'test': 887, },
        {'id': 125, 'eee': 434, 'def': 456, 'test': None, },
        ]
    tableExpectJoined = [
        {'id': 123, 'eee': None, 'def': 256, 'test': 987, 'xyz': [[123, 414, 256, ], [None, 424, 356]], },
        {'id': 124, 'eee': None, 'def': None, 'test': 887, 'xyz': [[125, None, 456], [126, 444, None]], },
        {'id': 125, 'eee': 434, 'def': 456, 'test': None, 'xyz': [], },
        ]
    tableExpectJoinedReplaced = [
        {'id': 123, 'eee': None, 'def': 256, 'test': 987, 'xyz': [[123, 414, 256, ], [0, 424, 356]], },
        {'id': 124, 'eee': None, 'def': None, 'test': 887, 'xyz': [[125, 0, 456], [126, 444, 0]], },
        {'id': 125, 'eee': 434, 'def': 456, 'test': None, 'xyz': [], },
        ]

    def test00(self):
        "get table translating null values."
        gp = mock.GpDispatch(default_table=self.tableIn)
        # check that our library converts special values to None
        tableOut = get_table(gp, "nomeACaso", nonevalues=[-9999, -9999.9999])
        self.assertEqual(tableOut, self.tableExpect)
        pass

    def test10(self):
        "recognizing null values on joined tables."
        gp = mock.GpDispatch(default_table=self.tableIn)
        # check that our library converts special values to None
        tableOut = get_table(gp, "nomeACaso", nonevalues=[-9999, -9999.9999])
        gp = mock.GpDispatch(default_table=self.branches)
        join_on_foreign_key(gp, tableOut, key='xyz', fields=['x', 'y', 'z', ], table="nome_a_caso", pk='id', fk='id', nonevalues=[-9999, -9999.9999])
        self.assertEqual(tableOut, self.tableExpectJoined)
        pass

    def test20(self):
        "replace null values with defaults on joined tables."
        gp = mock.GpDispatch(default_table=self.tableIn)
        # check that our library converts special values to None
        tableOut = get_table(gp, "nomeACaso", nonevalues=[-9999, -9999.9999])
        gp = mock.GpDispatch(default_table=self.branches)
        join_on_foreign_key(gp, tableOut, key='xyz', fields=['x', 'y', 'z', ], table="nome_a_caso", pk='id', fk='id', nonevalues=[-9999, -9999.9999], defaults={'x': 0, 'y': 0, 'z': 0})
        self.assertEqual(tableOut, self.tableExpectJoinedReplaced)
        pass


class RangeChecking(unittest.TestCase):
    tableIn = [
        {'abc': 0, 'eee': 5, 'def': '12345678', },
        {'abc': 3, 'eee': 4, 'def': '256', },
        {'abc': 4, 'eee': 2, 'def': '356', },
        {'abc': 6, 'eee':-4, 'def': None, },
        {'abc': 8, 'eee': 999, 'def': '756', },
        {'abc': 999, 'eee': 7, 'def': '856', },
        ]
    tableIn2 = [
        {'abc': 0, 'eee': '2907', 'bo': 'True', },
        {'abc': 3, 'eee': '', 'bo': 'False', },
        {'abc': 4, 'eee': '0101', 'bo': 'a', },
        {'abc': 6, 'eee': '1213', 'bo': 'b', },
        {'abc': 8, 'eee': '1312', 'bo': '1', },
        {'abc': 9, 'eee': '3212', 'bo': 'k', },
        ]
    tableExpectFilter = [
        {'abc': 3, 'eee': 4, 'def': '256', },
        {'abc': 4, 'eee': 2, 'def': '356', },
        {'abc': 8, 'eee': 999, 'def': '756', },
        {'abc': 999, 'eee': 7, 'def': '856', },
        ]
    tableExpectSubstitute = [
        {'abc': 3, 'eee': 4, 'def': '256', },
        {'abc': 4, 'eee': 2, 'def': '356', },
        {'abc': 6, 'eee':-4, 'def': None, },
        {'abc': 0, 'eee': 5, 'def': '12345678', },
        {'abc': 8, 'eee': None, 'def': '756', },
        {'abc': None, 'eee': 7, 'def': '856', },
        ]
    tableExpectSubstituteFilter = [
        {'abc': 3, 'eee': 4, 'def': '256', },
        {'abc': 4, 'eee': 2, 'def': '356', },
        ]
    tableExpectSubstituteFilterOptional = [
        {'abc': 3, 'eee': 4, 'def': '256', },
        {'abc': 4, 'eee': 2, 'def': '356', },
        {'abc': 8, 'eee': None, 'def': '756', },
        {'abc': None, 'eee': 7, 'def': '856', },
        ]

    def test10(self):
        "range splitter"

        for s, l in [("NonNegative W[-,100]", (False, ['NonNegative', 'W[-,100]'])),
                     ("NonNegative W[-, 100]", (False, ['NonNegative', 'W[-, 100]'])),
                     ("Integer NonNegative W[-, 100]", (False, ['Integer', 'NonNegative', 'W[-, 100]'])),
                     ("Integer NonNegative [-, 100]", (False, ['Integer', 'NonNegative', '[-, 100]'])),
                     ("W[-, 100]", (False, ['W[-, 100]'])),
                     ("[-, 100]", (False, ['[-, 100]'])),
                     ("string(100)", (False, ['string(100)'])),
                     ("(Integer NonNegative)", (True, ['Integer', 'NonNegative', ])),
                     ("(Integer [-50,50] [wp,-])", (True, ['Integer', '[-50,50]', '[wp,-]', ])),
                     ("(Integer [-50,50]    [wp,-])", (True, ['Integer', '[-50,50]', '[wp,-]', ])),
                     ]:
            self.assertEqual(split_constraints(s), l)

    def test12(self):
        "range splitter does not crash on empty input"

        for s in [None, '', ]:
            split_constraints(s)

    def test130(self):
        "check integer against valid range gives True"
        obj = {'a': 12}
        constraints = '[10,20]'
        self.assertEqual(check_constraints(obj, 'a', constraints), True)

    def test132(self):
        "check integer outside weak range gives True"
        obj = {'a': 22}
        constraints = 'w[10,20]'
        self.assertEqual(check_constraints(obj, 'a', constraints), True)

    def test134(self):
        "check integer outside range gives False"
        obj = {'a': 22}
        constraints = '[10,20]'
        self.assertEqual(check_constraints(obj, 'a', constraints), False)

    def test136(self):
        "check None against range gives False"
        obj = {'a': None}
        constraints = '[10,20]'
        self.assertEqual(check_constraints(obj, 'a', constraints), False)

    def test138(self):
        "check None against optional range gives True"
        obj = {'a': None}
        constraints = '([10,20])'
        self.assertEqual(check_constraints(obj, 'a', constraints), True)

    def test140(self):
        "check None against positive gives False"
        obj = {'a': None}
        constraints = 'positive'
        self.assertEqual(check_constraints(obj, 'a', constraints), False)

    def test142(self):
        "check None against optional positive gives True"
        obj = {'a': None}
        constraints = '(positive)'
        self.assertEqual(check_constraints(obj, 'a', constraints), True)

    def test150(self):
        "check moving interval - false"
        obj = {'a': 1, 'b': 2}
        constraints = '[b,-]'
        self.assertEqual(check_constraints(obj, 'a', constraints), False)

    def test151(self):
        "check moving interval - true"
        obj = {'a': 3, 'b': 2}
        constraints = '[b,-]'
        self.assertEqual(check_constraints(obj, 'a', constraints), True)

    def test152(self):
        "check moving interval - both cases"
        constraints = 'positive [eee,-]'
        obj = {'eee': 4, 'abc': 3, 'def': '256'}
        self.assertEqual(check_constraints(obj, 'abc', constraints), False)
        obj = {'eee': 2, 'abc': 4, 'def': '356'}
        self.assertEqual(check_constraints(obj, 'abc', constraints), True)

    def test155(self):
        "check moving interval and fixed interval - both cases"
        constraints = 'positive [-50,50] [eee,-]'
        obj = {'eee': 4, 'abc': 3, 'def': '256'}
        self.assertEqual(check_constraints(obj, 'abc', constraints), False)
        obj = {'eee': 2, 'abc': 4, 'def': '356'}
        self.assertEqual(check_constraints(obj, 'abc', constraints), True)

    def test157(self):
        "check moving interval and fixed interval - both cases"
        constraints = 'positive [-50,50] [-,abc]'
        obj = {'eee': 4, 'abc': 3, 'def': '256'}
        self.assertEqual(check_constraints(obj, 'eee', constraints), False)
        obj = {'eee': 2, 'abc': 4, 'def': '356'}
        self.assertEqual(check_constraints(obj, 'eee', constraints), True)

    def test20(self):
        "gp_as_dict can check ranges"

        ranges = {'abc': 'positive',
                  'eee': 'nonnegative',
                  }
        count_none = 0
        for obj_in in self.tableIn:
            row_in = mock.GpDispatch.Row(obj_in)
            obj_out = gp_as_dict(['abc', 'def', 'eee'], row_in, ranges=ranges)
            if obj_out is None:
                count_none += 1
                continue
            self.assertEqual(obj_out, obj_in)
        self.assertEqual(count_none, 2)

    def test30(self):
        "numerical range checking as filters"

        ranges = {'abc': 'positive',
                  'eee': 'nonnegative',
                  }

        gp = mock.GpDispatch(default_table=self.tableIn)
        tableOut = get_table(gp, "nomeACaso",
                             ranges=ranges)
        self.assertEqual(tableOut, self.tableExpectFilter)
        pass

    def test35(self):
        "string range checking as filters"

        ranges = {'def': 'string(4)',
                  }
        gp = mock.GpDispatch(default_table=self.tableIn)
        tableOut = get_table(gp, "nomeACaso",
                             ranges=ranges)
        self.assertEqual(tableOut, self.tableExpectFilter)
        pass

    def test360(self):
        """field holds a value that looks like a boolean
        """
        gp = mock.GpDispatch(default_table=self.tableIn2)
        tableOut = get_table(gp, "nomeACaso", ranges={'bo': 'boolean'})
        self.assertEqual([i['abc'] for i in tableOut], [0, 3, 8])

    def test361(self):
        """field holds an integer"""

        gp = mock.GpDispatch(default_table=self.tableIn2)
        tableOut = get_table(gp, "nomeACaso", ranges={'bo': 'integer'})
        self.assertEqual([i['abc'] for i in tableOut], [8])

    def test362(self):
        """field holds a DDMM - Integer holding a day of the year."""
        gp = mock.GpDispatch(default_table=self.tableIn2)
        tableOut = get_table(gp, "nomeACaso", ranges={'eee': 'DDMM'})
        self.assertEqual([i['abc'] for i in tableOut], [0, 4, 8])

    def test363(self):
        """field holds a MMDD - Integer holding a day of the year."""
        gp = mock.GpDispatch(default_table=self.tableIn2)
        tableOut = get_table(gp, "nomeACaso", ranges={'eee': 'MMDD'})
        self.assertEqual([i['abc'] for i in tableOut], [4, 6])

    def test367(self):
        """field holds an unrecognized condition, you get a True"""
        gp = mock.GpDispatch(default_table=self.tableIn2)
        tableOut = get_table(gp, "nomeACaso", ranges={'eee': 'MMxDD'})
        self.assertEqual(len(tableOut), 6)

    def test40(self):
        "special values are recognized as None before filtering - and are filtered out"

        ranges = {'abc': 'positive [-,100]',
                  'eee': 'positive [-,100]',
                  'def': 'string(4)',
                  }
        gp = mock.GpDispatch(default_table=self.tableIn)
        tableOut = get_table(gp, "nomeACaso",
                             ranges=ranges,
                             nonevalues=[999])
        self.assertEqual(tableOut, self.tableExpectSubstituteFilter)
        pass

    def test42(self):
        "special values are recognized as None before filtering - and are accepted by optional filter"

        ranges = {'abc': '(positive [-,100])',
                  'eee': '(positive [-,100])',
                  'def': '(string(4))',
                  }
        gp = mock.GpDispatch(default_table=self.tableIn)
        tableOut = get_table(gp, "nomeACaso",
                             ranges=ranges,
                             nonevalues=[999])
        self.assertEqual(tableOut, self.tableExpectSubstituteFilterOptional)
        pass

    def test500(self):
        "filtering on ranges that refer to other fields"

        ranges = {'wp': '[-100,zp]',
                  'zp': '[wp,100]',
                  }
        tableIn = [
            {'wp': 3, 'zp': 4, },
            {'wp': 4, 'zp': 2, },
            ]
        tableExpect = [
            {'wp': 3, 'zp': 4, },
            ]
        gp = mock.GpDispatch(default_table=tableIn)
        tableOut = get_table(gp, "nomeACaso",
                             ranges=ranges,
                             )
        self.assertEqual(tableOut, tableExpect)
        pass


class NamedInConversion(unittest.TestCase):
    def test00(self):
        "named_in_conversion can cope with None"
        self.assertEqual(named_in_conversion(None), {})

    def test01(self):
        "named_in_conversion finds plain named fields"
        conversion = {'st': 'abc',
                      'th': 'test',
                      }
        self.assertEqual(named_in_conversion(conversion), {'abc': None, 'test': None, })

    def test02(self):
        "named_in_conversion finds array fields"
        conversion = {'levels': '[lv_%i][0,10]', }
        self.assertEqual(named_in_conversion(conversion), {'lv_0': None, 'lv_1': None, 'lv_2': None,
                                                           'lv_3': None, 'lv_4': None, 'lv_5': None,
                                                           'lv_6': None, 'lv_7': None, 'lv_8': None,
                                                           'lv_9': None, 'lv_10': None, })

    def test03(self):
        "named_in_conversion finds array fields with step"
        conversion = {'levels': '[lv_%i][0,100,25]', }
        self.assertEqual(named_in_conversion(conversion), {'lv_0': None, 'lv_25': None, 'lv_50': None, 'lv_75': None, 'lv_100': None, })

    def test04(self):
        "named_in_conversion finds multiple named fields - list"
        conversion = (('st', 'abc'),
                      ('-', 'eee,def,finis'),
                      ('th', 'test'),
                      )
        self.assertEqual(named_in_conversion(conversion), {'abc': None, 'eee': None, 'def': None, 'finis': None, 'test': None, })

    def test05(self):
        "named_in_conversion finds multiple named fields - dict"
        conversion = {'st': 'abc',
                      '-': 'eee,def,finis',
                      'th': 'test',
                      }
        self.assertEqual(named_in_conversion(conversion), {'abc': None, 'eee': None, 'def': None, 'finis': None, 'test': None, })


class ShortenObjectName(unittest.TestCase):
    import os
    if os.name == 'posix':
        valid_dir = '/usr/local/geodatabase'
    else:
        valid_dir = "C:/Program Files/geodatabase"

    def test00(self):
        "loggable_name returns all parts after first non directory entry - empty"
        self.assertEqual(loggable_name(self.valid_dir), "")

    def test01(self):
        "loggable_name returns all parts after first non directory entry - one entry"
        self.assertEqual(loggable_name(self.valid_dir + "/level/"), "level")

    def test02(self):
        "loggable_name returns all parts after first non directory entry - two entries"
        self.assertEqual(loggable_name(self.valid_dir + "/level/second"), "level/second")


class GetTableAndJoinOnPrimaryKey(unittest.TestCase):
    tables = {'first': [{'pk': '1', 'abc':1, 'due':2, },
                        {'pk': '2', 'abc':4, 'due':3, },
                        {'pk': '3', 'abc':4, 'due':3, },
                        ],
              'second': [{'pk': '1', 'tre':1, },
                         {'pk': '2', 'tre':4, },
                         {'pk': '3', 'tre':4, },
                         ],
              'third': [{'pk': '1', 'tre':1, },
                        {'pk': '2', 'tre':4, },
                        ],
              }

    def test00(self):
        "get_table / primary_key: result is dict of dict"
        gp = mock.GpDispatch(default_table=None, tables=self.tables)
        table = get_table(gp, 'first', primary_key='pk')
        if sys.version_info < (2, 3):
            self.assertEqual(isinstance(table, types.DictionaryType), True)
        else:
            self.assertTrue(isinstance(table, types.DictionaryType))

    def test02(self):
        "get_table / primary_key: associates row to value of primary key"
        gp = mock.GpDispatch(default_table=None, tables=self.tables)
        table = get_table(gp, 'first', primary_key='pk')
        self.assertEqual(table['1'], self.tables['first'][0])

    def test04(self):
        "join_on_primary_key - returns augmented dictionary"
        gp = mock.GpDispatch(default_table=None, tables=self.tables)
        table = get_table(gp, 'first', primary_key='pk')
        augmented = join_on_primary_key(gp, table, 'second', 'pk')
        self.assertEqual(augmented, table)

    def test06(self):
        "join_on_primary_key - returns augmented contains data from second table"
        gp = mock.GpDispatch(default_table=None, tables=self.tables)
        table = get_table(gp, 'first', primary_key='pk')
        join_on_primary_key(gp, table, 'second', 'pk')
        self.assertEqual(table['1']['due'], 2)
        self.assertEqual(table['1']['tre'], 1)
        self.assertEqual(table['2']['due'], 3)
        self.assertEqual(table['2']['tre'], 4)

    def test10(self):
        "join_on_primary_key - does not complain if second table does not augment an object"
        gp = mock.GpDispatch(default_table=None, tables=self.tables)
        table = get_table(gp, 'first', primary_key='pk')
        join_on_primary_key(gp, table, 'third', 'pk')
        self.assertEqual(table['1']['tre'], 1)
        self.assertEqual(table['2']['tre'], 4)
        if sys.version_info < (2, 3):
            self.fail("can't test this in older python")
        else:
            self.assertRaises(KeyError, table['3'].__getitem__, 'tre')

    def test12(self):
        "join_on_primary_key - if first table does not define object, it remains unknown"
        gp = mock.GpDispatch(default_table=None, tables=self.tables)
        table = get_table(gp, 'third', primary_key='pk')
        join_on_primary_key(gp, table, 'first', 'pk')
        self.assertEqual(table['1']['due'], 2)
        self.assertEqual(table['2']['due'], 3)
        if sys.version_info < (2, 3):
            self.fail("can't test this in older python")
        else:
            self.assertRaises(KeyError, table.__getitem__, '3')


class GetTableWarnsAboutUnconvertedColumns(unittest.TestCase):
    tables = [{'pk': '1', 'abc':1, 'due':2, 'tre':2, 'ctr':2, },
              {'pk': '2', 'abc':4, 'due':3, 'tre':3, 'ctr':3, },
              {'pk': '3', 'abc':4, 'due':3, 'tre':3, 'ctr':3, },
              ]
    import logging
    log = logging.getLogger('test')
    handler = mock.Handler(level=logging.DEBUG)
    rootlog = logging.getLogger('')
    rootlog.addHandler(handler)
    orig_rootlog_level = rootlog.level

    def test00(self):
        "get_table - warns about unconverted columns"

        conversion = {'col1': 'abc',
                      'col2': 'tre',
                      'id': 'pk',
                      }
        self.handler.flush()
        gp = mock.GpDispatch(self.tables)
        table = get_table(gp, 'first', conversion=conversion, strict=True)
        self.assertTrue(table != None)
        relevant = [i for i in self.handler.content if i.find("remain unconverted") != -1]
        self.assertEquals(["nens.gp|WARNING|first: fields '['ctr', 'due']' remain unconverted"], relevant)
        self.rootlog.level = self.orig_rootlog_level

    def test01(self):
        "get_table - conversion is case insensitive"

        conversion = {'col1': 'ABC',
                      'col3': 'tre',
                      'col4': 'ctr',
                      'id': 'PK',
                      }
        self.handler.flush()
        gp = mock.GpDispatch(self.tables)
        self.rootlog.level = logging.DEBUG
        table = get_table(gp, 'first', conversion=conversion, strict=True)
        self.assertTrue(table != None)
        relevant = [i for i in self.handler.content if i.find("remain unconverted") != -1]
        self.assertEquals(["nens.gp|WARNING|first: fields '['due']' remain unconverted"], relevant)
        self.rootlog.level = self.orig_rootlog_level

    def test02(self):
        "get_table - explicitly ignored: no warning."

        conversion = {'col1': 'ABC',
                      'id': 'PK',
                      '-': 'ctr,due,tre',
                      }
        self.handler.flush()
        gp = mock.GpDispatch(self.tables)
        self.rootlog.level = logging.DEBUG
        table = get_table(gp, 'first', conversion=conversion)
        self.assertTrue(table != None)
        relevant = [i for i in self.handler.content if i.find("remain unconverted") != -1]
        self.assertEquals([], relevant)
        self.rootlog.level = self.orig_rootlog_level

    def test03(self):
        "get_table - all columns are converted, no warnings."

        conversion = {'col1': 'ABC',
                      'col2': 'due',
                      'col3': 'tre',
                      'col4': 'ctr',
                      'id': 'PK',
                      }
        self.handler.flush()
        gp = mock.GpDispatch(self.tables)
        self.rootlog.level = logging.DEBUG
        table = get_table(gp, 'first', conversion=conversion)
        self.assertTrue(table != None)
        relevant = [i for i in self.handler.content if i.find("remain unconverted") != -1]
        self.assertEquals([], relevant)
        self.rootlog.level = self.orig_rootlog_level

    def test10(self):
        "get_table - don't warn about unconverted columns if no conversion is given"

        self.rootlog.level = self.orig_rootlog_level
        self.handler.flush()
        gp = mock.GpDispatch(self.tables)
        table = get_table(gp, 'first')
        self.assertTrue(table != None)
        relevant = [i for i in self.handler.content if i.find("remain unconverted") != -1]
        self.assertEquals([], relevant)


class GetTableDefinition(unittest.TestCase):
    tables = [{'pk': '1', 'abc':1, 'due':2, },
              {'pk': '2', 'abc':4, 'due':3, },
              {'pk': '3', 'abc':4, 'due':3, },
              ]

    def test00(self):
        "get_table_def - checking initial implementation."

        gp = mock.GpDispatch(self.tables)
        types = get_table_def(gp, 'some_table_name')
        self.assertEqual(types, {'pk': '', 'abc': '', 'due': ''})


class ValidFileName(unittest.TestCase):

    def test00(self):
        "validfilename - leaves alphanumeric in peace"

        import random
        for i in range(50):
            key = ''.join([chr(random.randrange(65, 91)) for i in range(25)])
            self.assertEqual(key, validfilename(key))
        for i in range(50):
            key = ''.join([chr(random.randrange(97, 123)) for i in range(25)])
            self.assertEqual(key, validfilename(key))
        for i in range(50):
            key = 'a' + ''.join([chr(random.randrange(48, 58)) for i in range(25)])
            self.assertEqual(key, validfilename(key))
        for i in range(50):
            key = ''.join([chr(random.randrange(97, 123)) for i in range(25)])
            self.assertEqual(key[:20], validfilename(key, maxlen=20))

    def test01(self):
        "validfilename - removes symbols as of ticket 703"

        s = "spaties of !@#$%^&*()-{}[]:\";'>?./,<123"
        v = "spatiesof123"
        self.assertEqual(v, validfilename(s))

    def test02(self):
        "validfilename - removes leading numbers"

        s = "123spaties of !@#$%^&*()-{}[]:\";'>?./,<"
        v = "spatiesof"
        self.assertEqual(v, validfilename(s))

    def test10(self):
        "firstAvailableFilename on new name and default extension"

        gp = mock.GpDispatch(files=[])
        target = "abc.shp"
        current = firstAvailableFilename(gp, "abc")
        self.assertEqual(target, current)

    def test11(self):
        "firstAvailableFilename on new name and custom extension"

        gp = mock.GpDispatch(files=[])
        target = "abc.txt"
        current = firstAvailableFilename(gp, "abc", ".txt")
        self.assertEqual(target, current)

    def test12(self):
        "firstAvailableFilename on existing name and custom extension"

        gp = mock.GpDispatch(files=["abc.txt"])
        target = "abc_1.txt"
        current = firstAvailableFilename(gp, "abc", ".txt")
        self.assertEqual(target, current)

    def test13(self):
        "firstAvailableFilename on existing name and custom extension"

        gp = mock.GpDispatch(files=["abc.txt", "abc_1.txt"])
        target = "abc_2.txt"
        current = firstAvailableFilename(gp, "abc", ".txt")
        self.assertEqual(target, current)


class DoctestRunner(unittest.TestCase):
    def test0000(self):
        import doctest
        doctest.testmod(name=__name__[:-6])

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
#* Library    : more pythonic approach to the gp library.
#*
#* Project    : various
#*
#* $Id$
#*
#* initial programmer :  Mario Frasca
#* initial date       :  2008-07-28
#**********************************************************************

from __future__ import nested_scopes
__revision__ = "$Rev$"[6:-2]

import logging
log = logging.getLogger('nens.gp')
techlog = logging.getLogger('nens.')
log.debug('loading module')

import operator
import types

# Log level below DEBUG for logging that's even too verbose for the DEBUG level.
VERBOSE_LOGLEVEL = 5


def log_verbose(msg, *args, **kwargs):
    log.log(VERBOSE_LOGLEVEL, msg, *args, **kwargs)


import sys
if sys.version_info < (2, 3):
    False = 0
    True = 1

    types.StringTypes = types.StringType

    def dict(source):
        """avoiding error 'NameError: global name 'dict' is not defined'
        """

        if isinstance(source, types.ListType) or isinstance(source, types.TupleType):
            result = {}
            for key, value in source:
                result[key] = value
            return result
        if isinstance(source, types.DictionaryType):
            return source.copy()

    operator.itemgetter = lambda i: (lambda x: x[i])


class GpHandler(logging.Handler):
    """ Adds an extra handler to the logging class which displays messages in the ArcGIS window
    """

    class Formatter(logging.Formatter):
        def format(self, record):
            if self._fmt.find("%(relativeCreatedSeconds)") >= 0:
                record.relativeCreatedSeconds = record.relativeCreated / 1000.0
            return logging.Formatter.format(self, record)

    def __init__(self, level=logging.INFO, geoprocessor=None, format=None, *args, **kwargs):
        if geoprocessor == None:
            from sys import platform
            if platform == 'win32':
                # if no explicit geoprocessor is given, get the standard one from ArcGIS.
                import arcgisscripting
                geoprocessor = arcgisscripting.create()
            else:
                from nens import mock
                geoprocessor = mock.GpDispatch()
        self.geoproc = geoprocessor
        logging.Handler.__init__(self, level, *args, **kwargs)
        if format == None:
            format = '%(relativeCreatedSeconds)0.3f %(message)s'
        self.setFormatter(self.Formatter(format))

    def emit(self, record):
        try:
            message = self.format(record)
            if record.levelno >= logging.ERROR:
                self.geoproc.AddError(message)
            elif record.levelno >= logging.WARNING:
                self.geoproc.AddWarning(message)
            else:
                self.geoproc.AddMessage(message)
        except:
            self.handleError(record)


class gp_iterator:
    """iterating on anything with reset and next methods
    """
    def __init__(self, obj):
        self.__obj = obj
        self.__obj.reset()
        self.__index = None

    def next(self):
        result = self.__obj.next()
        if not result:
            raise StopIteration
        return result

    def __iter__(self):
        return self

    def __getitem__(self, index):
        if self.__index is None:
            self.__obj.reset()
            self.__index = 0
            result = self.__obj.next()
        if index < self.__index:
            raise IndexError("can only scan the iterator once")
        for i in range(self.__index, index):
            result = self.__obj.next()
            self.__index = index
        if result is None:
            raise IndexError("list index %d is out of range" % index)
        return result


def check_constraints(obj, field_name, constraints, on_error_fail=False):
    """boolean function, true if all constraints hold for value

    gets value associated to field_name in obj,
    constraints is list describing the constraints

    raises an exception if on_error_fail is True.
    returns False if the check fails on a strong constraint.
    returns True otherwise
    emits a warning if a check (strong or weak) fails.

    constraints is expected to be composed of:
    Integer
    NonNegative
    Positive
    DDMM - Integer holding a day of the year.
    MMDD - Integer holding a day of the year.
    [min, max] - an interval, either values can be a '-', which is ignored.
    W[min, max] - this is a weak constraint: logs a warning, but returns True.
    string(lenght) - string no longer than lenght characters
    (<condition>) - <condition> holds or the input is None
    """

    import re
    interval_pattern = re.compile(r'^([a-z]?)\[[ ]*([-0-9\.]+|[a-z_]+)[ ,]+([-0-9\.]+|[a-z_]+)[ ]*\]$', re.I)
    string_pattern = re.compile(r'string\(([0-9]+)\)', re.I)

    result = True

    log.debug("check_constraints for %s" % field_name)
    # get the string representation of the value from object
    value = obj[field_name]

    # get constraints from settings
    accept_none, constraints = split_constraints(constraints)
    if accept_none and value is None:
        return True

    try:
        fvalue = float(value)
        ivalue = int(fvalue)
    except:
        fvalue = ivalue = None

    log.debug("%s(%s)" % (type(value), value))

    # perform the check
    if fvalue:
        log.debug("checking s/f/i %s %0.6f %d, %s" % (value, fvalue, ivalue, constraints))
    else:
        log.debug("checking %s, %s" % (value, constraints))

    for i in [i.lower().strip() for i in constraints]:
        log.debug(i)
        justWarn = False
        matched_interval_pattern = interval_pattern.match(i)
        matched_string_pattern = string_pattern.match(i)
        ok = fvalue is not None
        if i == 'boolean':
            ok = value.lower() in ['1', '0', 'true', 'false', 'yes', 'no']
        elif i == 'percent':
            ok &= (fvalue >= 0)
            ok &= (fvalue <= 100)
        elif i == 'integer':
            ok &= (ivalue == fvalue)
        elif i == 'nonnegative':
            ok &= (fvalue >= 0)
        elif i == 'positive':
            ok &= (fvalue > 0)
        elif i in ['ddmm', 'mmdd']:
            try:
                if i == 'ddmm':
                    day, month = ivalue / 100, ivalue % 100
                if i == 'mmdd':
                    month, day = ivalue / 100, ivalue % 100
            except TypeError:
                day = month = 0
            try:
                import datetime
                datetime.datetime(2000, month, day)
                ok = True
            except ValueError:
                ok = False
            pass
        elif matched_interval_pattern:
            justWarn, min, max = matched_interval_pattern.groups()

            def translate(what):
                if what == '-':
                    return None
                try:
                    return obj[what]
                except:
                    return float(what)

            min = translate(min)
            max = translate(max)
            if min is not None:
                ok &= (fvalue >= min)
            if max is not None:
                ok &= (fvalue <= max)
        elif matched_string_pattern:
            max_lenght, = matched_string_pattern.groups()
            if max_lenght != '-':
                max_lenght = float(max_lenght)
            else:
                max_lenght = None
            ok = isinstance(value, types.StringTypes)
            if ok and max_lenght is not None:
                ok &= (len(value) <= max_lenght)
        else:
            log.warn("unrecognized pattern '%s'" % i)
            ok = True
        if not ok:
            log.warn("value %s in field %s does not respect constraint %s" %
                     (value, field_name, i))
        if justWarn:
            ok = True
        result &= ok

    if not result and on_error_fail:
        raise ValueError("value %s in field %s does not respect constraints %s" %
                         (value, field_name, ' '.join(constraints)))
    return result


def split_constraints(s):
    '''splits the string defining the range into its components

    returns a pair
    first indicates if None is acceptable
    second is list of atomic constraints

    splits on spaces that are separate atomic ranges.
    '''

    if s is None or s.strip() == '':
        return False, []

    if s[0] == '(' and s[-1] == ')':
        s = s[1:-1]
        accept_none = True
    else:
        accept_none = False

    import re
    p = re.compile(r'(?<=[\]a-z]) +(?=[\[a-z])', re.I)
    result = p.split(s)
    return accept_none, result

import re
array_key = re.compile("\[([a-z0-9_%]+)\][ ]*\[([0-9\.,-]+)\]", re.I)


def reverse_dict(forward):
    "returns a dictionary where keys are strings and values are lists"
    result = {}
    if isinstance(forward, types.DictionaryType):
        forward = forward.items()
    for k, v in forward:
        if isinstance(k, types.StringType):
            k = k.lower()
        if isinstance(v, types.StringType):
            if array_key.match(v):
                continue
            values = [i.lower() for i in v.split(',')]
        else:
            values = [v]
        for vi in values:
            result.setdefault(vi, []).append(k)
    return result


def evaluate_dict_fields(d, to_lower=False):
    """wherever possible, transforms fields to float or int.
    """

    result = {}
    for key, repr in dict(d).items():
        value = repr.lower()
        if repr[0] == repr[-1] == "'" or repr[0] == repr[-1] == '"':
            value = repr[1:-1]
        else:
            try:
                value = float(repr)
            except:
                pass
            try:
                value = int(repr)
            except:
                pass
        result[key] = value
    return result


def list_of_array_keys(pattern):
    "give me an 'array key' pattern, you get the corresponding list of tuples"

    match = array_key.match(pattern)
    if match is None:
        return []
    definition = match.group(2)
    if definition.count(',') == 1:
        definition += ",1"
    start, stop, step = [int(i) for i in definition.split(',')]
    stop = stop + 1
    return [(match.group(1) % k, k) for k in range(start, stop, step)]


def gp_as_dict(fields, object, conversion=None, defaults=None, evaluate=False, dictionaries={}, nonevalues=[],
               ranges={}, on_exception_raise=False, primary_key=None, no_shape=False):
    """extracts the values of the fields from the object and returns it as
    a dictionary.  a backward name conversion can be given, from the
    wished representation to the one found in the input data.

    if 'primary_key' is not None, the result is a pair where the first
    element is the value of the primary key and the second element is
    the dictionary representing the row.
    """

    reversed = dict([(k.lower(), [k.lower()]) for k in fields])
    if isinstance(conversion, types.DictionaryType):
        conversion = conversion.items()
    if conversion:
        reversed.update(reverse_dict(conversion))
    fields.sort()
    log_verbose("trying to get these fields out of the object..., %s" % (fields,))
    result = {}
    log_verbose("filling in defaults")
    if defaults is not None:
        defaults = dict(defaults)
        if evaluate:
            defaults = evaluate_dict_fields(defaults)
        result.update(defaults)
    else:
        defaults = {}
    log_verbose("getting values from object")
    for f in fields:
        if f == 'Shape' and no_shape is True:
            continue
        log_verbose("getting '%s' from %s" % (f, object))
        v = object.getvalue(f)
        for k in reversed[f.lower()]:
            result[k] = v
    log_verbose("overwriting None values with defaults.")
    for k, v in result.items():
        if v in nonevalues:
            result[k] = None
        if result[k] is None:
            result[k] = defaults.get(k)
    log_verbose("managed to get these fields out of the object..., %s" % (result.keys(),))

    if no_shape is not True:
        try:
            log_verbose('getting shape__centroid__x and y from shape.centroid')
            x, y = [float(i.replace(",", ".")) for i in object.shape.centroid.split(' ')]
            for k in reversed.get('shape__centroid__x', ['shape__centroid__x']):
                result[k] = x
            for k in reversed.get('shape__centroid__y', ['shape__centroid__y']):
                result[k] = y

            log_verbose('getting shape__area from shape.area')
            for k in reversed.get('shape__area', ['shape__area']):
                result[k] = object.shape.area
            log_verbose('getting shape__length from shape.length')
            for k in reversed.get('shape__length', ['shape__length']):
                result[k] = object.shape.length
        ## I would like to catch KeyError and AttributeError, but
        ## ArcGIS raises a generic RuntimeError.  I leave the two
        ## redundant more specific types for ease of search.
        except (KeyError, AttributeError, RuntimeError), e:
            log_verbose('accessing the shape: %s' % e)

    # now add the array of values, grouping them...
    if conversion:
        for candidate, pattern in conversion:
            if not array_key.match(pattern):
                continue

            # ok, so candidate is associated to an array of database fields
            log_verbose("looking for set of fields %s to decode into array %s" % (pattern, candidate))

            tried = []
            value = {}
            for key, k in list_of_array_keys(pattern):
                try:
                    tried.append(key)
                    value[k] = object.getvalue(key)
                except:
                    pass
            if value:
                result[candidate] = value
                log_verbose("defining %s as %s" % (candidate, value))
            else:
                log_verbose("not setting %s to anything" % (candidate,))
                pass

    for field_name, translation_rules in dictionaries.items():
        forward = evaluate_dict_fields(translation_rules, to_lower=True)
        reversed = dict([(k, v[0]) for k, v in reverse_dict(forward).items()])
        reversed = evaluate_dict_fields(reversed, to_lower=True)
        if field_name in result:
            old_value = result[field_name]
            try:
                old_value = old_value.lower()
            except:
                pass
            result[field_name] = reversed.get(old_value, old_value)

    if '-' in result:
        del result['-']
    fields = result.keys()
    fields.sort()
    log_verbose("returning result holding these fields..., %s" % (fields,))
    for key in result.keys():
        if not check_constraints(result, key, ranges.get(key), on_error_fail=on_exception_raise):
            return None
    if primary_key is not None:
        return (result[primary_key], result)
    else:
        return result


def named_in_conversion(conversion):
    """which database fields are named in the conversion dictionary.

    this function returns a 'dict' whereas a 'set' would be a more
    modern choice.
    """

    if conversion is None:
        return {}
    if not isinstance(conversion, types.DictionaryType):
        conversion = dict(conversion)
    result = reverse_dict(conversion)
    for pattern in conversion.values():
        result.update(dict(list_of_array_keys(pattern)))
    result = dict([(k, None) for k in result.keys()])
    return result


def get_table_def(gp, datasource):
    '''reads name and type of all fields of a table.

    returns a dictionary associating names to types
    '''

    return dict([(field.Name.lower(), field.Type)
                 for field in gp_iterator(gp.ListFields(datasource))])


def get_table(gp, datasource, conversion=None, defaults=None, evaluate=False, dictionaries={}, nonevalues=[],
              ranges={}, on_exception_raise=False, primary_key=None, no_shape=False, strict=False):
    """returns a table as a list/dictionary of dictionaries

    give me a geoprocessor gp and a valid name for a data source
    within gp, I will return you the content of the data source

    if 'primary_key' is None the result is a list of dictionaries.

    if 'primary_key' is not None, the result is a dictionary (key: the
    values of the field 'primary_key') of dictionaries.

    in either case, each the inner dictionaries holds the content of a
    database record.
    """

    log.debug("getting %s" % datasource)
    fields = [i.name for i in gp_iterator(gp.ListFields(datasource))]
    log.debug("table %s has fields %s." % (datasource, str(fields)))

    if conversion is None:
        log.debug("not discarding any field.")
    # check which fields from the datasource are not named in the
    # conversion and log all of them in a warning.
    unconverted = [item for item in fields if item not in named_in_conversion(conversion)]
    if conversion is not None and unconverted and strict:
        log.warn("%s: fields '%s' remain unconverted" % (datasource, unconverted))

    result = [gp_as_dict(fields, row,
                         conversion=conversion, defaults=defaults,
                         evaluate=evaluate, dictionaries=dictionaries,
                         nonevalues=nonevalues, ranges=ranges, on_exception_raise=on_exception_raise,
                         primary_key=primary_key, no_shape=no_shape)
              for row in gp_iterator(gp.SearchCursor(datasource))]
    result = [i for i in result if i is not None]
    if primary_key is not None:
        return dict(result)
    else:
        return result


def join_on_primary_key(gp, partial_result, datasource, primary_key, conversion=None, defaults=None,
                        evaluate=False, dictionaries={}, nonevalues=[], ranges={}, on_exception_raise=False):
    """joins a table to a dictionary of dictionaries

    give me a geoprocessor gp, a dictionary of dictionaries, a valid
    name for a data source within gp and the primary key of the data
    source, I will augment the dictionary of dictionaries with the
    content of the data source and return this augmented data to you.
    """

    right_table = get_table(gp, datasource, conversion=conversion, defaults=defaults,
                            evaluate=evaluate, dictionaries=dictionaries, nonevalues=nonevalues,
                            ranges=ranges, on_exception_raise=on_exception_raise,
                            primary_key=primary_key)
    for pk, item in partial_result.items():
        item.update(right_table.get(pk, {}))

    return partial_result


def join_dicts(dictlist1, dictlist2, key1, key2=None):
    """left outer join between lists of dictionaries

    returns a list of dictionaries where each element is a new
    dictionary holding all dict1 elements augmented with dict2, if any
    dict2 from dictlist2 matches dict1 from dictlist1
    """

    # key2 defaults to be the same as key1
    if key2 is None:
        key2 = key1

    # case insensitive is implemented by going to lower case.
    if isinstance(key1, types.StringType):
        key1 = key1.lower()
    if isinstance(key2, types.StringType):
        key2 = key2.lower()

    # prepare an index on the second list...  for better performance
    index2 = dict([(item[key2], item) for item in dictlist2])

    result = []
    for item in dictlist1:
        item = dict(item)
        item.update(index2.get(item[key1], {}))
        result.append(item)
    return result


def join_on_foreign_key(gp, dictlist, key=None, fields=None, table=None, pk=None, fk=None, conversion=None, sort_on=None, nonevalues=[], defaults=None, evaluate=False, ranges={}):
    """gets objects from the 'table' and joins them to those in 'dictlist'.

    for each object retrieved from the table, construct the list of
    values associated to the list 'fields'.

    the new objects are grouped by 'pk' and these are associated
    to the ones in 'dictlist' having the same value for the 'fk'
    field.

    in the end, in each element of 'dictlist', you have a 'key' value
    associated to the list of lists thus retrieved.
    """

    if fk == None:
        fk = pk
    if pk == None:
        pk = fk
    temp = [(i[pk], [i[k] for k in fields]) for i in get_table(gp, table, conversion, nonevalues=nonevalues, defaults=defaults, evaluate=evaluate, ranges=ranges)]
    pool = {}
    for i in temp:
        pool.setdefault(i[0], []).append(i[1])
    for i in dictlist:
        value = pool.get(i[fk], [])
        if sort_on is not None:
            value.sort(key=operator.itemgetter(sort_on))
        i[key] = value


def replace_notavalue(d, not_a_value):
    """replaces matching entries in dictionary d with None

    if a value in d matches a 'not_a_value' entries, the value in d is
    overwritten with a None.

    modifies and returns the modified dictionary.
    (version for 2.3 and later)
    """

    if isinstance(not_a_value, dict):
        not_a_value = not_a_value.values()
    elif not isinstance(not_a_value, (list, tuple)):
        not_a_value = [not_a_value]
    for k, v in d.items():
        if v in not_a_value:
            d[k] = None
    return d


def loggable_name(geo_name):
    """returns a shortened name

    give me a complete name of a ArcGIS thing, I'll strip the name of
    the ArcGIS database and return the remaining part"""

    import re
    import os
    splitter = re.compile(r"[\\/]")
    split = [i for i in splitter.split(geo_name) if i]
    if os.name == 'posix':
        split.insert(0, '')
    for i in range(1, len(split) + 1):
        try:
            os.listdir(os.sep.join(split[:i] + ['']))
        except:
            break
    return '/'.join(split[i:])


def firstAvailableFilename(gp, filename, ext=".shp"):
    """make unique name

    Deze functie bekijkt of een bepaalde file al bestaat (volgens de
    geoprocessor) en indien ja, dan wordt aan de filenaam een unique
    sequentieel getal toegevoegd.  De input is de filenaam zonder
    extensie.  extensie ext kan worden gespecificeerd en anders is het
    '.shp'

    return a valid filename that does not yet exist according to the geoprocessor.
    """
    # deze functie is gemaakt omdat arcgis soms een lock op een
    # bestand zet waardoor de file niet gedelete kan worden of
    # overschreven.  indien arcgis 9.3 gebruikt wordt is deze funcite
    # waarschijnlijk overbodig omdat je dan gebruik kan maken van
    # testschemalock.

    log.info("looking for an available filename in the geoprocessor")

    n = 0
    candidate = filename + ext
    while True:
        if not gp.Exists(candidate):
            return candidate
        n += 1
        candidate = filename + "_" + str(n) + ext

if sys.version_info < (2, 3):
    """redefine a few things for older python...
    """

    del replace_notavalue

    def replace_notavalue(d, not_a_value):
        """replaces matching entries in dictionary d with None

        if a value in d matches a 'not_a_value' entries, the value in d is
        overwritten with a None.

        modifies and returns the modified dictionary.
        (version for before 2.3)
        """

        if isinstance(not_a_value, types.DictionaryType):
            not_a_value = not_a_value.values()
        elif not isinstance(not_a_value, types.ListType) and not isinstance(not_a_value, types.TupleType):
            not_a_value = [not_a_value]
        for k, v in d.items():
            if v in not_a_value:
                d[k] = None
        return d


class validfilename_functor:
    def __init__(self):
        import re
        self.symbols = re.compile(r'[!@#\$%\^&\*()\-\+=_{}\[\]:";\'>\?\./,< ]')
        self.leadingdigits = re.compile(r'^[0-9]*')

    def __call__(self, name, maxlen=30):
        result = name
        result = ''.join(self.symbols.split(result))[:maxlen]
        result = ''.join(self.leadingdigits.split(result))[:maxlen]
        return result

validfilename = validfilename_functor()


def parse_arguments(definition, argv=sys.argv):
    """convert arguments according to definition

    >>> parse_arguments({1: ('opt', 'config'),
    ...                  2: ('arg', 0),
    ...                  3: ('arg', 1)}, ['a', 'b', 'c', 'd'])
    ({'config': 'b'}, ['c', 'd'])
    >>> parse_arguments({1: ('opt', 'config'),
    ...                  2: ('arg', 3),
    ...                  3: ('arg', 1)}, ['a', 'b', 'c', 'd'])
    ({'config': 'b'}, [None, 'd', None, 'c'])
    >>> parse_arguments({1: ('arg', 3),
    ...                  2: ('arg', 1),
    ...                  3: ('opt', 'config'),
    ...                  4: ('opt', 'water')}, ['a', 'b', 'c', 'd', '#'])
    ({'water': None, 'config': 'd'}, [None, 'c', None, 'b'])
    >>> parse_arguments({1: ('arg', 0), 2: ('arg', 1)}, ['command', 'input', 'output'])
    ({}, ['input', 'output'])
    """

    options = {}
    args = [None] * (max([field for (container_name, field) in definition.values()
                         if container_name == 'arg']) + 1)
    container = {'arg': args, 'opt': options}

    for index, (container_name, field) in definition.items():
        value = argv[index]
        if value == '#':
            value = None
        container[container_name][field] = value

    return options, args

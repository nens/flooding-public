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
# Copyright 2008, 2009 Mario Frasca
#
#***********************************************************************
#* Library    : defines sobek objects, enables reading and comparing
#*
#* Project    : various
#*
#* $Id$
#*
#* initial programmer :  Mario Frasca
#* initial date       :  2008-07-28
#**********************************************************************

"""this module defines classes that are useful for reading and writing sobek files.

one way to use this is by reading a sobek file into a ``nens.sobek.File`` object.

you can then access the objects by type, index or id.

objects can be queried and altered.

if you alter the content, you may save the ``nens.sobek.File`` container.

"""

__revision__ = "$Rev$"[6:-2]

from types import StringTypes, NoneType

NoneValue = -99999
max_decimal_digits = 15

import logging
import datetime
import os
import os.path
import re
from struct import unpack

log = logging.getLogger('nens.sobek')


def deprecated(func):
    """use this decorator to mark functions as deprecated.

    calling a function marked as deprecated will result in a warning
    being emitted.
    """

    def new_func(*args, **kwargs):
        log.warn("Call to deprecated function %s." % func.__name__,
                 category=DeprecationWarning)
        return func(*args, **kwargs)

    new_func.__name__ = func.__name__
    new_func.__doc__ = func.__doc__
    new_func.__dict__.update(func.__dict__)
    return new_func


def print_float(value):
    # don't try to be smart with exponent notation
    if value >= 1e9:
        return '%g' % value
    # natural notation
    from math import log, ceil
    try:
        leading_length = ceil(log(value) / log(10))
    except (ValueError, OverflowError):
        leading_length = 0
    trailing_length = min(15 - leading_length, max_decimal_digits)

    format = "%%0.%if" % trailing_length
    result = format % value
    while result[-1] == '0':
        result = result[:-1]
    if result[-1] == '.':
        result = result[:-1]
    return result


valueTags = ['PDIN', 'TBLE', 'CLTT', 'CLID']


def isvalue(text):
    if text[0] == text[-1] == "'":
        return True
    if text == '<':
        return True
    if text in valueTags:
        return True
    try:
        int(text)
        return True
    except:
        pass
    try:
        float(text)
        return True
    except:
        pass
    return False


def value(text):
    if text == "":
        return ""
    if text[0] == text[-1] == "'":
        return text[1:-1]
    try:
        return int(text)
    except:
        pass
    try:
        return float(text)
    except:
        pass
    return text

splitter = re.compile(r'[ \t\n]+')


def despace_strings(text):
    """returns altered text where included strings have no spaces.
    """

    instring = False
    result = []
    for ch in text:
        if ch == "'":
            instring = not instring
        if (ch in [' ', '\t']) and instring:
            ch = chr(0)
        result.append(ch)
    result = ''.join(result)
    return result


def respace_strings(text):
    return text.replace(chr(0), ' ')


class File(object):
    '''represents a list of Sobek objects.'''

    sourcedir = '.'

    @classmethod
    def setSourceDir(cls, d):
        if os.path.isdir(d):
            cls.sourcedir = d
        else:
            # raise an exception
            os.chdir(d)

    @classmethod
    def getSourceDir(cls):
        return cls.sourcedir

    pattern = re.compile(r'[A-Z][A-Z0-9_]{3}', re.I)

    def _str_to_stream(self, input):
        "this is part of the initialization process"
        self.source = None
        if isinstance(input, StringTypes):
            pastlastsep = (input.rfind(os.sep) + 1)
            if not pastlastsep and os.altsep:
                pastlastsep = input.rfind(os.altsep) + 1
            self.basename = input[pastlastsep:]
            if pastlastsep == 0:
                input = self.sourcedir + os.sep + input
            self.source = input
            try:
                input = file(self.source)
            except IOError:
                input = None
        return input

    def __len__(self):
        return len(self.content)

    def __init__(self, input):
        """initialize a ``File`` object from a file or a file name.

        if ``input`` is a file name, the name is held in
        ``self.source`` and can be used in a subsequent call to
        ``save``.
        """

        self.basename = None
        input = self._str_to_stream(input)
        content, self.extension, self.version = content_of_sobek_file(input, with_version=True)
        self.content = split_sobek_content(content)
        self.hashed = {}
        for i in self.content:
            self.hashed.setdefault(i.tag, [])
            self.hashed[i.tag].append(i)

    def writeToStream(self, output):
        """write self to an open writable output stream.
        """

        result = []
        if self.version and self.extension:
            result.append("%s%1.1f" % (self.extension, self.version))
        for item in self.content:
            result.append(str(item))

        if len(result) and result[-1] != '':
            result.append('')
        result = '\n'.join(result)

        output_methods = output.__class__.__dict__
        if 'writestr' in output_methods:
            ### Disabled due usage on ubuntu, enable it for windows, task 120
            # result = result.replace('\n', '\r\n')
            output.writestr(self.basename, result)
        elif 'write' in output_methods:
            output.write(result)
        else:
            raise TypeError("don't know how to write to a %(__name__)s" % type(output))
        pass

    def save(self, destdir=None):
        """write ``self`` to ``destdir``.

        the behaviour depends on the type of destdir.
          - if a stream, ``self`` is written to it.
          - if None, ``self`` is rewritten to ``self.source``.
          - if a directory name, ``self`` is written to its
            corresponding file in that directory.

        """

        if isinstance(destdir, (NoneType, StringTypes)):
            if destdir is None:
                dest = self.source
            else:
                dest = destdir + os.sep + self.basename
            output = file(dest, "w")
            self.writeToStream(output)
            output.close()
        else:
            self.writeToStream(output)

    def append(self, obj):
        if not isinstance(obj, Object):
            raise TypeError("can't add this kind of objects")
        self.content.append(obj)
        self.hashed.setdefault(obj.tag, [])
        self.hashed[obj.tag].append(obj)

    def addObject(self, obj):
        self.append(obj)

    def _getindex(self, type, id, pool=None):
        if pool is None:
            pool = self.hashed.get(type.upper(), [])
        for i, item in enumerate(pool):
            log.debug('maybe this? %s(%s)' % (str(item), item.id))
            if item.id == id:
                return i
        raise KeyError("no %s object with id '%s'" % (type, id))

    def __delitem__(self, i):
        if isinstance(i, tuple):
            type, i = i
        else:
            raise ValueError('can remove one item at a time')
        if isinstance(i, StringTypes):
            i = self._getindex(type, i)
        obj = self.hashed[type][i]
        del self.hashed[type][i]
        self.content.remove(obj)

    def __getitem__(self, i):
        if isinstance(i, int):
            return self.content[i]

        if isinstance(i, tuple):
            i, id = i
        else:
            id = None

        if not isinstance(i, str) or not self.pattern.match(i):
            raise ValueError("not legal key %s(%s).  must be string [A-Z_0-9]{4}" %
                             (type(i).__name__, repr(i)))
        result = self.hashed.get(i.upper(), [])
        log.debug('File being asked for %s, %s' % (i, id))
        log.debug('candidates for __getitem__ are %s' % result)
        if id is None:
            log.debug('returning the whole result')
            return result
        else:
            log.debug('choosing item with id %s' % id)
            return result[self._getindex(i, id, result)]

    def keys(self):
        return self.hashed.keys()


class Verbatim(File):
    '''represents a file which knows how to save itself'''

    def __init__(self, input):
        stream = self._str_to_stream(input)
        if stream is None:
            raise IOError("File not found: " + input)
        self.content = stream.readlines()
        self.hashed = {}
        self.extension = self.version = None
        self.lines = self.lines_generator()

    def __getitem__(self, i):
        raise IndexError("can't look at a verbatim as if it was a list")

    def writeToStream(self, output):
        output_methods = output.__class__.__dict__
        tmp = ''.join(self.content)
        if 'writestr' in output_methods:
            ### Disabled due usage on ubuntu, enable it for windows, task 120
            # if self.basename[-3:].lower() not in ['zip', 'nvl']:
            #     tmp = tmp.replace('\n', '\r\n')
            output.writestr(self.basename, tmp)
        elif 'write' in output_methods:
            output.write(tmp)
        else:
            raise TypeError("don't know how to write to a %(__name__)s" % type(output))
        pass

    def append(self, obj):
        raise NotImplementedError("can't append to Verbatim files")

    def replace(self, old, new, count=-1):
        self.content = [i.replace(old, new, count) for i in self.content]

    def truncate(self, size=0):
        if size != 0:
            raise ValueError("can only truncate a Verbatim to empty string")
        self.content = []

    def write(self, s):
        self.content.append(s)

    def reset(self):
        self.lines = self.lines_generator()

    def readline(self):
        try:
            return self.lines.next()
        except StopIteration:
            return ''

    def lines_generator(self):
        for i in self.content:
            yield i


class Network(Verbatim):

    header = ["ID_NETWORK", "NAME_NETWORK", "", "", "TYPE_NETWORK",
              "", "", "", "", "", "LENGTE", "", "", "", "ID_FROM",
              "NAME_FROM", "", "", "", "TYPE_FROM", "", "X_COORD_FROM",
              "Y_COORD_FROM", "", "", "", "", "ID_TO", "NAME_TO", "",
              "", "", "TYPE_TO", "", "X_COORD_TO", "Y_COORD_TO", "",
              "", "", ""]

    def __init__(self, input):
        Verbatim.__init__(self, input)

        log.debug('get CSV content as list of dictionaries.')
        import csv
        stream = self._str_to_stream(input)
        input_reader = csv.reader(stream)
        input_data = [dict(zip(self.header, i))
                      for i in input_reader
                      if len(i) == len(self.header)]
        log.debug('%d candidate elements' % len(input_data))

        log.debug('throw away all that does not match type_network == "SBK_CHANNEL"')
        input_data = [i for i in input_data if i['TYPE_NETWORK'] == "SBK_CHANNEL"]
        log.debug('%d candidate elements' % len(input_data))

        self.categorized = {}
        self.dict = {}

        for item in input_data:
            log.debug("%s" % item)
            ## check #3200#comment:9
            for type, ident, x_coord, y_coord in [(item["TYPE_NETWORK"], item["ID_NETWORK"],
                                                   (item["TYPE_FROM"], item["ID_FROM"]), (item["TYPE_TO"], item["ID_TO"])),
                                                  (item["TYPE_FROM"], item["ID_FROM"],
                                                   item["X_COORD_FROM"],
                                                   item["Y_COORD_FROM"]),
                                                  (item["TYPE_TO"], item["ID_TO"],
                                                   item["X_COORD_TO"],
                                                   item["Y_COORD_TO"])]:
                self.categorized.setdefault(type, {})
                self.categorized[type][ident, x_coord, y_coord] = True
                self.dict.setdefault(type, {})
                self.dict[type][ident] = (x_coord, y_coord)

    def __getitem__(self, key):
        return self.categorized[key]

    def __contains__(self, key):
        return key in self.categorized


class Object(object):
    '''represents a Sobek object or array.

    a sobek object has a tag, an id and a variable amount of fields.
    a sobek array has a tag and holds a variable amount of values.

    each field can hold a single value, a list of values, a sobek
    array or a sobek object.
    '''

    def __init__(self, input=None, tag=None, id=None, name=None, cols=None):
        self.fields = {}
        self.order = []
        self.tables = {}
        self.content = []
        if input is None:
            if tag is None:
                raise ValueError("can't initialize object without input nor tag")
            if id is None:
                import uuid
                id = str(uuid.uuid4())
            self.tag = tag
            if tag != 'TBLE':
                self['id'] = id
            else:
                self.id = None
                self.__cols = cols
        else:
            if tag is not None:
                raise ValueError("can't initialize object with both input and tag")
            self.tag = None
            if isinstance(input, StringTypes):
                input = [respace_strings(i) for i in splitter.split(despace_strings(input)) if i]
            source = ' '.join(input)
            try:
                self.initFromList(input)
            except:
                raise ValueError("can't initialize object from '%s'" % source)
            self._hash = repr(self.fields).__hash__()
            if 'id' in self.fields:
                self.id = self.fields['id'][0]
            else:
                self.id = None
            if self.tag == 'TBLE':
                try:
                    self.__cols = self['TBLE'].index('<')
                except ValueError:
                    self.__cols = None
        if name is not None:
            if self.tag == 'TBLE':
                self.name = name
            else:
                self['nm'] = name
        if self.tag == 'TBLE':
            self.table_data = {}
            row_no = 0
            row_values = []
            for item in self['TBLE']:
                if item == '<':
                    col_no = 0
                    for v in row_values:
                        self.table_data[row_no, col_no] = v
                        col_no += 1
                    row_no += 1
                    row_values = []
                    continue
                row_values.append(item)

    def initFromList(self, input):
        if isvalue(input[1]):
            # we're constructing an array
            self.tag = input.pop(0)
            values = []
            while input[0] != self.tag.lower():
                values.append(value(input.pop(0)))
            closing_tag = input.pop(0)
            self.fields[self.tag] = values
            self.order.append(self.tag)
        else:
            self.tag = input.pop(0)
            if self.tag == 'TBLE' and input[0] != 'tble' and not isvalue(input[0]):
                # specifying name and length...
                self.name = input.pop(0)
                input.pop(0)
            while input[0] != self.tag.lower():
                #print self.fields
                #print input
                i = input.pop(0)
                values = []
                if isvalue(i) and i not in valueTags:
                    # seems to be a loose literal...
                    self.fields.setdefault(self.tag, [])
                    self.fields[self.tag].append(value(i))
                elif i == i.upper():
                    # included object
                    input.insert(0, i.strip())
                    self.addObject(Object(input))
                else:
                    # field - copy it then scan all its optional values
                    fields = []
                    if not isvalue(input[0]):
                        i = i + ' ' + input.pop(0)
                    key = i
                    while isvalue(input[0]):
                        if input[0] in valueTags:
                            fields.append(Object(input))
                        else:
                            fields.append(value(input.pop(0)))
                        if key in ['id', ]:
                            break
                    self.fields[key] = fields
                    if key not in self.order:
                        self.order.append(key)
            closing_tag = input.pop(0)
        return closing_tag

    def __lt__(self, other):
        return self.fields.__lt__(other.fields)

    def __eq__(self, other):
        return self.fields.__eq__(other.fields)

    def __hash__(self):
        return self._hash

    def print_field(self, value, depth=0):
        if isinstance(value, (float, int, long)):
            value = print_float(value)
        elif isinstance(value, StringTypes):
            if value == '<':
                value = '<' + '  ' * depth
            else:
                value = "'" + value + "'"
        elif isinstance(value, datetime.datetime):
            value = value.strftime("'%Y-%m-%d;%H:%M:%S'")
        elif isinstance(value, datetime.timedelta):
            # sorry, too lazy to program it properly...
            day = datetime.datetime(2000, 1, 10, 0, 0, 0) + value
            value = "'" + day.strftime("%d:%H:%M:%S")[1:] + "'"
        elif isinstance(value, Object):
            inc_obj = value.__repr__(depth=depth)
            if self.tag == 'DOMN':
                depth = depth + 1
            log.debug("string representation of included object = %s" % inc_obj)
            # objects as CLID and CLTT do not want to go on a new line
            if value.tag not in ['CLID', 'CLTT']:
                value = '\n'.join([''] + [('  ' * depth + i) for i in inc_obj.split('\n')])
            else:
                value = inc_obj
        else:
            raise TypeError("can't handle this type: " + str(type(value)))
        return value

    def __repr__(self, depth=0):
        parts = []
        done = []

        if self.id is None and len(self.fields) == 1 and self.tag in self.fields:
            log.debug("string representation of an array")
            parts.append(self.tag)
            if self.tag == 'TBLE':
                if 'name' in self.__dict__:
                    parts.append(self.name)
                    parts.append(str(self.fields[self.tag].count('<')))
                parts.append(chr(0))
            for value in self.fields[self.tag]:
                parts.append(self.print_field(value))
            parts.append(self.tag.lower())
        else:
            log.debug("string representation of a true sobek object")
            ordered_fields = list(self.order)
            ordered_fields.extend([k for k in self.fields if k not in self.order])
            parts.append(self.tag)
            for field_name in ordered_fields:
                if field_name != field_name.upper():
                    parts.append(field_name)
                done.append(field_name)
                for value in self.fields[field_name]:
                    parts.append(self.print_field(value, depth=depth))
            if self.tag.lower() == 'domn':
                parts.append('\ndomn')
            else:
                parts.append(self.tag.lower())

        result = ' '.join(parts)
        result = result.replace(chr(0) + ' ', '\n')
        result = result.replace('< ', '<\n')
        return result

    def __delitem__(self, key):
        try:
            self.order.remove(key)
        except ValueError:
            pass
        del self.fields[key]

    def __getitem__(self, key, value=None):
        if isinstance(key, tuple):
            if self.tag == 'TBLE':
                return self.table_data[key]
            else:
                raise ValueError("indexing by tuple only allowed in TBLE")
        if isinstance(key, int):
            return self.content[key]
        return self.fields.setdefault(key, value or list())

    def __setitem__(self, key, value):
        if value is None:
            value = NoneValue
        if isinstance(key, tuple) and self.tag == 'TBLE':
            self.table_data[key] = value
            row, col = key
            self.fields['TBLE'][(self.__cols + 1) * row + col] = value
        elif isinstance(value, (list, tuple)):
            self.fields[key] = list(value)
        else:
            self.fields[key] = [value]
        if key not in self.order:
            self.order.append(key)
        if key == 'id':
            if isinstance(value, (list, tuple)):
                value = value[0]
            self.__dict__['id'] = value

    def __setattr__(self, key, value):
        if key == 'id' and 'id' in self.__dict__:
            raise AttributeError("can't redefine id attribute")
        object.__setattr__(self, key, value)

    def addObject(self, obj):
        self.fields.setdefault(obj.tag, [])
        self.fields[obj.tag].append(obj)
        self.content.append(obj)
        if obj.tag not in self.order:
            self.order.append(obj.tag)
        return obj

    def addRow(self, row, add_table=True, to_table=None, decimals=None):
        if self.tag == 'TBLE':
            add_to = self
        else:
            if to_table is None:
                if 'TBLE' not in self.fields:
                    if not add_table:
                        raise AttributeError("object does not have a TBLE field")
                    else:
                        self.addObject(Object("TBLE tble"))
                add_to = self['TBLE'][0]
            else:
                if to_table not in self.tables:
                    table = self.addObject(Object("TBLE tble"))
                    table.name = to_table
                    self.tables[to_table] = table
                add_to = self.tables[to_table]

        if add_to.__cols is None:
            add_to.__cols = len(row)
        if len(row) != add_to.__cols:
            raise ValueError("adding row with incorrect lenght")
        row_no = add_to.rows()

        col_no = 0
        for item in row:
            try:
                item = round(item, decimals)
            except:
                pass
            add_to['TBLE'].append(item)
            add_to[row_no, col_no] = item
            col_no += 1
        add_to['TBLE'].append('<')

    def clone(self):
        import copy
        return copy.deepcopy(self)

    def cols(self):
        "returns the amount of columns in a TBLE"
        return self.__cols

    def rows(self):
        "returns the amount of rows in a TBLE"

        if self.tag != 'TBLE':
            raise AttributeError("only TBLE objects have rows")

        if self.__cols is None:
            return 0

        return len(self['TBLE']) / (self.__cols + 1)

    def attribs(self):
        return self.fields.keys()

    def __contains__(self, key):
        return key in self.fields


class HISFile(Verbatim):
    """Read sobek ``his`` file en make timeseries visible.

    interne gegevenstructuren:

      - ``bin``: compleet inhoud van his file.
      - ``parameter_names``, ``location_names``: dictionaries.  ze
        koppelen de naam van een parameter/location aan zijn
        sequentiele plaats in het his bestand.

    """

    def __init__(self, input):
        input = self._str_to_stream(input)
        self.bin = input.read()
        #simple checks
        if self.bin[0:40].strip() != 'SOBEK':
            raise ValueError('HIS file corrupt.')

        #read

        reg = re.compile('T0: (?P<year>\d+)\.(?P<month>\d+)\.(?P<day>\d+) (?P<hour>\d+):(?P<minute>\d+):(?P<second>\d+)[ ]*\(scu=[ ]*(?P<scu>\d+).*')
        match = reg.match(self.bin[120:160])
        props = match.groupdict()

        self.dtstart = datetime.datetime(
            int(props['year']), int(props['month']), int(props['day']),
            int(props['hour']), int(props['minute']), int(props['second']))

        self.calc_timestep = int(props['scu'])

        self.nrof_parameters = unpack('<L', self.bin[160:164])[0]  # little endian
        self.nrof_locations = unpack('<L', self.bin[164:168])[0]  # little endian
        self.size_of_timestep = 4 + 4 * self.nrof_parameters * self.nrof_locations

        self.parameter_names = {}
        for p_count in range(self.nrof_parameters):
            idx_start = 168 + p_count * 20
            idx_end = idx_start + 20
            self.parameter_names[self.bin[idx_start:idx_end].strip()] = p_count

        self.location_names = {}
        for l_count in range(self.nrof_locations):
            idx_start = 168 + self.nrof_parameters * 20 + l_count * 24
            idx_end = idx_start + 20
            self.location_names[self.bin[idx_start + 4:idx_end].strip()] = l_count

        self.size_of_header = 168 + self.nrof_parameters * 20 + self.nrof_locations * 24

        self.timesteps = (len(self.bin) - self.size_of_header) / self.size_of_timestep

        idx_start = self.size_of_header + 0 * self.size_of_timestep
        idx_end = idx_start + 4
        ts_0 = unpack('<L', self.bin[idx_start:idx_end])[0]
        idx_start = self.size_of_header + 1 * self.size_of_timestep
        idx_end = idx_start + 4
        ts_1 = unpack('<L', self.bin[idx_start:idx_end])[0]

        self.nr_calc_timesteps_in_result_timestep = ts_1 - ts_0
        self.result_timestep = self.nr_calc_timesteps_in_result_timestep * self.calc_timestep
        log.debug('tijdstap resultaat is ' + str(self.result_timestep) + ' ' + str(self.nr_calc_timesteps_in_result_timestep) + ' ' + str(self.calc_timestep))

    def size(self):
        """the length (number of readings) of the timeseries"""
        return self.timesteps

    def parameters(self):
        """the parameters in the timeseries"""
        return self.parameter_names.keys()

    def locations(self):
        """the locations in the timeseries"""
        return self.location_names.keys()

    def get_timestamps(self):
        """return the timestamps for the values in the file"""

        return [self.get_datetime_of_timestep(i) for i in range(self.timesteps)]

    def get_timeseries(self, location_name, parameter_name, start=None, end=None, result_type=dict):
        """return the timeseries at location/parameter.

        a timeseries is a dictionary associating timestamp to value
        """

        result = [(self.get_datetime_of_timestep(i), v)
                  for i, v in enumerate(self.get_values(location_name, parameter_name))]
        if start:
            start = mk_datetime(start)
            result = [(t, v) for (t, v) in result if t >= start]
        if end:
            end = mk_datetime(end)
            result = [(t, v) for (t, v) in result if t < end]
        return result_type(result)

    def get_parameter_index(self, name):
        """return index of first matching parameter.

        if name is present in HIS file, its index is returned.

        otherwise interpret name as a regular expression and find the
        first match.  this is not guaranteed to provide the same
        result each time, as the order of the keys of a dictionary is
        dependent on the content of the dictionary and we return the
        first matching name.
        """

        if name not in self.parameter_names:

            par_re = re.compile(name)
            for p in self.parameter_names.keys():  # implementation
                                                   # dependent order
                if par_re.match(p):
                    log.warn("you asked for parameter '%s', you got '%s'." %
                             (name, unicode(p, errors='replace')))
                    name = p
                    break
            else:
                raise KeyError('parameter ' + name + ' not in hisfile')

        return self.parameter_names[name]

    def get_values(self, location_name, parameter_name, dtstart=None, dtend=None):
        """get complete timeseries at location/parameter.
        """

        if dtstart is not None or dtend is not None:
            log.warn("dtstart/dtend in nens.sobek.HISFile.get_values have no effect.")
        if location_name in self.location_names:
            idx_location = self.location_names[location_name]
        else:
            raise KeyError('location ' + location_name + ' not in hisfile ')

        idx_parameter = self.get_parameter_index(parameter_name)
        timestep_start = 0
        timestep_end = self.timesteps
        return self.get_timeseries_by_index(idx_location, idx_parameter, timestep_start, timestep_end)

    def get_timeseries_by_index(self, idx_location, idx_parameter, timestep_start, timestep_end):
        """get complete timeseries at location/parameter.
        """

        return [self.get_value(idx_location, idx_parameter, i)
                for i in range(timestep_start, timestep_end)]

    def get_values_timestep_by_index(self, idx_parameter, idx_timestep):
        """get values for all locations for given parameter/timestamp.
        """

        return dict([(name, self.get_value(value, idx_parameter, idx_timestep))
                     for name, value in self.location_names.items()])

    def get_value(self, idx_location, idx_parameter, idx_timestep):
        """get single value read at location/parameter/timestamp.
        """

        idx_start = (self.size_of_header +
                     idx_timestep * self.size_of_timestep +
                     (4 + idx_location * 4 * self.nrof_parameters + idx_parameter * 4))
        idx_end = idx_start + 4
        return unpack_floats(self.bin[idx_start:idx_end])[0]

    def get_datetime_of_timestep(self, idx_timestep):
        """get timestamp of given index.
        """

        pos = self.size_of_header + idx_timestep * self.size_of_timestep
        seconds = unpack('<L', self.bin[pos:pos + 4])[0] * self.calc_timestep
        return self.dtstart + datetime.timedelta(0, seconds)


def unpack_floats(input):
    return [float("%1.7g" % d) for d in unpack("<f", input)]


def mk_datetime(seconds_or_datetime):
    if isinstance(seconds_or_datetime, int):
        return datetime.datetime(1970, 1, 1) + datetime.timedelta(0, seconds_or_datetime)
    elif isinstance(seconds_or_datetime, datetime.datetime):
        return seconds_or_datetime
    else:
        raise TypeError("mk_datetime can only handle int or datetime.datetime, got %s instead." % type(seconds_or_datetime))


class SobekHIS(HISFile):
    @deprecated
    def __init__(self, input):
        '''a SobekHIS is different from a HISFile in that you
        initialize if with its content (not the stream)

        its get_timeseries method is different from the HISFile implementation
        '''
        from nens import mock
        HISFile.__init__(self, mock.Stream(input))

    @deprecated
    def get_timeseries(self, *argv, **kwargs):
        return self.get_values(*argv, **kwargs)


def compare_two_lists(first, second):
    """computes the differences between first and second files...

    the differences is a 5-tuple of the following values:
    number of elements in first file,
    number of elements in second file,
    elements in common,
    elements in first file which are not in the second one,
    elements in second file which are not in the first one.
    """

    #print len(first), len(second)

    # create the indices for the objects read
    hash_orig = dict((item, None) for item in first)
    hash_new = dict((item, None) for item in second)

    # create list of objects in one file not present in other
    intersection = [item for item in first if item in hash_new]
    orig_min_new = [item for item in first if item not in hash_new]
    new_min_orig = [item for item in second if item not in hash_orig]

    return (len(first), len(second), intersection, orig_min_new, new_min_orig)


def compare_two_files(first, second):
    "see: compare_two_lists"

    # read from files into lists of objects
    list_orig = split_sobek_content(content_of_sobek_file(file(first)))
    list_new = split_sobek_content(content_of_sobek_file(file(second)))
    return compare_two_lists(list_orig, list_new)


def compare_two_domains(first, second):
    """computes the difference between first and second domain

    it's an in-place substitution for compare_two_files, but works on
    the *content* of the two domains.

    see: compare_two_lists
    """

    domain_content_re = re.compile(r'DOMN .*?([A-Z0-9_]{4} .*)domn', re.S)

    first_content = content_of_sobek_file(file(first))
    match = domain_content_re.match(first_content)
    if not match:
        return None
    first_content = match.group(1)

    second_content = content_of_sobek_file(file(second))
    match = domain_content_re.match(second_content)
    if not match:
        return None
    second_content = match.group(1)

    #print first_content, second_content
    list_orig = split_sobek_content(first_content)
    list_new = split_sobek_content(second_content)
    #print list_orig, list_new
    return compare_two_lists(list_orig, list_new)


def content_of_sobek_file(stream, with_version=False):
    "reads a sobek file returning a content rich string"

    if stream is None:
        extension = version = None
        input = ""
    else:
        input = stream.read()
        # fall back to Mac separator style (the lazy way).
        input = input.replace('\r', '\n')
        input = input.replace('\n\n', '\n')

        # it may start with three chars plus some version number.
        fileversion_re = re.compile(r'^([A-Z0-9_]{3})([0-9]+\.[0-9]+)$')
        try:
            header, rest = input.split("\n", 1)
        except ValueError:
            header, rest = input, ''

        version = fileversion_re.match(header)
        if version:
            #print "skipping header"
            extension, version = version.groups()
            version = float(version)
            input = rest
        else:
            extension, version = None, None

    #print extension, version_number, header, input[:20]
    if with_version:
        return input, extension, version
    else:
        return input


def split_sobek_content(input):
    """splits the input string into the sobek parts, matching the start
    tag with the first corresponding closing tag.

    returns a list of Object.
    """

    result = []

    first_word_re = re.compile(r"^[ \t\n]*([A-Z_0-9]+) (.*)", re.S)
    #print r"^[ \t\n]*([A-Z_0-9]+) (.*)", input[:20]

    while first_word_re.match(input):
        first_word_match = first_word_re.match(input)
        opening = first_word_match.group(1)
        closing = opening.lower()
        first_object_re_string = "([ \t\n]*%s[ \t\n]+.*?[ \t\n]+%s)[\t ]*(?:[\n]+|$)(.*)" % (opening, closing)
        first_object_re = re.compile(first_object_re_string, re.S)

        #print input, first_object_re_string,
        item, input = first_object_re.match(input).groups()
        #print item
        result.append(Object(item))

    return result

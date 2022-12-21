#!/usr/bin/python
#* this program is free software: you can redistribute it and/or
#* modify it under the terms of the GNU General Public License as
#* published by the Free Software Foundation, either version 3 of the
#* License, or (at your option) any later version.
#*
#* this program is distributed in the hope that it will be useful, but
#* WITHOUT ANY WARRANTY; without even the implied warranty of
#* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#* General Public License for more details.
#*
#* You should have received a copy of the GNU General Public License
#* along with the nens libraray.  If not, see
#* <http://www.gnu.org/licenses/>.
#*
#* $Id$
#*
#* initial programmer :  Mario Frasca
#**********************************************************************

"""this file contains a Python implementation of things defined in the
*Green Book* of hydrological objects.
"""

__revision__ = "$Rev$"[6:-2]

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

import re
import uuid
import types


def isSufHydKey(key):
    if not isinstance(key, types.StringTypes):
        return False
    return (len(key) == 7 and key[3] == '_') or (len(key) == 10 and key[3] == key[6] == '_')


def fieldwise(obj, representation=None):
    """let obj split its representation according to the field lengths
    """

    if representation is None:
        representation = obj.toSufHyd().strip()

    offset = 0
    r = []
    for length in [obj.getType(k)[1] for k in obj.field_names]:
        r.append((offset, length))
        offset += length

    result = '|'.join([representation[offset:offset + length] for offset, length in r])
    result = "|%s|" % result
    offset, length = r[-1]
    result += representation[offset + length:]
    return result


class GmlElement:
    formats = {
        str: '''\
<element name="%(name)s" minOccurs="0">
<simpleType>
<restriction base="string">
<maxLength value="%(len)s"/>
</restriction>
</simpleType>
</element>''',
        int: '<element name="%(name)s" minOccurs="0" type="integer"/>',
        float: '<element name="%(name)s" minOccurs="0" type="double"/>',
        }

    def __init__(self, name, type, len, opt=None):
        self.name = name
        self.type = type
        self.len = len
        self.opt = opt
        pass

    def setValue(self, value):
        self.value = value
        pass

    def toxml(self):
        dict = self.__dict__.copy()
        if self.type == float and isinstance(self.opt, int) and isinstance(self.value, float):
            format = '%%0.%df' % self.opt
            dict['value'] = format % self.value
        if isinstance(self.value, types.StringTypes):
            value = self.value
            value = value.replace('&', '&amp;')
            value = value.replace('"', '&quot;')
            value = value.replace("'", '&apos;')
            value = value.replace('<', '&lt;')
            value = value.replace('>', '&gt;')
            dict['value'] = value
        return '<fme:%(name)s>%(value)s</fme:%(name)s>' % dict

    def toxsd(self):
        return self.formats[self.type] % self.__dict__


class HydroObject:
    types = {
        'aan_inw': (int, 4),
        'aan_won': (int, 4),
        'afv_afs': (float, 5, 3),
        'afv_brg': (float, 4, 1),
        'afv_een': (str, 2),
        'afv_hel': (float, 9, 2),
        'afv_ide': (str, 10),
        'afv_ifa': (float, 5, 2),
        'afv_ifh': (float, 5, 2),
        'afv_ifn': (int, 4),
        'afv_ifx': (int, 4),
        'afv_ind': (int, 3),
        'afv_inr': (int, 3),
        'afv_len': (float, 7, 1),
        'afv_nam': (str, 40),
        'afv_opp': (float, 9, 2),
        'afv_ruw': (float, 5, 1),
        'afv_top': (str, 2),
        'afv_tas': (str, 2),
        'afv_vdp': (float, 4, 1),
        'afv_vla': (float, 9, 2),
        'afv_vlu': (float, 9, 2),
        'alg_dat': (str, 8),
        'alg_oms': (str, 70),
        'alg_opd': (str, 70),
        'alg_ove': (str, 70),
        'alg_uit': (str, 70),
        'alg_vrs': (str, 5),
        'bob_kn': (float, 8, 2),
        'bop_0': (float, 7, 1),
        'bop_num': (int, 5),
        'bws_gem': (float, 8, 2),
        'bws_win': (float, 8, 2),
        'bws_zom': (float, 8, 2),
        'dak_een': (str, 2),
        'dak_hel': (float, 9, 2),
        'dak_vla': (float, 9, 2),
        'dak_vlu': (float, 9, 2),
        'drl_cap': (float, 8, 2),
        'drl_coe': (float, 6, 3),
        'dwa_con': (float, 6, 2),
        'dwa_def': (str, 40),
        'dwa_tot': (float, 8, 2),
        'dwa_typ': (int, 2),
        'dwa_u': (float, 5, 1),
        'fac_u': (float, 5, 1),
        'gvh_een': (str, 2),
        'gvh_hel': (float, 9, 2),
        'gvh_vla': (float, 9, 2),
        'gvh_vlu': (float, 9, 2),
        'ide_gb': (str, 3),
        'ide_geb': (str, 3),
        'ide_kn': (str, 10),
        'ide_knp': (str, 10),
        'ide_rec': (str, 4),
        'ini_afv': (float, 8, 4),
        'ini_cod': (int, 2),
        'ini_niv': (float, 8, 2),
        'inv_kn': (float, 4, 2),
        'inw_won': (float, 4, 2),
        'knp_bok': (float, 8, 2),
        'knp_bre': (float, 7, 3),
        'knp_len': (float, 7, 3),
        'knp_vrm': (str, 2),
        'knp_xco': (int, 11),
        'knp_yco': (int, 11),
        'lei_len': (float, 7, 2),
        'lei_typ': (str, 2),
        'loz_con': (float, 8, 2),
        'loz_dag': (str, 7),
        'loz_gem': (float, 9, 2),
        'loz_mnd': (str, 12),
        'mat_sdr': (int, 3),
        'mvd_niv': (float, 8, 2),
        'mvd_sch': (str, 2),
        'niv_0': (float, 8, 2),
        'nsh_frt': (int, 2),
        'nsh_frv': (float, 9, 5),
        'nsh_upt': (int, 2),
        'nsh_upn': (str, 40),
        'num_mvb': (int, 2),
        'onv_een': (str, 2),
        'onv_hel': (float, 9, 2),
        'onv_vla': (float, 9, 2),
        'onv_vlu': (float, 9, 2),
        'ovh_een': (str, 2),
        'ovh_hel': (float, 9, 2),
        'ovh_vla': (float, 9, 2),
        'ovh_vlu': (float, 9, 2),
        'ovs_bre': (float, 7, 3),
        'ovs_coe': (float, 6, 3),
        'ovs_niv': (float, 8, 2),
        'pmp_af': (float, 8, 2),
        'pmp_an': (float, 8, 2),
        'pmp_com': (int, 3),
        'pmp_pc': (float, 8, 2),
        'pro_bok': (float, 8, 2),
        'pro_br': (float, 7, 3),
        'pro_bre': (float, 7, 3),
        'pro_com': (int, 3),
        'pro_hgt': (float, 7, 3),
        'pro_hs': (float, 7, 3),
        'pro_knw': (float, 5, 2),
        'pro_mat': (str, 2),
        'pro_no': (float, 7, 3),
        'pro_num': (str, 3),
        'pro_nv': (float, 8, 3),
        'pro_vrm': (str, 2),
        'qdh_niv': (float, 8, 2),
        'qdh_num': (str, 2),
        'rel_af': (float, 8, 2),
        'rel_an': (float, 8, 2),
        'str_rch': (str, 2),
        'uit_kn': (float, 4, 2),
        'wos_opp': (int, 6),
        }
    fields = {}
    field_names = []
    pattern_head_length = 3

    pattern = None  # overwritten in initPatternFromFields
    ide_knp = ''

    def parseSufHydLine(self, persid):
        match = self.pattern.match(persid + " " * 700)
        if match:
            self.fields = match.groupdict()
            self.translateFields()
        else:
            raise RuntimeError('SUFHYD data does not match pattern')

    @classmethod
    def greenBookDef(cls):
        """returns list of fields, as of green book definition

        a field definition is a string, holding name, type and from/to
        positions
        """

        base = 1
        result = []
        for key in cls.field_names:
            if isSufHydKey(key):
                definition = cls.getType(key)
                if definition[0] is str:
                    letter = 'A'
                else:
                    letter = 'N'
                if definition[0] is float:
                    format = '%d.%d' % (definition[1], definition[2])
                else:
                    format = '%d' % (definition[1])
                result.append("%s | %s %s | %d-%d" % (key, letter, format, base, base + definition[1] - 1))
                base += definition[1]
            else:
                base += len(key)
        return result

    def __init__(self, source=None, persid=None):
        self.source = source

        self.kn1_xco_m = self.kn2_xco_m = self.knp_xco_m = 0.0
        self.kn1_yco_m = self.kn2_yco_m = self.knp_yco_m = 0.0

        self.python__class__name = self.__class__.__name__
        if source is None and persid is None:
            return
        if self.source == 'SUFHYD':
            self.parseSufHydLine(persid)
            self.objectid = 0
            self.fid = 0
            self.opmerking = ''
            self.gml__id = uuid.uuid4()
        elif self.source == 'GML':
            persid = persid.strip()
            log.debug("check that persid contains fme:self.python__class__name - #124")
            expect_element = "fme:%s" % self.python__class__name
            second_element_pos = persid.find('<', 1)
            space_pos = persid.find(' ', second_element_pos)
            element_name = persid[second_element_pos:space_pos][1:]
            if not element_name.startswith(expect_element):
                log.warn("resulting class name %s does not match declared fme:%s from input" % (expect_element, element_name, ))
            self.fields = {}
            for field in [i for i in self.field_names if isSufHydKey(i)]:
                pattern = r'.*<fme:%s>(.*?)</fme:' % field
                m = re.match(pattern, persid, re.S + re.I)
                if m:
                    self.fields[field.lower()] = m.group(1)
            self.translateFields()
            pass
        pass

    @classmethod
    def shortSufHydKey(cls, key):
        if not isinstance(key, types.StringTypes):
            return None
        key = key.strip()
        for i in [7, -1, -2, -4, ]:
            if key[:i] in cls.types:
                return key[:i]
        return None

    @classmethod
    def getType(cls, key):
        shortKey = cls.shortSufHydKey(key)
        if shortKey is not None:
            definition = cls.types[shortKey]
        else:
            definition = (str, len(key))
        return definition

    def translateFields(self):
        for key in self.fields:
            self.translateField(key)

    def translateField(self, key, override=None):
        'translate the string field (optionally using override value)'

        definition = self.getType(key)

        value = (override or self.fields[key] or '').strip()

        if value:
            try:
                value = definition[0](value)
            except:
                value = ''
        self.__dict__[key] = value

        pass

    def toSufHyd(self):
        repr = []
        for key in self.field_names:
            if isSufHydKey(key):
                definition = self.getType(key)
                if key in self.__dict__ and self.__dict__[key] not in ['', None]:
                    if definition[0] == float:
                        format = '%%(%s) %d.%df' % (key, definition[1], definition[2])
                    else:
                        format = '%%(%s) %ds' % (key, definition[1])
                    repr.append((format % self.__dict__)[-definition[1]:])
                else:
                    repr.append(' ' * definition[1])
            else:
                repr.append(key)
        return ''.join(repr)

    def get_start_pointGeb(self):
        if 'ide_geb' in dir(self):
            geb = self.ide_geb
        elif 'ide_gb1' in dir(self):
            geb = self.ide_gb1
        else:
            geb = ''
        return geb

    def get_start_pointId(self):
        geb = self.get_start_pointGeb()
        glue = (geb and '_' or '')
        try:
            return geb + glue + self.ide_kn1
        except:
            return geb + glue + self.ide_knp

    def get_end_pointId(self):
        if 'ide_kn2' not in self.__dict__:
            return ''
        if 'ide_gb2' in dir(self):
            geb = self.ide_gb2
        elif 'ide_geb' in dir(self):
            geb = self.ide_geb
        else:
            geb = ''
        if geb == '':
            geb = self.get_start_pointGeb()
        glue = (geb and '_' or '')
        return geb + glue + self.ide_kn2

    xsdHeader = """\
<element name="%(__name__)s" type="fme:%(__name__)s" substitutionGroup="gml:_Feature"/>
<complexType name="%(__name__)s">
<complexContent>
<extension base="gml:AbstractFeatureType">
<sequence>
<element name="fid" minOccurs="0" type="integer"/>
<element name="objectid" minOccurs="0" type="integer"/>
<element name="opmerking" minOccurs="0">
<simpleType>
<restriction base="string">
<maxLength value="50"/>
</restriction>
</simpleType>
</element>
"""
    xsdTrailer = """
</sequence>
</extension>
</complexContent>
</complexType>"""

    xmlHeader = """\
<gml:featureMember>
<fme:%(python__class__name)s gml:id="id%(gml__id)s">
<fme:fid>%(fid)s</fme:fid>
<fme:objectid>%(objectid)s</fme:objectid>
<fme:opmerking>%(opmerking)s</fme:opmerking>
"""
    xmlTrailer = """
</fme:%(python__class__name)s>
</gml:featureMember>\
"""

    def toxml(self):
        'returns the xml representation of self as a string'

        elements = self.gmlElements()
        keys = [k for k in self.field_names
                if isSufHydKey(k) and k in elements and not k.endswith('.')]
        return (self.xmlHeader + '\n'.join([elements[key].toxml() for key in keys]) + self.gmlProperties() + self.xmlTrailer) % self.__dict__

    def gmlProperties(self):
        return ''

    @classmethod
    def gmlElement(cls, key):
        return GmlElement(key, *cls.getType(key))

    @classmethod
    def toxsd(cls):
        '''returns the string needed in the xsd for this type

        it includes two xml entities: element, complexType.
        '''

        elements = []
        for key in cls.field_names:
            if isSufHydKey(key) and not key.endswith('.'):
                element = cls.gmlElement(key)
                elements.append(element.toxsd())
        return cls.xsdHeader % {'__name__': cls.__name__} + '\n'.join(elements) + cls.xsdTrailer

    def gmlElements(self):
        'returns a dictionary {key: GmlElement}'

        result = {}
        for key in self.field_names:
            if isSufHydKey(key):
                definition = self.getType(key)
                element = GmlElement(key, *definition)
                element.setValue(self.__dict__.get(key, ''))
                result[key] = element
        return result

    def x(self):
        '''returns the x coordinate of the (first) point of this object or None
        '''
        try:
            return self.knp_xco
        except AttributeError:
            return None

    def y(self):
        '''returns the x coordinate of the (first) point of this object
        '''
        try:
            return self.knp_yco
        except AttributeError:
            return None

    def shift_start_point(self, shift):
        (x, y) = (self.knp_xco, self.knp_yco)
        try:
            dx, dy = shift
        except:
            dx = dy = shift
        self.set_start_point((x + dx, y + dy))

    def set_start_point(self, coords):
        x, y = (coords)
        self.knp_xco = x
        self.knp_yco = y
        self.kn1_xco_m = self.knp_xco_m = x / 1000.0
        self.kn1_yco_m = self.knp_yco_m = y / 1000.0

    def set_end_point(self, coords):
        x, y = (coords)
        self.kn2_xco_m, self.kn2_yco_m = (x / 1000.0, y / 1000.0)

    pass


def initPatternFromFields(cls, field_names=None):
    import re
    pattern_fields = ['^']
    for f in (field_names or cls.field_names):
        if cls.shortSufHydKey(f) is not None:
            pattern_fields.append(r'(?P<%s>.{%s})' % (f, cls.getType(f)[1]))
        else:
            pattern_fields.append(f)
    pattern_head = ''.join(pattern_fields[:cls.pattern_head_length])
    pattern_tail = ''
    pattern_fields_tail_reversed = pattern_fields[cls.pattern_head_length:]
    pattern_fields_tail_reversed.reverse()
    for f in pattern_fields_tail_reversed:
        pattern_tail = "%s(?:%s)?" % (f, pattern_tail)
    cls.pattern = re.compile(pattern_head + pattern_tail + '[ ]*$')


class Vertex(HydroObject):
    '''this is a virtual class

    inherit from here if your type is -in graph terms- a vertex.'''

    # must match up to and including the white space for the
    # non-specified second vertex
    pattern_head_length = 5

    def __init__(self, *args):
        HydroObject.__init__(self, *args)

    def toNxTuple(self):
        """returns a tuple that can be fed to Graph.add_nodes_from

        the fields dictionary is augmented with the numerical coordinates.
        """

        sufhydinfo = self.fields.copy()
        if self.x() is not None and self.y() is not None:
            sufhydinfo['x'] = self.x() / 1000.0
            sufhydinfo['y'] = self.y() / 1000.0
        return (self.get_start_pointId(), sufhydinfo)

    def gmlProperties(self):
        'returns an xml string containing the gml elements for Knoop'

        return '''
<gml:pointProperty>
<gml:Point srsName="EPSG:28992" srsDimension="2">
<gml:pos>%(knp_xco_m)0.3f %(knp_yco_m)0.3f</gml:pos>
</gml:Point>
</gml:pointProperty>'''

    xsdTrailer = '''
<element ref="gml:pointProperty" minOccurs="0"/>
<element ref="gml:multiPointProperty" minOccurs="0"/>''' + HydroObject.xsdTrailer

    pass


class Edge(HydroObject):
    '''this is a virtual class

    inherit from here if your type is -in graph terms- an edge.'''

    def __init__(self, *args):
        HydroObject.__init__(self, *args)

    def toNxTuple(self):
        """returns a tuple that can be fed to Graph.add_edges_from
        """

        return (self.get_start_pointId(), self.get_end_pointId(), self.fields.copy())

    def gmlProperties(self):
        'returns an xml string containing the gml elements for GeslotenLeiding'

        return '''
<gml:curveProperty>
<gml:LineString srsName="EPSG:28992" srsDimension="2">
<gml:posList>%(kn1_xco_m)0.3f %(kn1_yco_m)0.3f %(kn2_xco_m)0.3f %(kn2_yco_m)0.3f</gml:posList>
</gml:LineString>
</gml:curveProperty>'''

    xsdTrailer = '''
<element ref="gml:curveProperty" minOccurs="0"/>
<element ref="gml:multiCurveProperty" minOccurs="0"/>''' + HydroObject.xsdTrailer

    pass


class Knoop(Vertex):
    types = HydroObject.types.copy()
    types.update({
            'afv_hel': (int, 6),
            'afv_vla': (int, 6),
            'afv_vlu': (int, 6),
            })
    field_names = ['ide_rec', 'ide_geb', 'ide_knp', '               ',
                   'knp_xco', 'knp_yco', 'mvd_niv', ' ', 'mvd_sch', 'wos_opp',
                   ' ', 'pro_mat', 'knp_bre', 'knp_len', ' ', 'knp_vrm',
                   'knp_bok', 'afv_hel', 'afv_vla', 'afv_vlu', 'loz_con',
                   'aan_won', 'aan_inw',
                   # orig length = 133
                   'dwa_def',
                   ]

    def translateField(self, key):
        '''coordinate fields knp_xco & knp_yco in Knoop are kept in millimetres

        the extra fields knp_xco_m & knp_yco_m keep the same info in metres
        '''

        value = self.fields[key] or ''
        if (self.source == 'GML' and
            key in ['knp_xco', 'knp_yco'] and
            value != ''):
            if value.find('.') == -1:
                value += '.'
            value += '000'
            value = value[:value.find('.') + 4]
            value = ''.join([ch for ch in value if ch != '.'])

        Vertex.translateField(self, key, value)

        if key in ['knp_xco', 'knp_yco']:
            self.__dict__[key + '_m'] = self.__dict__[key] / 1000.0

    @classmethod
    def gmlElement(self, key):
        result = GmlElement(key, *self.getType(key))
        if key in ['knp_xco', 'knp_yco']:
            result = GmlElement(key, float, 11, 3)
        return result

    def gmlElements(self):
        '''returns a dictionary {key: GmlElement}

        translating the values for coordinates into metres
        '''

        result = Vertex.gmlElements(self)
        for key in ['knp_xco', 'knp_yco']:
            valueString = str(result[key].value)
            valueString = valueString[:-3] + '.' + valueString[-3:]
            result[key].setValue(valueString)
        return result

initPatternFromFields(Knoop)


class End(HydroObject):
    field_names = ['ide_rec']

    def __init__(self, *args):
        if not args:
            args = ["SUFHYD", "*END"]
        HydroObject.__init__(self, *args)

    pass

initPatternFromFields(End)


class GeslotenLeiding(Edge):
    field_names = ['ide_rec', 'ide_geb', 'ide_kn1', 'ide_gb2', 'ide_kn2',
                   'num_mvb', 'bob_kn1', 'bob_kn2', 'lei_len', ' ', 'lei_typ',
                   ' ', 'pro_mat', 'mat_sdr', 'pro_bre', 'pro_hgt',
                   ' ', 'pro_vrm', 'pro_num', ' ', 'afv_een', 'afv_hel',
                   'afv_vla', 'afv_vlu', 'aan_won', 'aan_inw', 'pro_knw',
                   ' ', 'str_rch', 'inv_kn1', 'uit_kn1', 'inv_kn2', 'uit_kn2',
                   ' ', 'qdh_num', 'qdh_niv',
                   # orig length = 157
                   '  ', 'nsh_frt', '   ', 'nsh_frv',
                   ' ', 'dwa_def', ' ', 'nsh_upt', '  ', 'nsh_upn',
                   ]

initPatternFromFields(GeslotenLeiding)


class Gemaal:
    "just to identify <x>_Knoop and <x>_Tak as <x>"
    pass


class Overstort:
    "just to identify <x>_Knoop and <x>_Tak as <x>"
    pass


class AfvoerendOppervlak:
    "just to identify <x>_Knoop and <x>_Tak as <x>"
    pass


class AfvoerendOppervlakMetBijzondereKenmerken:
    "just to identify <x>_Knoop and <x>_Tak as <x>"
    types = HydroObject.types.copy()
    types.update({
            'afv_hel': (int, 4),
            })
    pass


class UitlaatMetKeerklep:
    "just to identify <x>_Knoop and <x>_Tak as <x>"
    pass


class Gemaal_Knoop(Gemaal, Vertex):
    field_names = ['ide_rec', 'ide_gb1', 'ide_kn1', 'ide_gb2', '          ',
                   'num_mvb', ' ', 'qdh_num', 'qdh_niv', 'pmp_com',
                   ]
    # append to field_names enough fields up to 8 pumps.  recognizing
    # 9 pumps would would exceed an internal limit for the re python
    # module and would require calculating the pattern differently
    # than by calling initPatternFromFields.
    for i in range(1, 9):
        for n in ['pmp_pc%d', 'pmp_an%d', 'pmp_af%d', 'rel_an%d', 'rel_af%d', ]:
            field_names.append(n % i)

    def __init__(self, *args):
        Vertex.__init__(self, *args)
        self.kn1_xco_m = self.kn1_yco_m = 0.0
    pass

initPatternFromFields(Gemaal_Knoop)


class Gemaal_Tak(Gemaal, Edge):
    field_names = ['ide_rec', 'ide_gb1', 'ide_kn1', 'ide_gb2',
                   'ide_kn2', 'num_mvb', ' ', 'qdh_num', 'qdh_niv', 'pmp_com',
                   ]
    # append to field_names enough fields up to 8 pumps.  recognizing
    # 9 pumps would would exceed an internal limit for the re python
    # module and would require calculating the pattern differently
    # than by calling initPatternFromFields.
    for i in range(1, 9):
        for n in ['pmp_pc%d', 'pmp_an%d', 'pmp_af%d', 'rel_an%d', 'rel_af%d', ]:
            field_names.append(n % i)

    def __init__(self, *args):
        Edge.__init__(self, *args)
        self.kn1_xco_m = self.kn1_yco_m = self.kn2_xco_m = self.kn2_yco_m = 0.0
    pass

initPatternFromFields(Gemaal_Tak)


class AfvoerendOppervlak_Knoop(AfvoerendOppervlak, Vertex):
    field_names = ['ide_rec', 'ide_geb', 'ide_kn1', 'ide_gb2', '          ',
                   'num_mvb', ' ', 'gvh_een', 'gvh_hel', 'gvh_vla', 'gvh_vlu',
                   ' ', 'ovh_een', 'ovh_hel', 'ovh_vla', 'ovh_vlu',
                   ' ', 'dak_een', 'dak_hel', 'dak_vla', 'dak_vlu',
                   ' ', 'onv_een', 'onv_hel', 'onv_vla', 'onv_vlu',
                   ]
    pass

initPatternFromFields(AfvoerendOppervlak_Knoop)


class AfvoerendOppervlak_Tak(AfvoerendOppervlak, Edge):
    field_names = ['ide_rec', 'ide_geb', 'ide_kn1', 'ide_gb2', 'ide_kn2',
                   'num_mvb', ' ', 'gvh_een', 'gvh_hel', 'gvh_vla', 'gvh_vlu',
                   ' ', 'ovh_een', 'ovh_hel', 'ovh_vla', 'ovh_vlu',
                   ' ', 'dak_een', 'dak_hel', 'dak_vla', 'dak_vlu',
                   ' ', 'onv_een', 'onv_hel', 'onv_vla', 'onv_vlu',
                   ]
    pass

initPatternFromFields(AfvoerendOppervlak_Tak)


class AfvoerendOppervlakMetBijzondereKenmerken_Knoop(AfvoerendOppervlakMetBijzondereKenmerken, Vertex):
    field_names = ['ide_rec', 'ide_geb', 'ide_kn1', 'ide_gb2', '          ',
                   'num_mvb', ' ', 'afv_een', ' ', 'afv_opp', 'afv_brg', 'afv_vdp',
                   'afv_ifx', 'afv_ifn', 'afv_ifa', 'afv_ifh',
                   'afv_afs', 'afv_len', 'afv_hel', 'afv_ruw',
                   'afv_ind', 'afv_inr', ' ', 'afv_ide', ' ', 'afv_nam',
                   ]
    pass

initPatternFromFields(AfvoerendOppervlakMetBijzondereKenmerken_Knoop)


class AfvoerendOppervlakMetBijzondereKenmerken_Tak(AfvoerendOppervlakMetBijzondereKenmerken, Edge):
    field_names = ['ide_rec', 'ide_geb', 'ide_kn1', 'ide_gb2', 'ide_kn2',
                   'num_mvb', ' ', 'afv_een', ' ', 'afv_opp', 'afv_brg', 'afv_vdp',
                   'afv_ifx', 'afv_ifn', 'afv_ifa', 'afv_ifh',
                   'afv_afs', 'afv_len', 'afv_hel', 'afv_ruw',
                   'afv_ind', 'afv_inr', ' ', 'afv_ide', ' ', 'afv_nam',
                   ]
    pass

initPatternFromFields(AfvoerendOppervlakMetBijzondereKenmerken_Tak)


class BijzonderLeidingprofiel(HydroObject):
    field_names = ['ide_rec', 'pro_num', 'pro_com', ]
    for i in range(50):
        field_names.extend([k % i for k in ['pro_nv_%03d', 'pro_no_%03d', 'pro_hs_%03d', 'pro_br_%03d', ]])

    def parseSufHydLine(self, persid):
        lead = self.field_names[:4]
        persid = persid + " " * 30
        self.fields = {}
        initPatternFromFields(BijzonderLeidingprofiel, lead)
        match = self.pattern.match(persid[:10])
        self.fields.update(match.groupdict())
        persid = persid[10:]
        i = 0
        while True:
            initPatternFromFields(BijzonderLeidingprofiel,
                                  [k % i for k in ['pro_nv_%03d', 'pro_no_%03d', 'pro_hs_%03d', 'pro_br_%03d', ]])
            match = self.pattern.match(persid[:29])
            if not match:
                break

            self.fields.update(match.groupdict())
            i += 1
            persid = persid[29:]
            if not persid.strip():
                break
        else:
            raise RuntimeError('SUFHYD data does not match pattern')
        self.translateFields()

    def __init__(self, *args):
        HydroObject.__init__(self, *args)
        try:
            ## if any profile point is empty, shift fields to the left
            ## TODO 2069
            while self.pro_br_000 == self.pro_no_000 == self.pro_nv_000 == self.pro_hs_000 == '':
                for i, j in zip(range(0, 500), range(1, 501)):
                    if not hasattr(self, "pro_br_%03d" % j):
                        delattr(self, "pro_br_%03d" % i)
                        delattr(self, "pro_no_%03d" % i)
                        delattr(self, "pro_nv_%03d" % i)
                        delattr(self, "pro_hs_%03d" % i)
                        del self.fields["pro_br_%03d" % i]
                        del self.fields["pro_no_%03d" % i]
                        del self.fields["pro_nv_%03d" % i]
                        del self.fields["pro_hs_%03d" % i]
                        break
                    setattr(self, "pro_br_%03d" % i, getattr(self, "pro_br_%03d" % j))
                    setattr(self, "pro_no_%03d" % i, getattr(self, "pro_no_%03d" % j))
                    setattr(self, "pro_nv_%03d" % i, getattr(self, "pro_nv_%03d" % j))
                    setattr(self, "pro_hs_%03d" % i, getattr(self, "pro_hs_%03d" % j))
                    self.fields["pro_br_%03d" % i] = self.fields["pro_br_%03d" % j]
                    self.fields["pro_no_%03d" % i] = self.fields["pro_no_%03d" % j]
                    self.fields["pro_nv_%03d" % i] = self.fields["pro_nv_%03d" % j]
                    self.fields["pro_hs_%03d" % i] = self.fields["pro_hs_%03d" % j]
        except AttributeError:
            ## empty profile, created from empty fake data.
            return
    pass


class BijzondereInloopparameters(HydroObject):
    field_names = ['ide_rec', ' ', 'afv_top', ' ', 'afv_tas',
                   ' ', 'afv_brg', ' ', 'afv_vdp',
                   'afv_ifx', 'afv_ifn', 'afv_ifa', 'afv_ifh',
                   'afv_afs',
                   # orig length = 43
                   'afv_ind', 'afv_inr',
                   ]
    pass

initPatternFromFields(BijzondereInloopparameters)


class InitieleLeidingWaarden(Edge):
    field_names = ['ide_rec', 'ide_gb1', 'ide_kn1',
                   'ide_gb2', 'ide_kn2', 'num_mvb',
                   'ini_afv', 'ini_cod', 'ini_niv',
                   ]

    pass

initPatternFromFields(InitieleLeidingWaarden)


class Doorlaat(Edge):
    field_names = ['ide_rec', 'ide_gb1', 'ide_kn1',
                   'ide_gb2', 'ide_kn2', 'num_mvb', 'pro_bre', 'pro_hgt',
                   ' ', 'pro_vrm', 'pro_bok', 'drl_coe', 'drl_cap',
                   ' ', 'str_rch', ' ', 'qdh_num', 'qdh_niv',
                   ]

    def __init__(self, *args):
        Edge.__init__(self, *args)
        self.kn1_xco_m = self.kn1_yco_m = self.kn2_xco_m = self.kn2_yco_m = 0.0
    pass

initPatternFromFields(Doorlaat)


class DWAVerloopPerInwoner(HydroObject):
    field_names = ['ide_rec', ' ', 'inw_won', 'dwa_con', 'dwa_u00', 'dwa_u01',
                   'dwa_u02', 'dwa_u03', 'dwa_u04', 'dwa_u05', 'dwa_u06',
                   'dwa_u07', 'dwa_u08', 'dwa_u09', 'dwa_u10', 'dwa_u11',
                   'dwa_u12', 'dwa_u13', 'dwa_u14', 'dwa_u15', 'dwa_u16',
                   'dwa_u17', 'dwa_u18', 'dwa_u19', 'dwa_u20', 'dwa_u21',
                   'dwa_u22', 'dwa_u23',
                   # orig length = 135
                   '  ', 'dwa_typ', '  ', 'dwa_tot', '  ', 'dwa_def',
                   ]

    pass

initPatternFromFields(DWAVerloopPerInwoner)


class DWALozingMetDagcyclus(Vertex):
    field_names = ['ide_rec', 'ide_geb', 'ide_knp', 'ide_gb2', '             ',
                   'loz_mnd', ' ', 'loz_dag', 'loz_gem', 'fac_u00', 'fac_u01',
                   'fac_u02', 'fac_u03', 'fac_u04', 'fac_u05', 'fac_u06',
                   'fac_u07', 'fac_u08', 'fac_u09', 'fac_u10', 'fac_u11',
                   'fac_u12', 'fac_u13', 'fac_u14', 'fac_u15', 'fac_u16',
                   'fac_u17', 'fac_u18', 'fac_u19', 'fac_u20', 'fac_u21',
                   'fac_u22', 'fac_u23',
                   ]
    pass

initPatternFromFields(DWALozingMetDagcyclus)


class BergendOppervlakKnoop(Vertex):
    field_names = ['ide_rec', 'ide_geb', 'ide_knp', 'ide_gb2', '            ',
                   'bop_num', 'niv_001', 'bop_001', 'niv_002', 'bop_002',
                   'niv_003', 'bop_003', 'niv_004', 'bop_004',
                   ]
    pass

initPatternFromFields(BergendOppervlakKnoop)


class Overstort_Knoop(Overstort, Vertex):
    field_names = ['ide_rec', 'ide_gb1', 'ide_kn1', 'ide_gb2', '          ',
                   'num_mvb', 'ovs_bre', 'ovs_niv', 'ovs_coe',
                   '  ', 'str_rch', 'bws_gem', 'bws_zom', 'bws_win',
                   ' ', 'qdh_num', 'qdh_niv',
                   ]
    pass

initPatternFromFields(Overstort_Knoop)


class Overstort_Tak(Overstort, Edge):
    field_names = ['ide_rec', 'ide_gb1', 'ide_kn1', 'ide_gb2',
                   'ide_kn2', 'num_mvb', 'ovs_bre', 'ovs_niv', 'ovs_coe',
                   '  ', 'str_rch', 'bws_gem', 'bws_zom', 'bws_win',
                   ' ', 'qdh_num', 'qdh_niv',
                   ]
    pass

initPatternFromFields(Overstort_Tak)


class UitlaatMetKeerklep_Knoop(UitlaatMetKeerklep, Vertex):
    field_names = ['ide_rec', 'ide_gb1', 'ide_kn1', 'ide_gb2', '          ',
                   'num_mvb', 'bws_gem', 'bws_zom', 'bws_win',
                   ]
    pass

initPatternFromFields(UitlaatMetKeerklep_Knoop)


class UitlaatMetKeerklep_Tak(UitlaatMetKeerklep, Edge):
    field_names = ['ide_rec', 'ide_gb1', 'ide_kn1', 'ide_gb2',
                   'ide_kn2', 'num_mvb', 'bws_gem', 'bws_zom', 'bws_win',
                   ]
    pass

initPatternFromFields(UitlaatMetKeerklep_Tak)


class AlgemeneInformatie(HydroObject):
    field_names = ['*AL1 ', 'alg_vrs', ' ', 'alg_dat', '\n',
                   '*AL2 ', 'alg_opd', '\n',
                   '*AL3 ', 'alg_uit', '\n',
                   '*AL4 ', 'alg_oms', '\n',
                   '*AL5 ', 'alg_ove', '\n',
                   ]

    pattern = re.compile(r'^\*AL(?:1 ?(?P<alg_vrs>.{5})?.?(?P<alg_dat>.{8})?)?(?:2 ?(?P<alg_opd>.{70})?)?(?:3 (?P<alg_uit>.{70}))?(?:4 (?P<alg_oms>.{70}))?(?:5 (?P<alg_ove>.{70}))?')
    pass

xsdFileHeader = """\
<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://www.w3.org/2001/XMLSchema" xmlns:gml="http://www.opengis.net/gml" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:fme="http://www.safe.com/gml/fme" targetNamespace="http://www.safe.com/gml/fme" elementFormDefault="qualified">
<import namespace="http://www.opengis.net/gml" schemaLocation="http://schemas.opengis.net/gml/3.1.1/base/gml.xsd"/>
"""

xsdFileTrailer = """\
</schema>
"""

xmlFileHeader = """\
<?xml version="1.0" encoding="UTF-8"?>
<gml:FeatureCollection xmlns:gml="http://www.opengis.net/gml" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:fme="http://www.safe.com/gml/fme" xsi:schemaLocation="http://www.safe.com/gml/fme %s.xsd">
"""

xmlFileTrailer = """\
</gml:FeatureCollection>
"""


class HydroObjectFactory:
    WhichHydroObject = {
        '*KNP': (Knoop,),
        '*LEI': (GeslotenLeiding, ),
        '*BOP': (BergendOppervlakKnoop,),
        '*GEM': (Gemaal_Knoop, Gemaal_Tak, ),
        '*AFV': (AfvoerendOppervlak_Knoop, AfvoerendOppervlak_Tak, ),
        '*DRL': (Doorlaat,),
        '*DWA': (DWAVerloopPerInwoner,),
        '*LZD': (DWALozingMetDagcyclus,),
        '*OVS': (Overstort_Knoop, Overstort_Tak, ),
        '*UIT': (UitlaatMetKeerklep_Knoop, UitlaatMetKeerklep_Tak, ),
        '*AFK': (AfvoerendOppervlakMetBijzondereKenmerken_Knoop, AfvoerendOppervlakMetBijzondereKenmerken_Tak, ),
        '*PRO': (BijzonderLeidingprofiel,),
        '*INL': (BijzondereInloopparameters,),
        '*INI': (InitieleLeidingWaarden,),
        '*AL1': (AlgemeneInformatie,),
        '*AL2': (AlgemeneInformatie,),
        '*AL3': (AlgemeneInformatie,),
        '*AL4': (AlgemeneInformatie,),
        '*AL5': (AlgemeneInformatie,),
        '*END': (End,),
        }

    get_ide = re.compile(r'.*?<fme:IDE_REC>(....)</fme:IDE_REC>', re.S + re.I)
    has_second_node = re.compile(r'.*?<fme:IDE_kn2>[^<]+</fme:IDE_kn2>', re.S + re.I)

    @classmethod
    def printDef(cls, persid, variant=0, trim_at=10):
        """prints the definition of the object in readable format

        >>> HydroObjectFactory.printDef('*INI', trim_at=140)
        ide_rec | A 4 | 1-4
        ide_gb1 | A 3 | 5-7
        ide_kn1 | A 10 | 8-17
        ide_gb2 | A 3 | 18-20
        ide_kn2 | A 10 | 21-30
        num_mvb | N 2 | 31-32
        ini_afv | N 8.4 | 33-40
        ini_cod | N 2 | 41-42
        ini_niv | N 8.2 | 43-50

        >>> HydroObjectFactory.printDef('*KNP', trim_at=200)
        ide_rec | A 4 | 1-4
        ide_geb | A 3 | 5-7
        ide_knp | A 10 | 8-17
        knp_xco | N 11 | 33-43
        knp_yco | N 11 | 44-54
        mvd_niv | N 8.2 | 55-62
        mvd_sch | A 2 | 64-65
        wos_opp | N 6 | 66-71
        pro_mat | A 2 | 73-74
        knp_bre | N 7.3 | 75-81
        knp_len | N 7.3 | 82-88
        knp_vrm | A 2 | 90-91
        knp_bok | N 8.2 | 92-99
        afv_hel | N 6 | 100-105
        afv_vla | N 6 | 106-111
        afv_vlu | N 6 | 112-117
        loz_con | N 8.2 | 118-125
        aan_won | N 4 | 126-129
        aan_inw | N 4 | 130-133
        dwa_def | A 40 | 134-173

        >>> HydroObjectFactory.printDef('*DWA', trim_at=200)
        ide_rec | A 4 | 1-4
        inw_won | N 4.2 | 6-9
        dwa_con | N 6.2 | 10-15
        dwa_u00 | N 5.1 | 16-20
        dwa_u01 | N 5.1 | 21-25
        dwa_u02 | N 5.1 | 26-30
        dwa_u03 | N 5.1 | 31-35
        dwa_u04 | N 5.1 | 36-40
        dwa_u05 | N 5.1 | 41-45
        dwa_u06 | N 5.1 | 46-50
        dwa_u07 | N 5.1 | 51-55
        dwa_u08 | N 5.1 | 56-60
        dwa_u09 | N 5.1 | 61-65
        dwa_u10 | N 5.1 | 66-70
        dwa_u11 | N 5.1 | 71-75
        dwa_u12 | N 5.1 | 76-80
        dwa_u13 | N 5.1 | 81-85
        dwa_u14 | N 5.1 | 86-90
        dwa_u15 | N 5.1 | 91-95
        dwa_u16 | N 5.1 | 96-100
        dwa_u17 | N 5.1 | 101-105
        dwa_u18 | N 5.1 | 106-110
        dwa_u19 | N 5.1 | 111-115
        dwa_u20 | N 5.1 | 116-120
        dwa_u21 | N 5.1 | 121-125
        dwa_u22 | N 5.1 | 126-130
        dwa_u23 | N 5.1 | 131-135
        dwa_typ | N 2 | 138-139
        dwa_tot | N 8.2 | 142-149
        dwa_def | A 40 | 152-191

        >>> HydroObjectFactory.printDef('*PRO', trim_at=3)
        ide_rec | A 4 | 1-4
        pro_num | A 3 | 5-7
        pro_com | N 3 | 8-10

        >>> HydroObjectFactory.printDef('*LEI', trim_at=200)
        ide_rec | A 4 | 1-4
        ide_geb | A 3 | 5-7
        ide_kn1 | A 10 | 8-17
        ide_gb2 | A 3 | 18-20
        ide_kn2 | A 10 | 21-30
        num_mvb | N 2 | 31-32
        bob_kn1 | N 8.2 | 33-40
        bob_kn2 | N 8.2 | 41-48
        lei_len | N 7.2 | 49-55
        lei_typ | A 2 | 57-58
        pro_mat | A 2 | 60-61
        mat_sdr | N 3 | 62-64
        pro_bre | N 7.3 | 65-71
        pro_hgt | N 7.3 | 72-78
        pro_vrm | A 2 | 80-81
        pro_num | A 3 | 82-84
        afv_een | A 2 | 86-87
        afv_hel | N 9.2 | 88-96
        afv_vla | N 9.2 | 97-105
        afv_vlu | N 9.2 | 106-114
        aan_won | N 4 | 115-118
        aan_inw | N 4 | 119-122
        pro_knw | N 5.2 | 123-127
        str_rch | A 2 | 129-130
        inv_kn1 | N 4.2 | 131-134
        uit_kn1 | N 4.2 | 135-138
        inv_kn2 | N 4.2 | 139-142
        uit_kn2 | N 4.2 | 143-146
        qdh_num | A 2 | 148-149
        qdh_niv | N 8.2 | 150-157
        nsh_frt | N 2 | 160-161
        nsh_frv | N 9.5 | 165-173
        dwa_def | A 40 | 175-214
        nsh_upt | N 2 | 216-217
        nsh_upn | A 40 | 220-259
        >>>

        >>> HydroObjectFactory.printDef('*INL', trim_at=200)
        ide_rec | A 4 | 1-4
        afv_top | A 2 | 6-7
        afv_tas | A 2 | 9-10
        afv_brg | N 4.1 | 12-15
        afv_vdp | N 4.1 | 17-20
        afv_ifx | N 4 | 21-24
        afv_ifn | N 4 | 25-28
        afv_ifa | N 5.2 | 29-33
        afv_ifh | N 5.2 | 34-38
        afv_afs | N 5.3 | 39-43
        afv_ind | N 3 | 44-46
        afv_inr | N 3 | 47-49

        >>> HydroObjectFactory.printDef('*AFV', trim_at=200)
        ide_rec | A 4 | 1-4
        ide_geb | A 3 | 5-7
        ide_kn1 | A 10 | 8-17
        ide_gb2 | A 3 | 18-20
        num_mvb | N 2 | 31-32
        gvh_een | A 2 | 34-35
        gvh_hel | N 9.2 | 36-44
        gvh_vla | N 9.2 | 45-53
        gvh_vlu | N 9.2 | 54-62
        ovh_een | A 2 | 64-65
        ovh_hel | N 9.2 | 66-74
        ovh_vla | N 9.2 | 75-83
        ovh_vlu | N 9.2 | 84-92
        dak_een | A 2 | 94-95
        dak_hel | N 9.2 | 96-104
        dak_vla | N 9.2 | 105-113
        dak_vlu | N 9.2 | 114-122
        onv_een | A 2 | 124-125
        onv_hel | N 9.2 | 126-134
        onv_vla | N 9.2 | 135-143
        onv_vlu | N 9.2 | 144-152

        """

        class_name = persid[:4]
        try:
            that_class = cls.WhichHydroObject[class_name][variant]
        except KeyError:
            print "no class for such name (%s)" % class_name
            return
        print '\n'.join(that_class.greenBookDef()[:trim_at])

    @classmethod
    def hydroObjectFromGML(cls, persid, strict=False):
        """parses persid and returns one object

        if parsid is not parseable and strict is True: raise an exception
        """
        try:
            match = cls.get_ide.match(persid)
            ide_rec = match.group(1)
            resultClassList = cls.WhichHydroObject[ide_rec]
            if len(resultClassList) == 2:
                # choose among _Knoop/_Tak variant of class
                if cls.has_second_node.match(persid):
                    resultClass = resultClassList[1]
                else:
                    resultClass = resultClassList[0]
            elif len(resultClassList) != 1:
                # choose the most generic one (only needed for
                # GeslotenLeiding so let's use a brutal and non
                # educated guess)
                resultClass = resultClassList[2]
            else:
                resultClass = resultClassList[0]
            return resultClass("GML", persid)
        except AttributeError:
            raise  # TODO: what exceptions do we hide behind the fallback?
            pass
        raise RuntimeError('GML data does not match any pattern ("%s")' % persid)

    @classmethod
    def hydroObjectListFromGML(cls, input, strict=False):
        """transforms xml input into sequence of objects

        splits input in gml:featureMember elements.
        parses each element singularly.
        returns list of results.
        if input contains non parseable parts:
          if strict is True: raise an exception
          else: ignore that part.
        """

        featureElement_re = re.compile(
            r'.*?(<gml:featureMember>.*?</gml:featureMember>)',
            re.S | re.I)

        result = []
        offset = 0
        m = featureElement_re.match(input)

        while m:
            try:
                try:
                    obj = cls.hydroObjectFromGML(m.group(1), strict)
                    result.append(obj)
                except AttributeError:
                    pass
                offset = m.span()[1]
                m = featureElement_re.match(input, offset)
            except RuntimeError, e:
                print e

        return result

    @classmethod
    def hydroObjectFromSUFHYD(cls, persid, strict=True):
        '''create object from string.

        if persid is not parseable:
          if strict is True: raise an exception
          else: return None
        '''
        tryingClass = None
        try:
            ide_rec = persid[:4]
            for resultClass in cls.WhichHydroObject[ide_rec]:
                try:
                    tryingClass = resultClass
                    return resultClass("SUFHYD", persid)
                except RuntimeError:
                    pass
        except (KeyError, TypeError):
            pass

        if not tryingClass:
            log.warn('%s' % persid)
        else:
            log.warn('%s' % fieldwise(tryingClass(), persid))
        if strict is True:
            raise RuntimeError('SUFHYD data does not match any pattern ("%s")' % persid)

    @classmethod
    def hydroObjectListFromSUFHYD(cls, input, strict=False):
        '''

        if input contains non parseable parts:
          if strict is True: raise an exception
          else: ignore those parts.
        '''

        log.info('logging non parsed input as WARNING')
        result = [cls.hydroObjectFromSUFHYD(i, strict) for i in re.split('[\n\r]+', input) if i]
        result = [i for i in result if i]
        log.info('end of non parsed input')

        ai_list = [i for i in result if i.__class__ == AlgemeneInformatie]
        if ai_list:
            log.info('collapsing AlgemeneInformatie to one object')
            ai = cls.hydroObjectFromSUFHYD("*AL1")
            for key in AlgemeneInformatie.field_names:
                if not isSufHydKey(key):
                    continue
                for item in ai_list:
                    value = getattr(item, key, None)
                    if value:
                        setattr(ai, key, value)
            result = [ai] + [i for i in result if i.__class__ != AlgemeneInformatie]

        vertices = [i for i in result if isinstance(i, Knoop)]
        by_coords = {}
        for i in vertices:
            coords = (i.x(), i.y())
            by_coords.setdefault(coords, [])
            by_coords[coords].append(i)

        if (None, None) in by_coords:
            for i in by_coords.get((None, None), []):
                log.warning("vertex object %s %s has no coordinates" % (i.ide_rec, i.get_start_pointId()))
            del by_coords[(None, None)]

        crowded_points = [k for (k, v) in by_coords.items() if len(v) > 1]
        if crowded_points:
            log.warning("found coinciding points")
        for P in crowded_points:
            objs = by_coords[P]
            log.info("coinciding objects at %s" % (P,))
            for shift, i in enumerate(objs):
                i.shift_start_point(shift * 1000)
                log.info("%s %s was moved from %s to %s" % (i.ide_rec, i.get_start_pointId(), P, (i.knp_xco, i.knp_yco)))

        edges = [i for i in result if isinstance(i, Edge)]
        for i in edges:
            if i.get_start_pointId() == i.get_end_pointId():
                log.warning("edge object %s goes from and to %s" % (i.ide_rec, i.get_end_pointId()))
        return result

    @classmethod
    def propagateGeometries(cls, obj_list, strict=False):
        '''propagate geometric properties from nodes to arcs

        it does so by creating a dictionary of nodes (pairs of
        coordinates) from all node elements in the obj_list.  then
        scans the obj_list again and updates each object with the
        coordinates of the node the objects refers to.

        if strict is True: raise an exception in case of errors
        '''

        log.info('logging removed objects as WARNING')
        nodes = {}
        for obj in obj_list:
            if isinstance(obj, Knoop):
                nodes[obj.get_start_pointId()] = (obj.x(), obj.y())
        for obj in list(obj_list):
            if isinstance(obj, Vertex) and not isinstance(obj, Knoop):
                try:
                    obj.set_start_point(nodes[obj.get_start_pointId()])
                except KeyError, e:
                    log.warn('%(ide_rec)s:%(ide_kn1)s' % obj.__dict__)
                    if strict is True:
                        raise RuntimeError('could not find point %s' % e)
                    obj_list.remove(obj)

        for obj in list(obj_list):
            if isinstance(obj, Edge):
                try:
                    obj.set_start_point(nodes[obj.get_start_pointId()])
                    obj.set_end_point(nodes[obj.get_end_pointId()])
                except KeyError, e:
                    d = {'id': obj.ide_rec,
                         'sp': obj.get_start_pointId(),
                         'ep': obj.get_end_pointId(),
                         'key': e,
                         }
                    log.warn("%(id)s:%(sp)s->%(ep)s - key %(key)s not found" % d)
                    if strict is True:
                        raise RuntimeError('could not find point %s' % e)
                    obj_list.remove(obj)
        log.info('end of removed objects')
        log.info('surviving objects: %d' % len(obj_list))
        return True

    @classmethod
    def writeGml(cls, obj_list, xsd_output, xml_output, basename='sample', progress=None):

        # first the xsd...
        xsd_output.write(xsdFileHeader)

        used_classes = dict([(obj.__class__, None) for obj in obj_list]).keys()
        for cls in used_classes:
            xsd_output.write(cls.toxsd() + '\n')

        xsd_output.write(xsdFileTrailer)

        # then the xml...
        xml_output.write(xmlFileHeader % basename)

        x_coords = [obj.x() / 1000.0 for obj in obj_list if obj.x()]
        y_coords = [obj.y() / 1000.0 for obj in obj_list if obj.y()]
        xmin = min(x_coords + [99999999])
        xmax = max(x_coords + [0])
        ymin = min(y_coords + [99999999])
        ymax = max(y_coords + [0])

        xml_output.write('''\
<gml:boundedBy>
<gml:Envelope srsName="EPSG:28992" srsDimension="2">
<gml:lowerCorner>%0.3f %0.3f</gml:lowerCorner>
<gml:upperCorner>%0.3f %0.3f</gml:upperCorner>
</gml:Envelope>
</gml:boundedBy>
'''
                         % (xmin, ymin, xmax, ymax))

        for obj in obj_list:
            xml_output.write(obj.toxml() + '\n')
            if progress:
                progress.write('inc 1\n')

        xml_output.write(xmlFileTrailer)
        pass

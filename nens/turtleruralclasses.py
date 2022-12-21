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
#* $Id: turtleurbanclasses.py 22194 2011-06-24 07:03:52Z mario.frasca $
#*
#* initial programmer :  Mario Frasca
#* initial date :        20110914
#**********************************************************************
""" for a sample usage, check turtle-rural/sobek_to_gml.py """


__revision__ = "$Rev: 22194 $"[6:-2]

import logging
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
import sobek
import os
import uuid
from xml.dom.minidom import Document


class Base(object):
    element_name = "unknown"
    NAME_TO_CLASS = {}
    MAIN_TAG = {'CONTROL.DEF': ('CNTL', {}),
                'PROFILE.DAT': ('CRSN', {}),
                'STRUCT.DAT': ('STRU', {'CONTROL.DEF': 'cj',
                                        'STRUCT.DEF': 'dd'}),
                'LATERAL.DAT': (None, {}),
                'STRUCT.DEF': ('STDS', {}),
                'FRICTION.DAT': ('STFR', {'STRUCT.DEF': 'ci'}),
                'INITIAL.DAT': ('FLIN', {}),
                'PROFILE.DEF': ('CRDS', {}),
                'BOUNDARY.DAT': (None, {}),
                'NETWORK.NTW': (None, {})}
    ## first element is the entry point.  the constructor will look
    ## for the object in the entry point and from there navigate the
    ## forward and backward links
    fields_used = set()
    sources = []
    automatic_fields = set(["nm", "id"])
    field_def = [  # sobek name, internal name, xsd type.
        ("aw", "aperture_width", "xs:decimal"),
        ("bl", "bottom_level", "xs:decimal"),
        ("bs", "slope", "xs:decimal"),
        ("bw", "bottom_width", "xs:decimal"),
        ("ca", "controller_active", "xs:integer"),
        ("ce", "discharge_coefficient", "xs:decimal"),
        ("ci", "struct_def_id", "xs:NCName"),
        ("cj", "control_def_id", "xs:NCName"),
        ("cl", "constant_crest_level", "xs:decimal"),
        ("cw", "constant_crest_width", "xs:decimal"),
        ("dd", "struct_def_id", "xs:NCName"),
        ("di", "profile_def_id", "xs:NCName"),
        ("dl", "length", "xs:decimal"),
        ("dn", "control_direction", "xs:integer"),
        ("gl", "ground_layer_depth", "xs:integer"),
        ("gu", "ground_layer_used", "xs:integer"),
        ("id", None, "xs:NMTOKEN"),
        ("lb", "bend_loss", "xs:decimal"),
        ("li", "inlet_loss", "xs:decimal"),
        ("ll", "bed_level_left", "xs:decimal"),
        ("lo", "outlet_loss", "xs:decimal"),
        ("mf", "friction_type", "xs:integer"),
        ("nm", "name", "xs:NCName"),
        ("ov", "initial_opening", "xs:decimal"),
        ("pw", "tot_pillar_width", "xs:decimal"),
        ("rd", "radius", "xs:decimal"),
        ("rl", "bottom_level", "xs:decimal"),
        ("rs", "field_level", "xs:decimal"),
        ("rt", "flow_direction", "xs:integer"),
        ("sc", "lateral_contraction", "xs:integer"),
        ("si", "profile_def_id", "xs:NCName"),
        ("st", "storage_type", "xs:integer"),
        ("sv", "contraction", "xs:decimal"),
        ("tb", "bridge_type", "xs:integer"),
        ("tc", "type_culvert", "xs:integer"),
        ("ty", "structure_type", "xs:integer"),
        ("vf", "pillar_form_factor", "xs:decimal"),
        ("wm", "main_water_width", "xs:decimal"),
        ("x", None, "xs:decimal"),
        ("z", None, "xs:decimal"),
        (None, "capacity", "xs:decimal"),
        (None, "winter_start", "xs:string"),
        (None, "summer_start", "xs:string"),
        (None, "first_year", "xs:decimal"),
        (None, "last_year", "xs:decimal"),
        (None, "width", "xs:decimal"),
        (None, "height", "xs:decimal"),
        ]

    def __init__(self, id, sobek_input, non_geographic):
        self.id = str(uuid.uuid4())
        self.content = {}
        self.content['id'] = id
        if len(self.sources) == 0:
            return
        try:
            todo = [(self.sources[0], 'id')]
            while todo:
                container_name, key = todo.pop()
                if container_name not in self.sources:
                    continue
                try:
                    type = self.MAIN_TAG[container_name][0]
                    if type is None:
                        continue
                    id = self.content[key]
                    sobek_object = sobek_input[container_name][type, id]
                except KeyError, e:
                    log.warn("%s: in %s, %s" % (e.__class__.__name__,
                                                container_name, str(e)))
                    continue
                except AttributeError, e:
                    log.warn("no %s link to %s" % (key, container_name))
                    continue
                for key, value in sobek_object.fields.items():
                    if key.find(' ') != -1:
                        key = key.replace(' ', '-')
                    else:
                        value = value[0]
                    self.content.setdefault(key, value)
                    if key in ['si', 'di']:
                        non_geographic.add(('N&S_PROFILE_DEF', value))
                todo.extend(self.MAIN_TAG[container_name][1].items())
        except Exception, e:
            log.warn("%s: %s" % (e.__class__.__name__, str(e)))

    @classmethod
    def add_definition_to(cls, container):
        """add own schema to container
        """

        doc = container.ownerDocument

        element = doc.createElement('xs:element')
        element.setAttribute("name", cls.element_name)
        element.setAttribute("substitutionGroup", "gml:_Feature")
        container.appendChild(element)

        complexType = doc.createElement("xs:complexType")
        element.appendChild(complexType)

        complexContent = doc.createElement("complexContent")
        complexType.appendChild(complexContent)

        extension = doc.createElement("extension")
        extension.setAttribute("base", "gml:AbstractFeatureType")
        complexContent.appendChild(extension)

        cls.sequence = doc.createElement("sequence")
        extension.appendChild(cls.sequence)

        for key, _ in cls.fields_used:
            element = doc.createElement("xs:element")
            element.setAttribute("ref", "fme:%s" % key)
            cls.sequence.appendChild(element)

    def add_field_to_itself(self, key, value):
        doc = self.itself.ownerDocument
        (key, xsd_type) = self.translate_key(key)
        field = doc.createElement("fme:" + key)
        self.itself.appendChild(field)
        ptext = doc.createTextNode(str(value))
        field.appendChild(ptext)
        Base.fields_used.add((key, xsd_type))
        self.__class__.fields_used.add((key, xsd_type))

    def add_as_element_to(self, container):
        """add self as xml element to container
        """

        doc = container.ownerDocument
        feature_member = doc.createElement('gml:featureMember')
        container.appendChild(feature_member)

        self.itself = itself = doc.createElement("fme:" + self.element_name)
        feature_member.appendChild(itself)

        for key, value in self.content.items():
            if key in self.automatic_fields:
                self.add_field_to_itself(key, value)

        tble = CrossSectionYZ(self.content['id'], self.content.get('lt-yz', [None])[0])
        tble.add_as_element_to(container)

        tble = PumpStages(self.content['id'], self.content.get('ct-lt', [1, None])[1])
        tble.add_as_element_to(container)

        tble = CrossSectionLW(self.content['id'], self.content.get('lt-lw', [None])[0])
        if tble.is_rectangular():
            self.add_field_to_itself('height', tble.height())
            self.add_field_to_itself('width', tble.width())
        else:
            tble.add_as_element_to(container)

        ## if object has a ti-tv field, decode it
        tble = self.content.get('ti-tv', [None, None])[1]
        if tble is not None:
            self.add_field_to_itself('first_year', tble.table_data[0, 0][0:4])
            self.add_field_to_itself('last_year', 2150)
            self.add_field_to_itself('summer_start', tble.table_data[0, 0][5:10].replace('/', ''))
            self.add_field_to_itself('winter_start', tble.table_data[2, 0][5:10].replace('/', ''))
            capacity = max(tble.table_data[k, 1] for k in range(tble.rows()))
            self.add_field_to_itself('capacity', capacity)

        if hasattr(self, 'point'):
            geom_property = doc.createElement('gml:pointProperty')
            itself.appendChild(geom_property)
            geom = doc.createElement('gml:Point')
            geom.setAttribute("srsName", "EPSG:28992")
            geom.setAttribute("srsDimension", "2")
            geom_property.appendChild(geom)
            pos = doc.createElement('gml:pos')
            geom.appendChild(pos)
            ptext = doc.createTextNode("%s %s" % self.point)
            pos.appendChild(ptext)

        if hasattr(self, 'from_point') and hasattr(self, 'to_point'):
            if self.from_point == self.to_point:
                log.warn("can't create LineString object with coinciding ends")
            else:
                geom_property = doc.createElement('gml:curveProperty')
                itself.appendChild(geom_property)
                geom = doc.createElement('gml:LineString')
                geom.setAttribute("srsName", "EPSG:28992")
                geom.setAttribute("srsDimension", "2")
                geom_property.appendChild(geom)
                pos = doc.createElement('gml:posList')
                geom.appendChild(pos)
                ptext = doc.createTextNode(("%s %s" % self.from_point) +
                                           " " + ("%s %s" % self.to_point))
                pos.appendChild(ptext)

    def translate_key(self, key):
        """give the configured name of the key
        """

        log.debug("translate_key receiving '%s'" % key)
        if key in set([sobn for (sobn, intn, xsdt) in self.field_def if intn is not None and sobn is not None]):
            key, xsd_type = dict([(sobn, (intn, xsdt)) for (sobn, intn, xsdt) in self.field_def if sobn is not None])[key]
        else:
            xsd_type = "xs:NCName"
        key = self.config_dict.get(key, key)

        log.debug("translate_key returning %s/%s" % (key, xsd_type))
        return (key, xsd_type)

    @classmethod
    def register_configuration(cls, config_file_name):
        """process a valid cf config.ini and register the configured names

        processing means read the configuration file, consider only
        all column sections (eg [column.bridge]) and store the field
        name conversions.

        this is a per-class action, so after reading the
        configuration, this function invokes
        Base.register_section, which implements derived class
        recursion.
        """

        import ConfigParser
        config = ConfigParser.ConfigParser()
        config.read(config_file_name)

        column_sections = [i for i in config.sections() if i.startswith('column.')]
        log.info("scanning sections %s" % column_sections)
        config_dict = dict((s[7:], dict((k.lower(), v.lower())
                                    for (k, v) in config.items(s)
                                    if k != '-' and v != '-'))
                           for s in column_sections)

        log.debug("using configuration %s" % config_dict)
        cls.register_section(config_dict)

    @classmethod
    def register_section(cls, config_dict):
        if hasattr(cls, 'section_name'):
            section_name = cls.section_name
        else:
            section_name = cls.__name__.lower()
        cls.config_dict = config_dict.get(section_name, {})
        log.info("class '%s' registered config_dict '%s'" % (cls.__name__, cls.config_dict))
        for subclass in cls.__subclasses__():
            subclass.register_section(config_dict)


class TabularData(Base):
    element_name = "unknown"
    enumerating = False

    def __init__(self, fk, source):
        self.fk = fk
        self.tble = source

    def add_as_element_to(self, container):
        """add own schema to container
        """

        if self.tble is None:
            return

        doc = container.ownerDocument

        for row in range(self.tble.rows()):
            feature_member = doc.createElement('gml:featureMember')
            container.appendChild(feature_member)

            self.itself = itself = doc.createElement("fme:" + self.element_name)
            feature_member.appendChild(itself)

            self.add_field_to_itself('id', self.fk)
            if self.enumerating:
                self.add_field_to_itself('rowno', row + 1)
            for col in range(self.tble.cols()):
                self.add_field_to_itself(self.colnames[col], self.tble[row, col])


class PumpStages(TabularData):
    element_name = "pump_station_def"
    enumerating = True
    fields_used = set()
    section_name = 'pump_station_def'
    colnames = ['capacity', 'suc_start', 'suc_stop', 'prs_start', 'prs_stop', ]


class CrossSectionYZ(TabularData):
    element_name = "cross_section_yz"
    fields_used = set()
    section_name = 'xsection_2dpoint'
    colnames = ['x', 'z']


class CrossSectionLW(TabularData):
    element_name = "cross_section_lw"
    fields_used = set()
    section_name = 'xsection_levelwidth'
    colnames = ['level', 'widthflow', 'widthmax']

    def is_rectangular(self):
        """inspect the table and tell whether shape is rectangular
        """

        if self.tble is None:
            return False

        if self.tble.rows() != 3:
            return False

        if self.tble[2, 1] > 0.01:
            return False

        if self.tble[2, 0] - self.tble[1, 0] > 0.01:
            return False

        if self.tble[1, 1] != self.tble[0, 1]:
            return False

        return True

    def width(self):
        return self.tble[0, 1]

    def height(self):
        return self.tble[1, 0]


class Profile(Base):
    'models a profile definition, used by objects that are geographically placed'

    element_name = "cross_section_definition"
    section_name = 'xsection_definition'
    sources = ['PROFILE.DEF']
    automatic_fields = set(['gu', 'bl', 'wm', 'bw', 'aw', 'bs', 'gl', 'ty', 'rd']).union(Base.automatic_fields)
    fields_used = set()


class Base_Edge(Base):
    element_name = "unknown"
    fields_used = set()

    @classmethod
    def add_definition_to(cls, container):
        """add own schema to container
        """

        super(Base_Edge, cls).add_definition_to(container)

        element = container.ownerDocument.createElement("xs:element")
        element.setAttribute("ref", "gml:curveProperty")
        cls.sequence.appendChild(element)


class Channel(Base_Edge):
    'models a SBK_CHANNEL record'

    element_name = "channel"
    automatic_fields = set().union(Base_Edge.automatic_fields)
    section_name = 'waterline'
    fields_used = set()


class Base_Node(Base):
    element_name = "unknown"
    fields_used = set()

    @classmethod
    def add_definition_to(cls, container):
        """add own schema to container
        """

        super(Base_Node, cls).add_definition_to(container)

        element = container.ownerDocument.createElement("xs:element")
        element.setAttribute("ref", "gml:pointProperty")
        cls.sequence.appendChild(element)


class Measstat(Base_Node):
    "models a SBK_MEASSTAT record"

    element_name = "measurement_station"
    automatic_fields = set().union(Base_Node.automatic_fields)
    fields_used = set()


class Uniweir(Base_Node):
    'models a SBK_UNIWEIR record'

    element_name = "universal_weir"
    sources = ['STRUCT.DAT', 'STRUCT.DEF', 'FRICTION.DAT', 'PROFILE.DEF']
    automatic_fields = set(['rt', 'gu', 'ty', 'dd', 'cl', 'sv', 'ce', 'st', 'si', 'gl']).union(Base_Node.automatic_fields)
    section_name = 'univw'
    fields_used = set()


class Weir(Base_Node):
    'models a SBK_WEIR record'

    element_name = "weir"
    sources = ['STRUCT.DAT', 'STRUCT.DEF', 'FRICTION.DAT', 'PROFILE.DEF']
    automatic_fields = set(['rt', 'ty', 'dd', 'cl', 'ce', 'sc', 'cw']).union(Base_Node.automatic_fields)
    fields_used = set()


class Orifice(Base_Node):
    'models a SBK_ORIFICE record'

    element_name = "orifice"
    sources = ['STRUCT.DAT', 'STRUCT.DEF', 'FRICTION.DAT', 'PROFILE.DEF']
    fields_used = set()


class Sbk_3b_Reach(Base_Node):
    'models a SBK_SBK-3B-REACH record'

    element_name = "rrcf_connection"
    fields_used = set()


class Culvert(Base_Node):
    'models a SBK_CULVERT record'

    element_name = "culvert"
    sources = ['STRUCT.DAT', 'STRUCT.DEF', 'FRICTION.DAT', 'PROFILE.DEF']
    automatic_fields = set(['rt', 'dl', 'll', 'ty', 'lb', 'lo', 'dd', 'gu', 'tc', 'rd', 'bl', 'si', 'rl', 'ov', 'li', 'gl']).union(Base_Node.automatic_fields)
    fields_used = set()


class Pump(Base_Node):
    'models a SBK_PUMP record'

    element_name = "pump_station"
    sources = ['STRUCT.DAT', 'STRUCT.DEF', 'FRICTION.DAT', 'PROFILE.DEF', 'CONTROL.DEF']
    automatic_fields = set(['dn', 'cj', 'ty', 'dd', 'ca']).union(Base_Node.automatic_fields)
    fields_used = set()


class Bridge(Base_Node):
    'models a SBK_BRIDGE record'

    element_name = "bridge"
    sources = ['STRUCT.DAT', 'STRUCT.DEF', 'FRICTION.DAT', 'PROFILE.DEF']
    automatic_fields = set(['dl', 'pw', 'vf', 'ty', 'lo', 'dd', 'li', 'rl', 'si', 'tb']).union(Base_Node.automatic_fields)
    structure_type = 12
    fields_used = set()

    def add_as_element_to(self, container):
        """add own schema to container
        """

        super(Bridge, self).add_as_element_to(container)
        ## read first_year, summer_start, winter_start, period from ti_tv[1]
        tble = self.content.get('lt-lw', [None])[0]
        if tble is not None:
            self.add_field_to_itself('width', tble.table_data[0, 1])
            self.add_field_to_itself('height', tble.table_data[1, 0])


class Gridpoint(Base_Node):
    'models a SBK_GRIDPOINT record'

    element_name = "calculation_points"
    fields_used = set()


class Boundary(Base_Node):
    'models a SBK_BOUNDARY record'

    element_name = "boundaries"
    sources = ['BOUNDARY.DAT']
    fields_used = set()


class Lateralflow(Base_Node):
    'models a SBK_LATERALFLOW record'

    element_name = "lateral_flow"
    sources = ['LATERAL.DAT']
    fields_used = set()


class Location(Base_Node):
    'models a SBK_PROFILE record'

    element_name = "locations"
    sources = ['PROFILE.DAT', 'PROFILE.DEF']
    automatic_fields = set(['di', 'rl', 'rs']).union(Base_Node.automatic_fields)
    fields_used = set()


Base.NAME_TO_CLASS.update({'SBK_MEASSTAT': Measstat,
                           'SBK_UNIWEIR': Uniweir,
                           'SBK_CHANNEL': Channel,
                           'SBK_WEIR': Weir,
                           'SBK_ORIFICE': Orifice,
                           'SBK_SBK-3B-REACH': Sbk_3b_Reach,
                           'SBK_CULVERT': Culvert,
                           'SBK_PUMP': Pump,
                           'SBK_BRIDGE': Bridge,
                           'SBK_GRIDPOINT': Gridpoint,
                           'SBK_CHANNELCONNECTION': Gridpoint,
                           'SBK_GRIDPOINTFIXED': Gridpoint,
                           'SBK_BOUNDARY': Boundary,
                           'SBK_LATERALFLOW': Lateralflow,
                           'SBK_PROFILE': Location,
                           'N&S_PROFILE_DEF': Profile,
                           })


def create_object(type, id, sobek_input, non_geographic=None):
    """trc object factory
    """

    return Base.NAME_TO_CLASS.get(type, Base)(id, sobek_input, non_geographic)


def from_sobek_network(sobek_network_ntw):
    """read the sobek files and convert them to trc objects.
    """

    sobek_input = {}
    sobek_input['NETWORK.NTW'] = sobek.Network(sobek_network_ntw)
    other_sobek_files = ['INITIAL.DAT', 'LATERAL.DAT', 'STRUCT.DAT',
                         'CONTROL.DEF', 'FRICTION.DAT', 'PROFILE.DEF',
                         'STRUCT.DEF', 'PROFILE.DAT', 'BOUNDARY.DAT']
    path_to_files = os.path.split(sobek_network_ntw)[0]

    sobek_input.update(dict([(i, sobek.File(path_to_files + '/' + i))
                             for i in other_sobek_files
                             if i != "NETWORK.NTW"]))

    ## the result is a collection of trc objects, indexed by type and id.
    trc_collection = dict()

    ## main entry point is the channels network, but the network also
    ## defines nodes and most of these objects correspond to trc
    ## objects that must be exported.
    sobek_network = sobek_input['NETWORK.NTW'].dict

    non_geographic = set()

    ## scan the network for objects (edge, node_from, node_to).
    sobek_channels = sobek_network.get('SBK_CHANNEL', [])
    log.debug("sobek network describes %s channels" % len(sobek_channels))
    for edge_id in sobek_channels:
        (from_type, from_id), (to_type, to_id) = (
            sobek_network['SBK_CHANNEL'][edge_id])
        edge_obj = create_object('SBK_CHANNEL', edge_id, sobek_input)
        trc_collection['SBK_CHANNEL', edge_id] = edge_obj
        if (from_type, from_id) not in trc_collection:
            obj = create_object(from_type, from_id, sobek_input, non_geographic)
            obj.point = sobek_network[from_type][from_id]
            trc_collection[from_type, from_id] = obj
        if (to_type, to_id) not in trc_collection:
            obj = create_object(to_type, to_id, sobek_input, non_geographic)
            obj.point = sobek_network[to_type][to_id]
            trc_collection[to_type, to_id] = obj
        edge_obj.from_point = trc_collection[(from_type, from_id)].point
        edge_obj.to_point = trc_collection[(to_type, to_id)].point

    log.debug("sobek network describes %s point objects" % (len(trc_collection) - len(sobek_channels)))
    log.debug("sobek network describes %s tabular objects" % len(non_geographic))

    for type, id in non_geographic:
        trc_collection[type, id] = create_object(type, id, sobek_input)

    return trc_collection


def create_gml_document(output_basename):
    """create a gml document with only the root element.

    set the attributes of the root element,
    return the root element.
    """

    doc = Document()
    root = doc.createElement('gml:FeatureCollection')
    doc.appendChild(root)

    for key, value in [("xmlns:gml", "http://www.opengis.net/gml"),
                       ("xmlns:xlink", "http://www.w3.org/1999/xlink"),
                       ("xmlns:xsi",
                        "http://www.w3.org/2001/XMLSchema-instance"),
                       ("xmlns:fme", "http://www.safe.com/gml/fme"),
                       ("xsi:schemaLocation",
                        "http://www.safe.com/gml/fme " + output_basename + ".xsd"),
                       ]:
        root.setAttribute(key, value)

    return root


def create_xsd_document():
    """create the schema document with only the root element

    set the attributes of the root element,
    add the atomic elements,
    return the root element
    """

    doc = Document()
    root = doc.createElement('xs:schema')
    doc.appendChild(root)

    for key, value in [("xmlns:xs", "http://www.w3.org/2001/XMLSchema"),
                       ("elementFormDefault", "qualified"),
                       ("targetNamespace", "http://www.safe.com/gml/fme"),
                       ("xmlns:fme", "http://www.safe.com/gml/fme"),
                       ("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance"),
                       ("xmlns:gml", "http://www.opengis.net/gml"),
                       ]:
        root.setAttribute(key, value)

    xs_import = doc.createElement("xs:import")
    xs_import.setAttribute("namespace", "http://www.opengis.net/gml")
    xs_import.setAttribute("schemaLocation", "http://schemas.opengis.net/gml/3.1.1/base/gml.xsd")
    root.appendChild(xs_import)

    for key, value in Base.fields_used:
        xs_element = doc.createElement("xs:element")
        xs_element.setAttribute("name", key)
        xs_element.setAttribute("type", value)
        root.appendChild(xs_element)

    return root

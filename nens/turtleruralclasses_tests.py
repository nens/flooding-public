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

__revision__ = "$Rev: 22194 $"[6:-2]

import unittest
import turtleruralclasses as trc
from turtleruralclasses import Base
from turtleruralclasses import Measstat
from turtleruralclasses import Uniweir
from turtleruralclasses import Channel
#from turtleruralclasses import weir
#from turtleruralclasses import orifice
#from turtleruralclasses import sbk_3b_reach
from turtleruralclasses import Culvert
#from turtleruralclasses import pump
from turtleruralclasses import Bridge
#from turtleruralclasses import gridpoint
#from turtleruralclasses import boundary
from turtleruralclasses import Lateralflow
#from turtleruralclasses import profile
#from turtleruralclasses import create_object
from turtleruralclasses import from_sobek_network
from turtleruralclasses import create_gml_document
from turtleruralclasses import create_xsd_document
from turtleruralclasses import CrossSectionLW
from xml.dom.minidom import Element
import pkg_resources


class SomeGenericTests(unittest.TestCase):

    def setUp(self):
        reload(trc)

    def test0001(self):
        'can create empty schema'

        schema = create_xsd_document()
        self.assertTrue(isinstance(schema, Element))
        self.assertEquals("xs:schema", schema.tagName)
        self.assertEquals(1, len(schema.childNodes))

    def test0002(self):
        'can create empty document'

        obj = create_gml_document("filename")
        self.assertTrue(isinstance(obj, Element))
        self.assertEquals("gml:FeatureCollection", obj.tagName)
        self.assertEquals(0, len(obj.childNodes))
        self.assertEquals("http://www.safe.com/gml/fme filename.xsd", obj.getAttribute("xsi:schemaLocation"))


class SetOfTestsOnNetwork01(unittest.TestCase):

    def test0010(self):
        'import network01 into trc'

        input_file_name = pkg_resources.resource_filename("nens", "testdata/network01/NETWORK.NTW")
        collection = from_sobek_network(input_file_name)
        self.assertEquals(185, len(collection))

    def test0020(self):
        'register configuration'

        config_file_name = pkg_resources.resource_filename("nens", "testdata/network01/cf_config.ini")
        Base.register_configuration(config_file_name)
        self.assertEquals('bed_lvl', Bridge.config_dict['bottom_level'])
        self.assertEquals('kwkident', Bridge.config_dict['id'])
        self.assertEquals('cp_ident', Measstat.config_dict['id'])
        self.assertEquals('ovkident', Channel.config_dict['id'])
        self.assertEquals('lat_ident', Lateralflow.config_dict['id'])
        self.assertEquals('dis_coef', Uniweir.config_dict['discharge_coefficient'])
        self.assertEquals('outlet_los', Culvert.config_dict['outlet_loss'])

    def test030(self):
        'adding a couple of objects to the gml output'

        input_file_name = pkg_resources.resource_filename("nens", "testdata/network01/NETWORK.NTW")
        collection = from_sobek_network(input_file_name)
        root = create_gml_document("filename")
        collection[('SBK_GRIDPOINT', 'WL_5_5')].add_as_element_to(root)
        self.assertEquals(1, len(root.childNodes))
        gridpoint = root.childNodes[0]
        self.assertEquals([], gridpoint.attributes.keys())
        self.assertEquals(1, len(gridpoint.childNodes))
        self.assertEquals(2, len(gridpoint.childNodes[0].childNodes))
        self.assertEquals('<fme:id>WL_5_5</fme:id>', gridpoint.childNodes[0].childNodes[0].toxml())

        collection[('SBK_WEIR', 'KST_2')].add_as_element_to(root)
        self.assertEquals(2, len(root.childNodes))
        weir = root.childNodes[1]
        self.assertEquals([], weir.attributes.keys())
        self.assertEquals([], weir.attributes.keys())
        self.assertEquals(1, len(weir.childNodes))
        self.assertEquals(10, len(weir.childNodes[0].childNodes))
        self.assertEquals('<fme:flow_direction>0</fme:flow_direction>', weir.childNodes[0].childNodes[0].toxml())

    def test0040(self):
        'add empty definition to schema'

        schema = create_xsd_document()
        Channel.add_definition_to(schema)
        self.assertEquals(2, len(schema.childNodes))
        self.assertEquals("xs:element", schema.childNodes[1].tagName)
        self.assertEquals("channel", schema.childNodes[1].getAttribute("name"))

    def test0200(self):
        'some of the profiles are rectangular'
        input_file_name = pkg_resources.resource_filename("nens", "testdata/network01/NETWORK.NTW")
        collection = from_sobek_network(input_file_name)
        tables = [CrossSectionLW('fake_id', i.content['lt-lw'][0]) for i in collection.values() if 'lt-lw' in i.content]
        target = [False, True, True, False, False, True, False, True]
        current = [i.is_rectangular() for i in tables]
        self.assertEquals(target, current)

    def test0210(self):
        'extents of rectangular profiles'
        input_file_name = pkg_resources.resource_filename("nens", "testdata/network01/NETWORK.NTW")
        collection = from_sobek_network(input_file_name)
        tables = [CrossSectionLW('fake_id', i.content['lt-lw'][0]) for i in collection.values() if 'lt-lw' in i.content]
        tables = [i for i in tables if i.is_rectangular()]
        target = [(1.4, 0.3), (1.33, 0.81), (3.1, 2.181), (5.3, 1.1)]
        current = [(i.width(), i.height()) for i in tables]
        self.assertEquals(target, current)


class DoctestRunner(unittest.TestCase):
    def test0000(self):
        import doctest
        doctest.testmod(name=__name__[:-6])


class SetOfTestsOnNetwork02(unittest.TestCase):

    def test0010(self):
        'import network02 into trc'

        input_file_name = pkg_resources.resource_filename("nens", "testdata/network02/NETWORK.NTW")
        collection = from_sobek_network(input_file_name)
        self.assertEquals(1389, len(collection))

    def test0020(self):
        'register configuration'

        config_file_name = pkg_resources.resource_filename("nens", "testdata/network02/cf_config.ini")
        Base.register_configuration(config_file_name)

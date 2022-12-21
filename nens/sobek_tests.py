"""nens.sobek testsuite"""
import logging
import mock
from sobek import HISFile
from sobek import File
from sobek import Network
from sobek import NoneValue
from sobek import Object
from sobek import Verbatim
from sobek import isvalue
from sobek import datetime
from sobek import print_float

handler = mock.Handler(level=logging.DEBUG)
logging.getLogger('').addHandler(handler)


def reindent(s, i=1):
    return '\n'.join(['' * i + l for l in s.split('\n')])

import unittest


class ReadingAtomsTest(unittest.TestCase):

    def test_isvalue_PDIN(self):
        "PDIN is value"
        self.assertTrue(isvalue('PDIN'))

    def test_isvalue_TBLE(self):
        "TBLE is value"
        self.assertTrue(isvalue('TBLE'))

    def test_isvalue_string(self):
        "'ab' is value"
        self.assertTrue(isvalue("'ab'"))

    def test_isvalueNOT_id(self):
        "ab is not a value"
        self.assertFalse(isvalue("ab"))

    def test_isvalue_integer(self):
        "123 is value"
        self.assertTrue(isvalue('123'))

    def test_isvalue_float(self):
        "1.23 is value"
        self.assertTrue(isvalue('1.23'))

    def testNODE_length(self):
        "NODE object with 4 fields"
        obj = Object("NODE id 'BOEZ_1' nm '' px 134808.891822728 py 456721.97309417 node")
        self.assertEqual(len(obj.fields), 4)
        pass

    def testPDIN_no_id(self):
        "PDIN are arrays without an id"
        obj = Object("PDIN 1 2 3 pdin")
        self.assertEqual(obj['PDIN'], [1, 2, 3])
        pass

    def testNODE_tag(self):
        "NODE tag"
        obj = Object("NODE id '1' node")
        self.assertEqual(obj.tag, 'NODE')
        pass

    def testNODE_id(self):
        "NODE id"
        obj = Object("NODE id '1' node")
        self.assertEqual(obj.id, '1')
        pass

    def testNODE_fields(self):
        "NODE fields"
        obj = Object("NODE id 'BOEZ_1' nm '' px 134808.891822728 py 456721.97309417 node")
        self.assertEqual(obj['id'], ['BOEZ_1'])
        self.assertEqual(obj['nm'], [''])
        self.assertEqual(obj['px'], [134808.891822728])
        self.assertEqual(obj['py'], [456721.97309417])
        pass


class ObjectLikeHandling(unittest.TestCase):

    def test1_creation(self):
        "create object with TAG only gets random id"
        obj = Object(tag="TEST")
        self.assertNotEqual(obj.id, None)

    def test2_creation(self):
        "create object with TAG and id"
        obj = Object(tag="TEST", id='id')
        self.assertEqual(obj.id, 'id')
        self.assertEqual(str(obj), "TEST id 'id' test")

    def test3_alter(self):
        "altering id field is reflected in id attribute"
        obj = Object(tag="TEST", id='id')
        obj['id'] = 'test'
        self.assertEqual(obj.id, 'test')
        self.assertEqual(str(obj), "TEST id 'test' test")

    def test40_alter(self):
        "altering id attribute raises AttributeError"
        obj = Object(tag="TEST", id='id')
        self.assertRaises(AttributeError, obj.__setattr__, 'id', 'test')

    def test42_alter(self):
        "reading incorrectly formed object raises ValueError"
        input = "GLFR id '0' BDFR id '0' ci '0' mf 0 sf 0 mr cp 0 40 mt st sr bdfr glfr"
        self.assertRaises(ValueError, Object, input)

    def test5_addingFields(self):
        "adding fields to object created with TAG and id"
        obj = Object(tag="TEST", id='id')
        obj['px'] = 135000
        obj['py'] = 455000
        self.assertEqual(str(obj), "TEST id 'id' px 135000 py 455000 test")

    def test60(self):
        "asking all attributes of an object"
        obj = Object(tag="TEST", id='id')
        obj['px'] = 135000
        obj['py'] = 455000
        self.assertEqual(len(obj.attribs()), 3)
        self.assertEqual('id' in obj.attribs(), True)
        self.assertEqual('px' in obj.attribs(), True)
        self.assertEqual('py' in obj.attribs(), True)

    def test61(self):
        "asking if an object has an attribute"
        obj = Object(tag="TEST", id='id')
        obj['px'] = 135000
        obj['py'] = 455000
        self.assertEqual('id' in obj, True)
        self.assertEqual('px' in obj, True)
        self.assertEqual('py' in obj, True)

    def test70(self):
        "reading attributes that contain attributes that contain values"
        src = "STFR id '15' ci '15' mf 4 mt cp 0 0.003 0 mr cp 0 0.003 0 s1 6 s2 6 sf 4 st cp 0 0.003 0 sr cp 0 0.003 stfr"
        obj = Object(src)
        self.assertEqual('mt cp' in obj.fields, True)
        self.assertEqual(obj.fields['mt cp'], [0, 0.003, 0])
        self.assertEqual(str(obj), src)

    def test71(self):
        "reading attributes that contain attributes with empty list of values"
        src = "GRID id '1' ci '1' gr gr grid"
        obj = Object(src)
        self.assertEqual('gr gr' in obj.fields, True)
        self.assertEqual(obj.fields['gr gr'], [])
        self.assertEqual(str(obj), src)


class ReadingComplexTest(unittest.TestCase):

    def testFLBO_containedArray(self):
        "FLBO contains an array"
        obj = Object("FLBO id 'lkb_condition_extern' ty 0 h_ wt 1 0 0 PDIN 0 0  pdin flbo")
        pdin = Object("PDIN 0 0 pdin")
        self.assertEqual(obj['h_ wt'][3], pdin)
        pass

    def testFLBO_containedTable(self):
        "FLBO contained table"
        table_str = """\
TBLE \n\
 '2000/01/01;00:00:00' 1 <
 '2000/01/01;06:00:00' 1.5 <
 '2000/01/01;12:00:00' 1 <
 '2000/01/01;18:00:00' 1.9 <
 '2000/01/02;00:00:00' .8 <
 '2000/01/02;06:00:00' 1.5 <
 '2000/01/02;12:00:00' .6 <
 '2000/01/02;18:00:00' 1.5 <
 '2000/01/03;00:00:00' 0 <
 tble"""
        obj = Object("FLBO id 'lkb_condition_extern' " + table_str + " flbo")
        table = Object(table_str)
        self.assertEqual(obj['TBLE'][0], table)
        pass


class ReadingListsTest(unittest.TestCase):
    obj1_str = """\
GFLS nc 15 nr 15 x0 135000 y0 456500 dx 100 dy 100 cp 0 fnm '\Sobek210\lizardkb.lit\FIXED\grid\test_hoogte.asc' gfls
"""
    obj2_str = """\
PT12 id '2' nm '2' ci '1' lc 0 px 135451.113212727 py 456364.531129484 mc 5 mr 2 pt12
"""
    obj3_str = """\
PT12 id '5' nm '5' ci '1' lc 99.1349688238926 px 135352.060094798 py 456360.503490938 mc 4 mr 2 pt12
"""
    domain_str = """\
DOMN id '1' nm '1'
  """ + obj1_str + """
  """ + obj2_str + """
  """ + obj3_str + """
domn"""

    def testDOMN_length(self):
        "DOMN reads that many objects"
        domain = Object(self.domain_str)
        self.assertEqual(len(domain.fields), 4)
        self.assertEqual(len(domain['GFLS']), 1)
        self.assertEqual(len(domain['PT12']), 2)

    def testDOMN_first(self):
        "DOMN reads the first object"
        domain = Object(self.domain_str)
        gfls = Object(self.obj1_str)
        self.assertEqual(domain['GFLS'][0], gfls)

    def testDOMN_last(self):
        "DOMN reads the last object"
        domain = Object(self.domain_str)
        pt12 = Object(self.obj3_str)
        self.assertEqual(domain['PT12'][1], pt12)


class ReadingFromFile(unittest.TestCase):
    point_1 = "PT12 id '2' nm '2' ci '1' lc 0 px 135451.113212727 py 456364.531129484 mc 5 mr 2 pt12"
    point_2 = "PT12 id '5' nm '5' ci '1' lc 99.1349688238926 px 135352.060094798 py 456360.503490938 mc 4 mr 2 pt12"
    input_domn = """\
D121.0
DOMN id '2' nm '1'
domn
DOMN id '1' nm '1'
  GFLS nc 15 nr 15 x0 135000 y0 456500 dx 100 dy 100 cp 0 fnm '\\Sobek210\\lizardkb.lit\\FIXED\\grid\\test_hoogte.asc' gfls
  """ + point_1 + """
  """ + point_2 + """
domn
DOMN id '3' nm '1'
  PT12 id '7' nm '5' ci '1' lc 99.1349688238926 px 135352.060094798 py 456360.503490938 mc 4 mr 2 pt12
domn
"""
    input_noversion = """\
GFLS nc 15 nr 15 x0 135000 y0 456500 dx 100 dy 100 cp 0 fnm '\Sobek210\lizardkb.lit\FIXED\grid\test_hoogte.asc' gfls
NODE id '10' ty 1 ws 10000 ss 0 wl -0.89 ml 0 node
PT12 id '7' nm '5' ci '1' lc 99.1349688238926 px 135352.060094798 py 456360.503490938 mc 4 mr 2 pt12
PT12 id '2' nm '2' ci '1' lc 0 px 135451.113212727 py 456364.531129484 mc 5 mr 2 pt12
"""

    def test01Reading(self):
        "reading three objects from a stream"

        content = File(mock.Stream(self.input_domn))
        self.assertEqual(len(content), 3)

    def test02Reading(self):
        "reading one object from a versionless stream"

        content = File(mock.Stream(self.input_noversion))
        self.assertEqual(len(content), 4)

    def test11Reading(self):
        "version and extension from source stream"

        content = File(mock.Stream(self.input_domn))
        self.assertEqual(content.version, 1.0)
        self.assertEqual(content.extension, 'D12')

    def test12Reading(self):
        "source stream does not have any version information"

        content = File(mock.Stream(self.input_noversion))
        self.assertEqual(content.version, None)
        self.assertEqual(content.extension, None)

    def test2GetElement(self):
        "reading a file and selecting an atom"
        network_d12 = File(mock.Stream(self.input_domn))
        grid_name = network_d12['DOMN'][1]['GFLS'][0]['fnm'][0]
        self.assertEqual(grid_name, r'\Sobek210\lizardkb.lit\FIXED\grid\test_hoogte.asc')

    def test3GetFirstIteratedElement(self):
        "reading a file and selecting first of two objects with same type"
        network_d12 = File(mock.Stream(self.input_domn))
        self.assertEqual(len(network_d12['DOMN'][1]['PT12']), 2)
        self.assertEqual(len(network_d12['DOMN'][2]['PT12']), 1)
        point = network_d12['DOMN'][1]['PT12'][0]
        self.assertEqual(str(point), self.point_1)

    def test4GetSecondIteratedElement(self):
        "reading a file and selecting second of two objects with same type"
        network_d12 = File(mock.Stream(self.input_domn))
        point = network_d12['DOMN'][1]['PT12'][1]
        self.assertEqual(str(point), self.point_2)

    def test50(self):
        "reading a file and selecting object by type and id"
        network_d12 = File(mock.Stream(self.input_domn))
        self.assertEqual(network_d12['DOMN', '2'], network_d12['DOMN'][0])
        self.assertEqual(network_d12['DOMN', '1'], network_d12['DOMN'][1])
        self.assertEqual(network_d12['DOMN', '3'], network_d12['DOMN'][2])

    def test60(self):
        "iterating in a File is allowed"
        f = File(mock.Stream(self.input_domn))
        self.assertEqual(len([i for i in f]), 3)

    def test61(self):
        "iterating in a DOMN is allowed"
        f = File(mock.Stream(self.input_domn))
        self.assertEqual(len([0 for i in f['DOMN'][0]]), 0)
        self.assertEqual(len([0 for i in f['DOMN'][1]]), 3)
        self.assertEqual(len([0 for i in f['DOMN'][2]]), 1)

    def test70(self):
        "reading a GFLR containing a BDFR and nothing else"
        txt = "GLFR BDFR id '0' ci '0' mf 0 mt cp 0 0.0000 0 mr cp 0 0.0000 0 s1 6 s2 6 sf 0 st cp 0 0.0000 0 sr cp 0 0.0000 bdfr    glfr"
        f = File(mock.Stream(txt))
        f['GLFR']
        f['GLFR'][0]
        f['GLFR'][0]['BDFR']


class RepresentingAsText(unittest.TestCase):

    obj0_str = """\
PT12 id '2' nm '2' ci '1' lc 0 px 135451.113212727 py 456364.531129484 mc 5 mr 2 %spt12"""
    obj1_str = """\
PT12 id '2' nm '2' ci '1' lc 0 px 135451.5 py 456366 mc 5 mr 2 %spt12"""
    obj2_str = """\
PT12 id '2' nm '2 bis' ci '1' lc 0 px 135451.5 py 456366 mc 5 mr 2 %spt12"""
    obj2a_str = """\
PT12 id '2' nm '2 bis a' ci '1' lc 0 px 135451.5 py 456366 mc 5 mr 2 %spt12"""

    def test10writing(self):
        "representing unmodified object"
        obj = Object(self.obj0_str % '')
        self.assertEqual(str(obj), self.obj0_str % '')

    def test11writing(self):
        "representing unmodified object - with spaces in string"
        obj = Object(self.obj2_str % '')
        self.assertEqual(str(obj), self.obj2_str % '')

    def test12writing(self):
        "representing modified object - with spaces in string"
        obj = Object(self.obj2_str % '')
        obj['nm'] = '2 bis a'
        self.assertEqual(str(obj), self.obj2a_str % '')

    def test24writing(self):
        "representing modified object (modify single field value)"

        obj = Object(self.obj0_str % '')
        obj['px'][0] = 135451.5
        obj['py'][0] = 456366
        self.assertEqual(str(obj), self.obj1_str % '')

    def test25writing(self):
        "representing modified object (redefine atomic field)"

        obj = Object(self.obj0_str % '')
        obj['px'] = 135451.5
        obj['py'] = 456366
        self.assertEqual(str(obj), self.obj1_str % '')

    def test251writing(self):
        "representing modified object (adding atomic fields)"

        d2li = Object("D2LI id 'id' d2li")
        d2li['bx'] = 125500
        d2li['by'] = 425500
        d2li['ex'] = 135500
        d2li['ey'] = 455500
        self.assertEqual(str(d2li), "D2LI id 'id' bx 125500 by 425500 ex 135500 ey 455500 d2li")

    def test252writing(self):
        "representing modified object (adding list of fields)"

        d2li = Object("D2LI id 'id' d2li")
        d2li['bn'] = [125500, 425500]
        d2li['en'] = [135500, 455500]
        self.assertEqual(str(d2li), "D2LI id 'id' bn 125500 425500 en 135500 455500 d2li")

    def test253writing(self):
        "representing modified object (adding two fields at once)"

        li12 = Object("LI12 id 'id' li12")
        li12['bx'], li12['by'] = [125500, 425500]
        li12['ex'], li12['ey'] = [135500, 455500]
        self.assertEqual(str(li12), "LI12 id 'id' bx 125500 by 425500 ex 135500 ey 455500 li12")

    def test26writing(self):
        "representing modified object (add 'str' field)"

        obj = Object(self.obj0_str % '')
        obj['iets'] = 'waarde'
        self.assertEqual(str(obj), self.obj0_str % "iets 'waarde' ")

    def test270writing(self):
        "representing modified object (add int field)"

        obj = Object(self.obj0_str % '')
        obj['iets'] = 13
        self.assertEqual(str(obj), self.obj0_str % "iets 13 ")

    def test271writing(self):
        "representing modified object (add long field)"

        obj = Object(self.obj0_str % '')
        obj['iets'] = 13401345L
        self.assertEqual(str(obj), self.obj0_str % "iets 13401345 ")

    def test272writing(self):
        "representing modified object (add small float field)"

        obj = Object(self.obj0_str % '')
        obj['iets'] = 13.40
        self.assertEqual(str(obj), self.obj0_str % "iets 13.4 ")

    def test273writing(self):
        "representing modified object (add large float field)"

        obj = Object(self.obj0_str % '')
        obj['iets'] = 9999900000
        try:
            self.assertEqual(str(obj), self.obj0_str % "iets 9.9999e+009 ")
        except AssertionError:
            self.assertEqual(str(obj), self.obj0_str % "iets 9.9999e+09 ")

    def test274writing(self):
        "representing modified object (add huge float field)"

        obj = Object(self.obj0_str % '')
        obj['iets'] = 9.999e+019
        try:
            self.assertEqual(str(obj), self.obj0_str % "iets 9.999e+019 ")
        except AssertionError:
            self.assertEqual(str(obj), self.obj0_str % "iets 9.999e+19 ")

    def test28writing(self):
        "representing modified object (add PDIN field)"

        obj = Object(self.obj0_str % '')
        pdin = Object("PDIN 0 1 '' pdin")
        obj['PDIN'].append(pdin)
        self.assertEqual(str(obj), self.obj0_str % "\nPDIN 0 1 '' pdin ")

    def test3PDIN_no_id(self):
        "representing arrays without an id"
        obj = Object("PDIN 1 2 3 pdin")
        self.assertEqual(str(obj), "PDIN 1 2 3 pdin")
        pass

    def test4FLBO_containedArray(self):
        "representing FLBO with contained array"
        obj_str = "FLBO id 'lkb_condition_extern' ty 0 h_ wt 1 0 0 \nPDIN 0 0 pdin flbo"
        obj = Object(obj_str)
        self.assertEqual(str(obj), obj_str)
        pass

    def test5FLBO_containedTable(self):
        "representing FLBO with contained table"
        table_str = """\
TBLE \n\
'2000/01/01;00:00:00' 1 <
'2000/01/01;06:00:00' 1.5 <
'2000/01/01;12:00:00' 1 <
'2000/01/01;18:00:00' 1.9 <
'2000/01/02;00:00:00' 0.8 <
'2000/01/02;06:00:00' 1.5 <
'2000/01/02;12:00:00' 0.6 <
'2000/01/02;18:00:00' 1.5 <
'2000/01/03;00:00:00' 0 <
tble"""
        obj_str = "FLBO id 'lkb_condition_extern' \n" + table_str + " flbo"
        obj = Object(obj_str)
        self.assertEqual(str(obj), obj_str)

    def test60_printingdatetime(self):
        "can write datetime.datetime objects in tables"

        flbo = Object("FLBO id 'lkb_condition_extern' ty 0 h_ wt 1 0 0 PDIN 0 0 pdin flbo")
        values = {datetime.datetime(2000, 1, 1, 0): 1.2,
                  datetime.datetime(2000, 1, 1, 1): 1.1,
                  datetime.datetime(2000, 1, 1, 2): 1.0,
                  datetime.datetime(2000, 1, 1, 3): 0.7,
                  datetime.datetime(2000, 1, 1, 4): 0.4,
                  }

        for key, value in values.items():
            flbo.addRow([key, value])
        self.assertEqual(str(flbo), """\
FLBO id 'lkb_condition_extern' ty 0 h_ wt 1 0 0 \n\
PDIN 0 0 pdin \n\
TBLE \n\
'2000-01-01;00:00:00' 1.2 <
'2000-01-01;01:00:00' 1.1 <
'2000-01-01;02:00:00' 1 <
'2000-01-01;03:00:00' 0.7 <
'2000-01-01;04:00:00' 0.4 <
tble flbo""")

    def test62_printingtimedelta(self):
        "can write datetime.datetime objects"

        obj = Object("STDS id 'id' nm '' ts '2000/01/01;00:30:00' dt '0:01:00:00' stds")

        obj['ts'] = datetime.datetime(2000, 1, 2, 3, 4, 5)
        self.assertEqual(str(obj), "STDS id 'id' nm '' ts '2000-01-02;03:04:05' dt '0:01:00:00' stds")

    def test63_printingtimedelta(self):
        "can write datetime.timedelta objects, longer than 1 day"

        obj = Object("STDS id 'id' nm '' ts '2000/01/01;00:30:00' dt '0:01:00:00' stds")

        obj['dt'] = datetime.timedelta(1, 43251)
        self.assertEqual(str(obj), "STDS id 'id' nm '' ts '2000/01/01;00:30:00' dt '1:12:00:51' stds")

    def test64_printingtimedelta(self):
        "can write datetime.timedelta objects, shorter than 1 day"

        obj = Object("STDS id 'id' nm '' ts '2000/01/01;00:30:00' dt '0:01:00:00' stds")

        obj['dt'] = datetime.timedelta(0, 43251)
        self.assertEqual(str(obj), "STDS id 'id' nm '' ts '2000/01/01;00:30:00' dt '0:12:00:51' stds")


class RepresentingFloats(unittest.TestCase):

    def test_excess(self):
        "1.1 (1.1000000000000001) is printed as 1.1"
        self.assertEqual(print_float(1.1), "1.1")

    def test_defect(self):
        "1.4 (1.3999999999999999) is printed as 1.4"
        self.assertEqual(print_float(1.4), "1.4")

    def test_larger(self):
        "135451.113212727 (135451.11321272701)"
        self.assertEqual(print_float(135451.113212727), "135451.113212727")

    def test_smaller(self):
        "0.06 (0.059999999999999998)"
        self.assertEqual(print_float(0.06), "0.06")


class WritingToFile(unittest.TestCase):

    def test0writing(self):
        "writing a NETWORK.TP - no version"
        input_str = """\
NODE id 'BOEZ_1' nm '' px 134808.891822728 py 456721.97309417 node
BRCH id '6' nm '' bn 'BOEZ_4' en 'BOEZ_2' al 204.961262972225 brch
"""
        sobek = File(mock.Stream(input_str))
        output = mock.Stream()
        sobek.writeToStream(output)
        self.assertEqual(''.join(output.content), input_str)

    def test1writing(self):
        "writing a NETWORK.TP - with version"
        input_str = """\
TP_1.0
NODE id 'BOEZ_1' nm '' px 134808.891822728 py 456721.97309417 node
BRCH id '6' nm '' bn 'BOEZ_4' en 'BOEZ_2' al 204.961262972225 brch
"""
        sobek = File(mock.Stream(input_str))
        output = mock.Stream()
        sobek.writeToStream(output)
        self.assertEqual(''.join(output.content), input_str)

    def test2writing(self):
        "writing DOMN with more than one included objects of same type"
        input_str = """\
D121.0
DOMN id '2' nm '1' \n\
domn
DOMN id '1' nm '1' \n\
  GFLS nc 15 nr 15 x0 135000 y0 456500 dx 100 dy 100 cp 0 fnm '\\Sobek210\\lizardkb.lit\\FIXED\\grid\\test_hoogte.asc' gfls \n\
  PT12 id '2' nm '2' ci '1' lc 0 px 135451.113212727 py 456364.531129484 mc 5 mr 2 pt12 \n\
  PT12 id '5' nm '5' ci '1' lc 99.1349688238926 px 135352.060094798 py 456360.503490938 mc 4 mr 2 pt12 \n\
domn
DOMN id '3' nm '1' \n\
  PT12 id '7' nm '5' ci '1' lc 99.1349688238926 px 135352.060094798 py 456360.503490938 mc 4 mr 2 pt12 \n\
domn
"""
        sobek = File(mock.Stream(input_str))
        self.assertEqual(len(sobek['DOMN'][1]['PT12']), 2)
        output = mock.Stream()
        sobek.writeToStream(output)
        self.assertEqual(''.join(output.content), input_str)

    def test3writing(self):
        "reading empty DOMN and writing it after adding one PT12"
        input_str = """\
D121.0
DOMN id '2' nm '1' %s
domn
"""
        pt_str = """
  PT12 id '2' nm '2' ci '1' lc 0 px 135451.113212727 py 456364.531129484 mc 5 mr 2 pt12 """

        sobek = File(mock.Stream(input_str % ''))
        self.assertEqual(sobek['DOMN'][0]['PT12'], [])
        sobek['DOMN'][0].addObject(Object(pt_str))
        output = mock.Stream()
        sobek.writeToStream(output)
        self.assertEqual(''.join(output.content), input_str % pt_str)

    def test40writing(self):
        "reading empty DOMN and writing it after adding two PT12"
        input_str = """\
D121.0
DOMN id '2' nm '1' %s
domn
"""
        pt_str = """
  PT12 id '2' nm '2' ci '1' lc 0 px 135451.113212727 py 456364.531129484 mc 5 mr 2 pt12 """

        sobek = File(mock.Stream(input_str % ''))
        self.assertEqual(sobek['DOMN'][0]['PT12'], [])
        sobek['DOMN'][0].addObject(Object(pt_str))
        sobek['DOMN'][0].addObject(Object(pt_str))
        output = mock.Stream()
        sobek.writeToStream(output)
        self.assertEqual(''.join(output.content), input_str % (pt_str * 2))

    def test41(self):
        "writing DOMN with GRID with TBLE"
        expect = """\
DOMN id 'id' \n\
  GRID id 'id' \n\
  TBLE \n\
  1 2 3 <
  1 2 3 <
  tble grid \n\
domn"""
        domn = Object(tag='DOMN', id='id')
        grid = domn.addObject(Object(tag='GRID', id='id'))
        grid.addRow([1, 2, 3])
        grid.addRow([1, 2, 3])
        self.assertEqual(str(domn), expect)

    def test5writing(self):
        "reading and writing a NETWORK.GR"
        input_str = """\
GR_1.1
GRID id '1' ci '1' gr gr 'GridPoint Table' \n\
PDIN 0 0 '' pdin CLTT 'Location' '1/R' cltt CLID '' '' clid \n\
TBLE \n\
0 0 '' '2' '1' 135451.113212727 456364.531129484 <
99.1349688238926 0 '1' '5' '4' 135352.060094798 456360.503490938 <
199.443229780832 0 '4' '6' '5' 135253.892598708 456340.348467165 <
381.75081351349 0 '5' '19' '17' 135248.677965555 456162.71307676 <
612.922174526211 0 '15' '23' '21' 135249.438818165 455931.542967845 <
784.754497959803 0 '11' '10' '9' 135250.004368634 455759.71157511 <
974.405728092209 0 '9' '20' '18' 135250.628566341 455570.061372189 <
1188.8456835183 0 '14' '21' '19' 135251.334350998 455355.622578238 <
1403.21641321846 0 '16' '22' '20' 135252.039907812 455141.253009638 <
1505.92919162709 0 '20' '8' '7' 135267.300230805 455054.47672909 <
1577.18307555953 0 '7' '9' '8' 135338.415507777 455058.918953381 <
1694.41879530824 0 '8' '3' '' 135455.423174178 455066.227851273 <
tble grid
GRID id '2' ci '2' gr gr 'GridPoint Table' \n\
PDIN 0 0 '' pdin CLTT 'Location' '1/R' cltt CLID '' '' clid \n\
TBLE \n\
0 0 '' '3' '2' 135455.423174178 455066.227851273 <
196.965217438059 0 '12' '11' '10' 135473.319683645 455241.69159442 <
391.97895625292 0 '10' '4' '' 135650.055480615 455159.260918116 <
tble grid
GRID id '3' ci '3' gr gr 'GridPoint Table' \n\
PDIN 0 0 '' pdin CLTT 'Location' '1/R' cltt CLID '' '' clid \n\
TBLE \n\
0 0 '' '3' '3' 135455.423174178 455066.227851273 <
111.679498816059 0 '3' '7' '6' 135556.183537484 455114.390696312 <
215.724097483806 0 '13' '4' '' 135650.055480615 455159.260918116 <
tble grid
GRID id 'lkb_grid' ci 'lkb_breach' gr gr 'GridPointTable' \n\
PDIN 0 0 '' pdin CLTT 'Location' '1/R' cltt CLID '' '' clid \n\
TBLE \n\
0 0 '' 'lkb_extern' '23' 134838 455760 <
412.004469957 0 '23' '10' '' 135250.004368634 455759.71157511 <
tble grid
"""
        sobek = File(mock.Stream(input_str))
        output = mock.Stream()
        sobek.writeToStream(output)
        self.assertEqual(''.join(output.content), input_str)

    def test6writing(self):
        "writing a NODE.DAT - one object, no version"
        input_str = """\
NODE id '10' ty 1 ws 10000 ss 0 wl -0.89 ml 0 node
"""
        sobek = File(mock.Stream(input_str))
        output = mock.Stream()
        sobek.writeToStream(output)
        self.assertEqual(''.join(output.content), input_str)

    def test70writing(self):
        "writing a sobek.File to a zip archive gives CRLF line terminators"
        input_str = """\
NODE id '10' ty 1 ws 10000 ss 0 wl -0.89 ml 0 node
"""
        sobek = File(mock.Stream(input_str))
        output = mock.ZipFile()
        sobek.basename = "n1.nod"
        sobek.writeToStream(output)
        sobek.basename = "n2.nod"
        sobek.writeToStream(output)
        output_withCRLF = (input_str + input_str).replace('\n', '\r\n')
        self.assertEqual(''.join(output.content), output_withCRLF)
        self.assertEqual(output.namelist(), ['n1.nod', 'n2.nod'])

    def test71writing(self):
        "writing a sobek.Verbatim to a zip archive"
        input_str = "ND d'0 y1w 00 s0w 08 l0nd"
        sobek = Verbatim(mock.Stream(input_str))
        output = mock.ZipFile()
        sobek.basename = "f1"
        sobek.writeToStream(output)
        sobek.basename = "f2"
        sobek.writeToStream(output)
        self.assertEqual(output.namelist(), ['f1', 'f2'])
        self.assertEqual(''.join(output.content), input_str + input_str)


class AddingRowsToATable(unittest.TestCase):
    input_str = "TBLE tble"
    values = [['2000/01/01;00:00:00', 1],
              ['2000/01/01;06:00:00', 1.9],
              ['2000/01/01;12:00:00', 0.87],
              ['2000/01/01;18:00:00', 2.1],
              ]
    tble_str = """\
TBLE \n\
'2000/01/01;00:00:00' 1 <
'2000/01/01;06:00:00' 1.9 <
'2000/01/01;12:00:00' 0.87 <
'2000/01/01;18:00:00' 2.1 <
tble"""
    named_values = [['0', 1],
                    ['4', 1.9],
                    ['5', 0.87],
                    ['8', 2.1],
                    ]
    named_tble_str = {None: """\
TBLE %s 4 \n\
'0' 1 <
'4' 1.9 <
'5' 0.87 <
'8' 2.1 <
tble""",
                      2: """\
TBLE %s 4 \n\
'0' 1 <
'4' 1.9 <
'5' 0.87 <
'8' 2.1 <
tble""",
                      1: """\
TBLE %s 4 \n\
'0' 1 <
'4' 1.9 <
'5' 0.9 <
'8' 2.1 <
tble""",
                      0: """\
TBLE %s 4 \n\
'0' 1 <
'4' 2 <
'5' 1 <
'8' 2 <
tble""",
                      }
    obj_str = """\
FLBO id 'lkb_condition_extern' ty 0 h_ wt 1 0 0 %sflbo"""

    def test1writing(self):
        "adding values to unnamed table 'by hand'"
        obj = Object(self.input_str)
        for d, v in self.values:
            obj['TBLE'].append(d)
            obj['TBLE'].append(v)
            obj['TBLE'].append('<')
        self.assertEqual(str(obj), self.tble_str)

    def test2writing(self):
        "adding values to unnamed table using the addRow utility function"
        obj = Object(self.input_str)
        for d, v in self.values:
            obj.addRow((d, v))
        self.assertEqual(str(obj), self.tble_str)

    def test4writing(self):
        "addRow without TBLE allowing addition"
        obj = Object(self.obj_str % '')
        for d, v in self.values:
            obj.addRow((d, v))
        self.assertEqual(str(obj), self.obj_str % ('\n' + reindent(self.tble_str) + ' '))

    def test6writing(self):
        "addRow without TBLE not allowing addition causes error"
        obj = Object(self.obj_str % '')
        for d, v in self.values:
            self.assertRaises(AttributeError, obj.addRow, (d, v), False)

    def test7writing(self):
        "if TBLE value is in input, it is associated to a key"
        obj = Object(self.obj_str % 'TBLE tble ')
        for d, v in self.values:
            self.assertRaises(AttributeError, obj.addRow, (d, v), False)
            obj['h_ wt'][3].addRow((d, v), False)
        self.assertEqual(str(obj), self.obj_str % ('\n' + reindent(self.tble_str) + ' '))

    def test80_named(self):
        "addRow to named TBLE - adding table"
        obj = Object(self.obj_str % '')
        for d, v in self.named_values:
            obj.addRow((d, v), to_table='cells')
        self.assertEqual(str(obj), self.obj_str % ('\n' + reindent(self.named_tble_str[None] % 'cells') + ' '))

    def test82_named(self):
        "addRow to named TBLE - adding second table"
        obj = Object(self.obj_str % '')
        for d, v in self.named_values:
            obj.addRow((d, v), to_table='cells')
        for d, v in self.named_values:
            obj.addRow((d, v), to_table='other')
        repr1 = '\n' + reindent(self.named_tble_str[None] % 'cells') + ' '
        repr2 = '\n' + reindent(self.named_tble_str[None] % 'other') + ' '
        self.assertEqual(str(obj), self.obj_str % (repr1 + repr2))

    def test90_named(self):
        "reading back named TBLE"
        obj = Object(tag='TBLE', name='cells')
        for d, v in self.named_values:
            obj.addRow((d, v))
        obj2 = Object(str(obj))
        self.assertEqual(obj.fields, obj2.fields)
        self.assertEqual(str(obj2), str(obj))

    def test91_named(self):
        "reading back an object with one named TBLE"
        obj = Object(self.obj_str % 'TBLE cells 0 tble ')
        for d, v in self.named_values:
            obj['h_ wt'][3].addRow((d, v), to_table='cells')
        self.assertEqual(str(obj), self.obj_str % ('\n' + reindent(self.named_tble_str[None] % 'cells') + ' '))
        obj2 = Object(str(obj))
        self.assertEqual(obj.fields, obj2.fields)
        self.assertEqual(str(obj2), str(obj))

    def test92_named(self):
        "reading back an object with two named TBLEs"
        obj = Object(self.obj_str % '')
        for d, v in self.named_values:
            obj.addRow((d, v), to_table='cells')
        for d, v in self.named_values:
            obj.addRow((d, v), to_table='other')
        repr1 = ('\n' + reindent(self.named_tble_str[None] % 'cells') + ' ')
        repr2 = ('\n' + reindent(self.named_tble_str[None] % 'other') + ' ')
        self.assertEqual(str(obj), self.obj_str % (repr1 + repr2))
        obj2 = Object(str(obj))
        # self.assertEqual(obj.fields, obj2.fields)
        self.assertEqual(str(obj2), str(obj))

    def test930_named(self):
        "addRow to named TBLE - specifying decimal places"
        for decs in [None, 2, 1, 0]:
            obj = Object(self.obj_str % '')
            for d, v in self.named_values:
                obj.addRow((d, v), to_table='cells', decimals=decs)
            self.assertEqual(str(obj), self.obj_str % ('\n' + reindent(self.named_tble_str[decs] % 'cells') + ' '))


class AddingObjectsToFiles(unittest.TestCase):

    input_str = """\
D121.0
DOMN id '1' nm '1'
domn
"""

    def test1(self):
        "reading file and adding one object - append"

        f = File(mock.Stream(self.input_str))
        self.assertEqual(len(f), 1)
        f.append(Object(tag='DOMN', id='2'))
        self.assertEqual(len(f), 2)

    def test2(self):
        "reading file and adding one object - addObject"

        f = File(mock.Stream(self.input_str))
        self.assertEqual(len(f), 1)
        f.addObject(Object(tag='DOMN', id='2'))
        self.assertEqual(len(f), 2)

    def test3(self):
        "reading file, adding one object, retrieving it by id"

        f = File(mock.Stream(self.input_str))
        self.assertEqual(len(f), 1)
        obj = Object(tag='DOMN', id='2')
        f.addObject(obj)
        self.assertEqual(len(f), 2)
        self.assertEqual(f['DOMN', '2'], obj)

    def test4(self):
        "altering object id, retrieving it by new id"

        f = File(mock.Stream(self.input_str))
        obj = f['DOMN', '1']
        obj['id'] = '2'
        self.assertEqual(f['DOMN', '2'], obj)

    def test5(self):
        "altering object id (list), retrieving it by new id"

        f = File(mock.Stream(self.input_str))
        obj = f['DOMN', '1']
        obj['id'] = ['id']
        self.assertEqual(f['DOMN', 'id'], obj)


class VerbatimDoesNothing(unittest.TestCase):

    def test0(self):
        "reading a Verbatim file does not cause errors"
        f = Verbatim(mock.Stream("abcde\n\naaa"))
        self.assertTrue(f != None)

    def test1(self):
        "writing a Verbatim file gets you the input verbatim"
        f = Verbatim(mock.Stream("abcde\n\naaa"))
        output = mock.Stream()
        f.writeToStream(output)
        self.assertEqual(''.join(output.content), "abcde\n\naaa")

    def test2(self):
        "iterating in a Verbatim file gives the empty list"
        f = Verbatim(mock.Stream("abcde"))
        self.assertEqual([i for i in f], [])

    def test3(self):
        "appending to a Verbatim file gives NotImplementedError"
        f = Verbatim(mock.Stream("abcde"))
        self.assertRaises(NotImplementedError, f.append, '1')


class DictionaryLikeAccess(unittest.TestCase):
    input_noversion = """\
GFLS nc 15 nr 15 x0 135000 y0 456500 dx 100 dy 100 cp 0 fnm '\Sobek210\lizardkb.lit\FIXED\grid\test_hoogte.asc' gfls
NODE id '10' ty 1 ws 10000 ss 0 wl -0.89 ml 0 node
PT12 id '7' nm '5' ci '1' lc 99.1349688238926 px 135352.060094798 py 456360.503490938 mc 4 mr 2 pt12
PT12 id '2' nm '2' ci '1' lc 0 px 135451.113212727 py 456364.531129484 mc 5 mr 2 pt12
GRID id '1' ci '1' gr gr 'GridPointTable'
PDIN 0 0 '' pdin CLTT 'Location' '1/R' cltt CLID '' '' clid
TBLE \n\
0 0 '' '2' '1' 135451.113212727 456364.531129484 <
99.1349688238926 0 '1' '5' '4' 135352.060094798 456360.503490938 <
199.443229780832 0 '4' '6' '5' 135253.892598708 456340.348467165 <
tble grid
"""

    def test0(self):
        "get base objects by type - existing gives list"
        f = File(mock.Stream(self.input_noversion))
        self.assertEqual(len(f['PT12']), 2)
        self.assertEqual(len(f['NODE']), 1)
        self.assertEqual(len(f['GFLS']), 1)

    def test1(self):
        "get base objects by type - not existing gives empty list"
        f = File(mock.Stream(self.input_noversion))
        self.assertEqual(len(f['DOMN']), 0)

    def test2(self):
        "get list of types of base objects"
        f = File(mock.Stream(self.input_noversion))
        self.assertEqual(f.keys(), ['GFLS', 'NODE', 'GRID', 'PT12'])

    def test3(self):
        "asking by integer index in File gives i-th contained object"
        f = File(mock.Stream(self.input_noversion))
        self.assertEqual(f[0].tag, 'GFLS')
        self.assertEqual(f[1].tag, 'NODE')
        self.assertEqual(f[2].tag, 'PT12')
        self.assertEqual(f[3].tag, 'PT12')
        self.assertEqual(f[4].tag, 'GRID')
        self.assertRaises(IndexError, f.__getitem__, 5)

    def test31(self):
        "asking by integer index in Object gives i-th included object"
        f = File(mock.Stream("FLBO id 'lkbce' PDIN pdin CLTT cltt CLID clid TBLE tble flbo"))
        self.assertEqual(f['FLBO', 'lkbce'][0].tag, 'PDIN')
        self.assertEqual(f['FLBO', 'lkbce'][1].tag, 'CLTT')
        self.assertEqual(f['FLBO', 'lkbce'][2].tag, 'CLID')
        self.assertEqual(f['FLBO', 'lkbce'][3].tag, 'TBLE')
        self.assertRaises(IndexError, f['FLBO', 'lkbce'].__getitem__, 4)

    def test32(self):
        "included value-objects get appended to current key"
        f = File(mock.Stream(self.input_noversion))
        self.assertEqual(f['GRID', '1']['gr gr'][1].tag, 'PDIN')
        self.assertEqual(f['GRID', '1']['gr gr'][2].tag, 'CLTT')
        self.assertEqual(f['GRID', '1']['gr gr'][3].tag, 'CLID')
        self.assertEqual(f['GRID', '1']['gr gr'][4].tag, 'TBLE')
        self.assertRaises(IndexError, f['GRID', '1']['gr gr'].__getitem__, 5)

    def test4(self):
        "asking impossible sobek name gives ValueError"
        f = File(mock.Stream(self.input_noversion))
        self.assertRaises(ValueError, f.__getitem__, "no")

    def test5(self):
        "asking lower case sobek name gives upper case answer"
        f = File(mock.Stream(self.input_noversion))
        self.assertEqual(f['domn'], f['DOMN'])
        self.assertEqual(f['pt12'], f['PT12'])


class ReadingAndAlteringTables(unittest.TestCase):
    input_str = "TBLE tble"
    values = [
        [0, 0, '', 'c_BOEZ_1', 'c_17', 134808.891822728, 456721.97309417, ],
        [188.779056149839, 0, 'c_17', 'c_BOEZ_5', 'c_20', 134997.326506, 456710.575630373, ],
        [505.605005395534, 0, 'c_25', 'c_BOEZ_6', 'c_21', 135313.574497785, 456691.44738405, ],
        [779.884026046477, 0, 'c_21', 'c_BOEZ_2', '', 135587.353175561, 456674.887892377, ],
        ]
    tble_str = """\
TBLE \n\
0 0 '' 'c_BOEZ_1' 'c_17' 134808.891822728 456721.97309417 <
188.779056149839 0 'c_17' 'c_BOEZ_5' 'c_20' 134997.326506 456710.575630373 <
505.605005395534 0 'c_25' 'c_BOEZ_6' 'c_21' 135313.574497785 456691.44738405 <
779.884026046477 0 'c_21' 'c_BOEZ_2' '' 135587.353175561 456674.887892377 <
tble"""
    obj_str = """\
FLBO id 'lkb_condition_extern' ty 0 h_ wt 1 0 0 %sflbo"""

    def test0(self):
        "TBLE contains list of values accessible by pair of coordinates"
        t = Object(self.tble_str)
        self.assertEqual(t.fields['TBLE'],
                         [0, 0, '', 'c_BOEZ_1', 'c_17', 134808.89182272801, 456721.97309416998, '<',
                          188.77905614983899, 0, 'c_17', 'c_BOEZ_5', 'c_20', 134997.32650600001, 456710.57563037297, '<',
                          505.60500539553402, 0, 'c_25', 'c_BOEZ_6', 'c_21', 135313.57449778501, 456691.44738405, '<',
                          779.88402604647695, 0, 'c_21', 'c_BOEZ_2', '', 135587.353175561, 456674.88789237698, '<',
                          ])

    def test10(self):
        "getting info from the first row of a TBLE"
        t = Object(self.tble_str)
        self.assertEqual(t[0, 0], 0)
        self.assertEqual(t[0, 1], 0)
        self.assertEqual(t[0, 2], '')
        self.assertEqual(t[0, 3], 'c_BOEZ_1')
        self.assertEqual(t[0, 4], 'c_17')
        self.assertEqual(t[0, 5], 134808.891822728)
        self.assertEqual(t[0, 6], 456721.97309417)

    def test15(self):
        "setting info into the first row of a TBLE"
        t = Object(self.tble_str)
        t[0, 3] = "c_1"
        t[0, 4] = "c_2"
        self.assertEqual(t[0, 0], 0)
        self.assertEqual(t[0, 1], 0)
        self.assertEqual(t[0, 2], '')
        self.assertEqual(t[0, 3], 'c_1')
        self.assertEqual(t[0, 4], 'c_2')
        self.assertEqual(t[0, 5], 134808.891822728)
        self.assertEqual(t[0, 6], 456721.97309417)

    def test2(self):
        "accessing by tuple into a non-TBLE gives ValueError"
        nt = Object(self.obj_str % '')
        self.assertRaises(ValueError, nt.__getitem__, (0, 0))

    #def test3(self):
    #    "accessing by non-tuple into a TBLE gives ValueError"
    #    t = Object(self.tble_str)
    #    self.assertRaises(ValueError, t.__getitem__, "")
    #    self.assertRaises(ValueError, t.__getitem__, 0)

    def test4(self):
        "accessing out of range -by row- in a TBLE gives KeyError"
        t = Object(self.tble_str)
        self.assertRaises(KeyError, t.__getitem__, (7, 0))

    def test41(self):
        "accessing out of range -by col- in a TBLE gives KeyError"
        t = Object(self.tble_str)
        self.assertRaises(KeyError, t.__getitem__, (0, 25))

    def test42(self):
        "accessing the '<' of a TBLE gives KeyError"
        t = Object(self.tble_str)
        self.assertRaises(KeyError, t.__getitem__, (0, 7))
        self.assertRaises(KeyError, t.__getitem__, (1, 7))
        self.assertRaises(KeyError, t.__getitem__, (2, 7))

    def test50(self):
        "initialize an empty TBLE specifying the column count"
        t = Object(tag='TBLE', id='44', cols=6)
        self.assertEqual(t.cols(), 6)

    def test52(self):
        "initialize an empty TBLE without specifying the column count"
        t = Object(tag='TBLE', id='44')
        self.assertEqual(t.cols(), None)

    def test54(self):
        "empty TBLE without column count infers it from addRow data"
        t = Object(tag='TBLE', id='44')
        self.assertEqual(t.cols(), None)
        t.addRow([1, 2, 3])
        self.assertEqual(t.cols(), 3)

    def test56(self):
        "TBLE accepts addRow data with correct amount of columns"
        t = Object(tag='TBLE', id='44')
        self.assertEqual(t.cols(), None)
        t.addRow([1, 2, 3])
        self.assertEqual(t.cols(), 3)
        t.addRow([1, 2, 3])

    def test58(self):
        "TBLE addRow with wrong amount of columns raises ValueError"
        t = Object(tag='TBLE', id='44', cols=3)
        self.assertRaises(ValueError, t.addRow, [1, 2, 3, 4])

    def test582(self):
        "TBLE addRow and read new entries by tuple"
        t = Object(tag='TBLE', id='44')
        self.assertEqual(t.cols(), None)
        t.addRow([1, 2, 3])
        self.assertEqual(t[0, 0], 1)
        self.assertEqual(t[0, 1], 2)
        self.assertEqual(t[0, 2], 3)
        t.addRow([4, 5, 6])
        self.assertEqual(t[1, 0], 4)
        self.assertEqual(t[1, 1], 5)
        self.assertEqual(t[1, 2], 6)

    def test584(self):
        "TBLE addRow and alter entries by tuple"
        t = Object(tag='TBLE', id='44')
        self.assertEqual(t.cols(), None)
        t.addRow([1, 2, 3])
        t.addRow([4, 5, 6])
        t.addRow([4, 5, 6])
        t[2, 0] = 7
        t[2, 1] = 8
        t[2, 2] = 9
        self.assertEqual(t[0, 0], 1)
        self.assertEqual(t[0, 1], 2)
        self.assertEqual(t[0, 2], 3)
        self.assertEqual(t[1, 0], 4)
        self.assertEqual(t[1, 1], 5)
        self.assertEqual(t[1, 2], 6)
        self.assertEqual(t[2, 0], 7)
        self.assertEqual(t[2, 1], 8)
        self.assertEqual(t[2, 2], 9)

    def test586(self):
        "TBLE addRow and alter entries by tuple - prints new values"
        t = Object(tag='TBLE')
        t.addRow([1, 2, 3])
        t.addRow([4, 5, 6])
        t.addRow([4, 5, 6])
        t[2, 0] = 7
        t[2, 1] = 8
        t[2, 2] = 9
        self.assertEqual(str(t), """\
TBLE \n\
1 2 3 <
4 5 6 <
7 8 9 <
tble""")

    def test600(self):
        "TBLE counting rows from empty"
        t = Object(tag='TBLE')
        t.addRow([1, 2, 3])
        self.assertEqual(t.rows(), 1)
        t.addRow([4, 5, 6])
        self.assertEqual(t.rows(), 2)
        t.addRow([4, 5, 6])
        self.assertEqual(t.rows(), 3)

    def test601(self):
        "TBLE counting rows from input string"
        t = Object('TBLE 1 2 3 < 2 2 2 < tble')
        self.assertEqual(t.rows(), 2)

    def test610(self):
        "empty TBLE has 0 rows"
        t = Object(tag='TBLE', cols=5)
        self.assertEqual(t.rows(), 0)

    def test620(self):
        "empty TBLE not knowing about its shape has 0 rows"
        t = Object(tag='TBLE')
        self.assertEqual(t.rows(), 0)

    def test650(self):
        "not TBLE raises AttributeError when asking rows count"
        t = Object(tag='DOMN')
        self.assertRaises(AttributeError, t.rows)


class VerbatimFunctions(unittest.TestCase):
    "a few functions available in Verbatim objects"

    def test01replace(self):
        "replace a substring in a Verbatim object"
        f = Verbatim(mock.Stream("abcde"))
        f.replace("bcd", "123")
        output = mock.Stream()
        f.writeToStream(output)
        self.assertEqual(''.join(output.content), "a123e")

    def test02(self):
        "Verbatim file-like behaviour: truncate to 0"
        f = Verbatim(mock.Stream("abcde\n12345\nxyzt"))
        f.truncate(0)
        output = mock.Stream()
        f.writeToStream(output)
        self.assertEqual(''.join(output.content), "")

    def test030(self):
        "Verbatim file-like behaviour: truncate to nonzero raises ValueError"
        f = Verbatim(mock.Stream("abcde\n12345\nxyzt"))
        self.assertRaises(ValueError, f.truncate, 1)

    def test031(self):
        "Verbatim file-like behaviour: truncate and extend"
        f = Verbatim(mock.Stream("abcde\nabcde\n12345\nxyzt\n"))
        f.truncate(0)
        f.write('test')
        output = mock.Stream()
        f.writeToStream(output)
        self.assertEqual(''.join(output.content), "test")

    def test04(self):
        "Verbatim file-like behaviour: write adds to end of buffer"
        f = Verbatim(mock.Stream("abcde\n"))
        output = mock.Stream()
        f.writeToStream(output)
        self.assertEqual(''.join(output.content), "abcde\n")
        f.write("12345\nxyzt")
        output = mock.Stream()
        f.writeToStream(output)
        self.assertEqual(''.join(output.content), "abcde\n12345\nxyzt")

    def test05(self):
        "Verbatim file-like behaviour: can retrieve content using readline"
        f = Verbatim(mock.Stream("abcde\nabcde\n12345\nxyzt\n"))
        self.assertEqual(f.readline(), 'abcde\n')
        self.assertEqual(f.readline(), 'abcde\n')
        self.assertEqual(f.readline(), '12345\n')
        self.assertEqual(f.readline(), 'xyzt\n')


class DeletingItemsFromFile(unittest.TestCase):
    "it is possible to remove items from a sobek.File"
    input = """\
GLIN fi 0 fr '(null)'
FLIN nm '' ss 0 id '-1' ci '-1' lc 999990 q_ lq 0 0 999990 ty 1 lv ll 0 44 999990 flin glin
FLIN nm 'initial' ss 0 id '1' ci '1' lc 999990 q_ lq 0 0 999990 ty 1 lv ll 0 -0.2 999990 flin
FLIN nm 'initial' ss 0 id '2' ci '2' lc 999990 q_ lq 0 0 999990 ty 1 lv ll 0 -0.2 999990 flin
FLIN nm 'initial' ss 0 id '3' ci '3' lc 999990 q_ lq 0 0 999990 ty 1 lv ll 0 -0.2 999990 flin
"""

    def test01(self):
        "delete one item by type and number - existing"
        f = File(mock.Stream(self.input))
        flins = len(f['FLIN'])
        del f['FLIN', 0]
        self.assertEqual(len(f['FLIN']), flins - 1)

    def test02(self):
        "delete one item by type and number - out of range - IndexError"
        f = File(mock.Stream(self.input))
        self.assertRaises(IndexError, f.__delitem__, ('FLIN', 5))

    def test03(self):
        "delete one item by type and id - existing"
        f = File(mock.Stream(self.input))
        flins = len(f['FLIN'])
        del f['FLIN', '2']
        self.assertEqual(len(f['FLIN']), flins - 1)

    def test04(self):
        "delete one item by type and id - not existing - KeyError"
        f = File(mock.Stream(self.input))
        self.assertRaises(KeyError, f.__delitem__, ('FLIN', '4'))

    def test05(self):
        "delete all items by type - existing or not - ValueError"
        f = File(mock.Stream(self.input))
        self.assertRaises(ValueError, f.__delitem__, 'FLIN')
        self.assertRaises(ValueError, f.__delitem__, 'NOPE')


class CreatingFileFromScratch(unittest.TestCase):
    def test01(self):
        "create File object without a source"
        f = File(None)
        self.assertTrue(f != None)

    def test11(self):
        "create File object from non existing file"
        f = File('struct.def')
        self.assertTrue(f != None)


class NoneValuesAreConvertedInOutput(unittest.TestCase):
    def test01(self):
        "a field receiving None stores it using a global setting"
        f = Object("PT12 id '2' nm '2' ci '1' lc 0 pt12")
        f['mc'] = None
        self.assertEqual(f['mc'], [NoneValue])

    def test02(self):
        "a field receiving '' stores it verbatim"
        f = Object("PT12 id '2' nm '2' ci '1' lc 0 pt12")
        f['mc'] = ''
        self.assertEqual(f['mc'], [''])


class ReadingAttributesWithDoubleName(unittest.TestCase):
    def test01(self):
        "can read a sobek string with long attribute names"
        f = Object("STFR id 'fr_KBR_1' mf 1 mt cp 0 71 mr cp 71 s1 6 s2 6 sf 1 st cp 71 sr cp 71 stfr")
        self.assertEqual(f['mf'], [1])
        self.assertEqual(f['mt cp'], [0, 71])
        self.assertEqual(f['mr cp'], [71])


class Ticket319(unittest.TestCase):
    input_no_seps = "D121.0|DOMN id 'Dummy9' nm 'Dummy9' |  GFLS nc 31 nr 36 x0 124878.21251062 y0 486580.70841546 dx 25 dy 25 cp 0 fnm '../WORK/grid/ahn25_dm.asc' gfls |  PT12 id '1' nm '1' ci '' lc 0 px 125230.9669999 py 486354.027000174 mc 15 mr 10 pt12|  PT12 id '183647_1' nm '183647_1' ci '183647' lc 34.3695294843414 px 125253.704736949 py 486379.622994496 mc 16 mr 9 pt12|  PT12 id '183647_2' nm '183647_2' ci '183647' lc 68.7390589695179 px 125276.126426661 py 486405.671563959 mc 16 mr 8 pt12|domn"

    def test01(self):
        "reading versioned file with line separators DOS style"

        f = File(mock.Stream(self.input_no_seps.replace('|', '\n\r')))
        self.assertEqual(f.keys(), ['DOMN'])

    def test02(self):
        "reading versioned file with line separators unix style"

        f = File(mock.Stream(self.input_no_seps.replace('|', '\r')))
        self.assertEqual(f.keys(), ['DOMN'])

    def test03(self):
        "reading versioned file with line separators Mac style"

        f = File(mock.Stream(self.input_no_seps.replace('|', '\n')))
        self.assertEqual(f.keys(), ['DOMN'])


class HISFileFunctions(unittest.TestCase):
    input = 'SOBEK                                   History at calculation points           TITLE :Model_BG                         T0: 2000.01.01 00:00:00  (scu=      20s)\x01\x00\x00\x00\x02\x00\x00\x00     Waterdepth  (m)\x01\x00\x00\x00183184_8            \x02\x00\x00\x00183190_22           \x00\x00\x00\x00\x85\xeb\xd1\xbe\\\x8f\x02\xbf\x84\x03\x00\x00\xaeG\xe1\xbe\x00\x00\x00\xbf\x08\x07\x00\x00ff\xe6\xbe\\\x8f\x02\xbf'

    def test01(self):
        "HISFile: reading file"

        f = HISFile(mock.Stream(self.input))
        self.assertEqual(f.dtstart, datetime.datetime(2000, 1, 1))
        self.assertEqual(f.nrof_parameters, 1)
        self.assertEqual(f.nrof_locations, 2)
        self.assertEqual(f.locations(), ['183184_8', '183190_22'])
        self.assertEqual(f.parameters(), ['Waterdepth  (m)'])
        self.assertEqual(f.size(), 3)

    def test03(self):
        "HISFile: get_values for one location/parameter"
        f = HISFile(mock.Stream(self.input))
        self.assertEqual(f.get_values('183184_8', 'Waterdepth  (m)'), [-0.41, -0.44, -0.45])

    def test05(self):
        "HISFile: get_timestamps for one location/parameter"
        f = HISFile(mock.Stream(self.input))
        self.assertEqual(f.get_timestamps(),
                         [datetime.datetime(2000, 1, 1, 0, 0, 0),
                          datetime.datetime(2000, 1, 1, 5, 0, 0),
                          datetime.datetime(2000, 1, 1, 10, 0, 0),
                          ])

    def test07(self):
        "HISFile: get_timeseries for one location/parameter, complete"
        f = HISFile(mock.Stream(self.input))
        self.assertEqual(f.get_timeseries('183184_8', 'Waterdepth  (m)'),
                         {datetime.datetime(2000, 1, 1, 0, 0): -0.41,
                          datetime.datetime(2000, 1, 1, 5, 0): -0.44,
                          datetime.datetime(2000, 1, 1, 10, 0): -0.45})

    def test09(self):
        "HISFile: get_timeseries for one location/parameter, from second"
        f = HISFile(mock.Stream(self.input))
        self.assertEqual(f.get_timeseries('183184_8', 'Waterdepth  (m)', 946684801),
                         {datetime.datetime(2000, 1, 1, 5, 0): -0.44,
                          datetime.datetime(2000, 1, 1, 10, 0): -0.45})

    def test11(self):
        "HISFile: get_timeseries for one location/parameter, from datetime.datetime"
        f = HISFile(mock.Stream(self.input))
        self.assertEqual(f.get_timeseries('183184_8', 'Waterdepth  (m)', datetime.datetime(2000, 1, 1, 6, 0)),
                         {datetime.datetime(2000, 1, 1, 10, 0): -0.45})

    def test15(self):
        "HISFile: get_timeseries as a list of tuples"
        f = HISFile(mock.Stream(self.input))
        self.assertEqual(f.get_timeseries('183184_8', 'Waterdepth  (m)', datetime.datetime(2000, 1, 1, 6, 0), result_type=list),
                         [(datetime.datetime(2000, 1, 1, 10, 0), -0.45)])

    def test51(self):
        "HISFile: get_timeseries for imprecise location/parameter issues warning"
        handler.flush()
        handler.setLevel(20)
        f = HISFile(mock.Stream(self.input))
        self.assertEqual(f.get_timeseries('183184_8', 'Waterdepth'),
                         {datetime.datetime(2000, 1, 1, 0, 0): -0.41,
                          datetime.datetime(2000, 1, 1, 5, 0): -0.44,
                          datetime.datetime(2000, 1, 1, 10, 0): -0.45})
        self.assertEqual(handler.content, ["nens.sobek|WARNING|you asked for parameter 'Waterdepth', you got 'Waterdepth  (m)'."])


class NetworkDecoding(unittest.TestCase):
    input_str = '''\
"NTW6.6","C:\SOBEK211\TAUW.lit\CMTWORK\ntrpluv.ini","SOBEK-LITE-3B, edit network"
"WL_351_1","WL_351_1",1,1,"SBK_CHANNEL","",0,0,0,0,85.3504190152846,0,0,0,"4","","",1,12,"SBK_CHANNELCONNECTION","",181252.9,488342.074,0,0,"SYS_DEFAULT",0,"LOC_R40","LOC_R40","",1,20,"SBK_PROFILE","",181315.478165453,488379.054838942,0,85.3504190152846,"SYS_DEFAULT",0
"WL_353_1","WL_353_1",2,1,"SBK_CHANNEL","",0,0,0,0,24.0902312151046,0,0,0,"7","","",2,12,"SBK_CHANNELCONNECTION","",181753.474,488714.798,0,0,"SYS_DEFAULT",0,"LOC_201","LOC_201","",2,20,"SBK_PROFILE","",181737.652,488732.964,0,24.0902312151046,"SYS_DEFAULT",0
"WL_354_1","WL_354_1",3,1,"SBK_CHANNEL","",0,0,0,0,18.3010214195775,0,0,0,"5","","",0,12,"SBK_CHANNELCONNECTION","",181724.76,488753.474,0,0,"SYS_DEFAULT",0,"LOC_D01","LOC_D01","",3,20,"SBK_PROFILE","",181731.773,488770.378,0,18.3010214195775,"SYS_DEFAULT",0
"WL_355_1","WL_355_1",4,1,"SBK_CHANNEL","",0,0,0,0,.612875094882207,0,0,0,"8","","",0,12,"SBK_CHANNELCONNECTION","",181825.397,488850.43,0,0,"SYS_DEFAULT",0,"LOC_203","LOC_203","",4,20,"SBK_PROFILE","",181825.893202299,488850.789720948,0,.612875094882207,"SYS_DEFAULT",0
"WL_356_1","WL_356_1",5,1,"SBK_CHANNEL","",0,0,0,0,.568225085529253,0,0,0,"8","","",0,12,"SBK_CHANNELCONNECTION","",181825.397,488850.43,0,0,"SYS_DEFAULT",0,"LOC_202","LOC_202","",5,20,"SBK_PROFILE","",181825.965013713,488850.414502591,0,.568225085529253,"SYS_DEFAULT",0
"WL_357_1","WL_357_1",6,1,"SBK_CHANNEL","",0,0,0,0,.350844684788141,0,0,0,"9","","",0,12,"SBK_CHANNELCONNECTION","",181826.844,488851.479,0,0,"SYS_DEFAULT",0,"LOC_D21","LOC_D21","",6,20,"SBK_PROFILE","",181827.128049734,488851.6849314,0,.350844684788141,"SYS_DEFAULT",0
"WL_355_s1","",4,1,"SBK_CHANNEL","",0,0,0,0,.900711845416477,0,0,0,"DU_68","DU_68","",4,24,"SBK_CULVERT","",181826.114756322,488850.950336131,0,.886523449704097,"SYS_DEFAULT",0,"9","","",0,12,"SBK_CHANNELCONNECTION","",181826.844,488851.479,0,0,"SYS_DEFAULT",0
"WL_357_s1","",6,1,"SBK_CHANNEL","",0,0,0,0,44.9573115854777,0,0,0,"DU_4","DU_4","",6,24,"SBK_CULVERT","",181903.073057648,489295.266858857,0,467.811997465847,"SYS_DEFAULT",0,"DU_5","DU_5","",6,24,"SBK_CULVERT","",181898.174729063,489335.49522329,0,512.769309051325,"SYS_DEFAULT",0
"WL_357_s2","",6,1,"SBK_CHANNEL","",0,0,0,0,12.1345791425794,0,0,0,"DU_5","DU_5","",6,24,"SBK_CULVERT","",181898.174729063,489335.49522329,0,512.769309051325,"SYS_DEFAULT",0,"DU_6","DU_6","",6,24,"SBK_CULVERT","",181900.337947165,489344.306968456,0,524.903888193904,"SYS_DEFAULT",0
"WL_357_s3","",6,1,"SBK_CHANNEL","",0,0,0,0,22.614281198018,0,0,0,"DU_6","DU_6","",6,24,"SBK_CULVERT","",181900.337947165,489344.306968456,0,524.903888193904,"SYS_DEFAULT",0,"LOC_6","LOC_6","",6,20,"SBK_PROFILE","",181889.542877499,489364.161938347,0,547.518169391922,"SYS_DEFAULT",0
"WL_357_s4","",6,1,"SBK_CHANNEL","",0,0,0,0,7.6688758532049,0,0,0,"LOC_6","LOC_6","",6,20,"SBK_PROFILE","",181889.542877499,489364.161938347,0,547.518169391922,"SYS_DEFAULT",0,"10","","",6,12,"SBK_CHANNELCONNECTION","",181886.2,489371.059,0,555.187045245127,"SYS_DEFAULT",0
"WL_357_s5","",6,1,"SBK_CHANNEL","",0,0,0,0,61.0431251571269,0,0,0,"LOC_5","LOC_5","",6,20,"SBK_PROFILE","",181895.173592905,489236.837030347,0,406.768872308721,"SYS_DEFAULT",0,"DU_4","DU_4","",6,24,"SBK_CULVERT","",181903.073057648,489295.266858857,0,467.811997465847,"SYS_DEFAULT",0
"WL_351_s1","",1,1,"SBK_CHANNEL","",0,0,0,0,69.612970270265,0,0,0,"LOC_R40","LOC_R40","",1,20,"SBK_PROFILE","",181315.478165453,488379.054838942,0,85.3504190152846,"SYS_DEFAULT",0,"LOC_R43","LOC_R43","",1,20,"SBK_PROFILE","",181369.977075031,488421.706884734,0,154.96338928555,"SYS_DEFAULT",0
"WL_351_s2","",1,1,"SBK_CHANNEL","",0,0,0,0,218.178858401499,0,0,0,"LOC_R43","LOC_R43","",1,20,"SBK_PROFILE","",181369.977075031,488421.706884734,0,154.96338928555,"SYS_DEFAULT",0,"LOC_R50","LOC_R50","",1,20,"SBK_PROFILE","",181544.705711699,488490.050269125,0,373.142247687049,"SYS_DEFAULT",0
"WL_351_s3","",1,1,"SBK_CHANNEL","",0,0,0,0,42.2760490100177,0,0,0,"LOC_R50","LOC_R50","",1,20,"SBK_PROFILE","",181544.705711699,488490.050269125,0,373.142247687049,"SYS_DEFAULT",0,"LOC_R53","LOC_R53","",1,20,"SBK_PROFILE","",181573.554,488520.954,0,415.418296697066,"SYS_DEFAULT",0
"WL_351_s4","",1,1,"SBK_CHANNEL","",0,0,0,0,68.0174365247107,0,0,0,"LOC_R53","LOC_R53","",1,20,"SBK_PROFILE","",181573.554,488520.954,0,415.418296697066,"SYS_DEFAULT",0,"LOC_R56","LOC_R56","",1,20,"SBK_PROFILE","",181574.503906285,488585.523130178,0,483.435733221777,"SYS_DEFAULT",0
"WL_351_s5","",1,1,"SBK_CHANNEL","",0,0,0,0,93.6881553376135,0,0,0,"LOC_R56","LOC_R56","",1,20,"SBK_PROFILE","",181574.503906285,488585.523130178,0,483.435733221777,"SYS_DEFAULT",0,"LOC_R60","LOC_R60","",1,20,"SBK_PROFILE","",181614.35592023,488651.244970215,0,577.123888559391,"SYS_DEFAULT",0
"WL_351_s6","",1,1,"SBK_CHANNEL","",0,0,0,0,94.0130642584541,0,0,0,"LOC_R60","LOC_R60","",1,20,"SBK_PROFILE","",181614.35592023,488651.244970215,0,577.123888559391,"SYS_DEFAULT",0,"LOC_R65","LOC_R65","",1,20,"SBK_PROFILE","",181656.259,488716.423,0,671.136952817845,"SYS_DEFAULT",0
"WL_351_s7","",1,1,"SBK_CHANNEL","",0,0,0,0,74.8326200149762,0,0,0,"LOC_R65","LOC_R65","",1,20,"SBK_PROFILE","",181656.259,488716.423,0,671.136952817845,"SYS_DEFAULT",0,"LOC_R69","LOC_R69","",1,20,"SBK_PROFILE","",181719.256897851,488747.324091406,0,745.969572832821,"SYS_DEFAULT",0
"WL_351_s8","",1,1,"SBK_CHANNEL","",0,0,0,0,8.2526061930057,0,0,0,"LOC_R69","LOC_R69","",1,20,"SBK_PROFILE","",181719.256897851,488747.324091406,0,745.969572832821,"SYS_DEFAULT",0,"5","","",0,12,"SBK_CHANNELCONNECTION","",181724.76,488753.474,0,0,"SYS_DEFAULT",0
"WL_354_s1","",3,1,"SBK_CHANNEL","",0,0,0,0,125.121001711554,0,0,0,"LOC_D01","LOC_D01","",3,20,"SBK_PROFILE","",181731.773,488770.378,0,18.3010214195775,"SYS_DEFAULT",0,"LOC_D12","LOC_D12","",3,20,"SBK_PROFILE","",181825.063728081,488850.188375056,0,143.422023131132,"SYS_DEFAULT",0
"WL_357_s6","",6,1,"SBK_CHANNEL","",0,0,0,0,13.6738723393493,0,0,0,"LOC_D02","LOC_D02","",6,20,"SBK_PROFILE","",181894.157084806,489223.200993678,0,393.094999969371,"SYS_DEFAULT",0,"LOC_5","LOC_5","",6,20,"SBK_PROFILE","",181895.173592905,489236.837030347,0,406.768872308721,"SYS_DEFAULT",0
"WL_353_s1","",2,1,"SBK_CHANNEL","",0,0,0,0,24.2252711853396,0,0,0,"LOC_201","LOC_201","",2,20,"SBK_PROFILE","",181737.652,488732.964,0,24.0902312151046,"SYS_DEFAULT",0,"5","","",0,12,"SBK_CHANNELCONNECTION","",181724.76,488753.474,0,0,"SYS_DEFAULT",0
"WL_356_s1","",5,1,"SBK_CHANNEL","",0,0,0,0,.51666052002914,0,0,0,"LOC_202","LOC_202","",5,20,"SBK_PROFILE","",181825.965013713,488850.414502591,0,.568225085529253,"SYS_DEFAULT",0,"ST_3","P1695","",5,21,"SBK_WEIR","",181826.440931405,488850.541102778,0,1.08488560555839,"SYS_DEFAULT",0
"WL_355_s2","",4,1,"SBK_CHANNEL","",0,0,0,0,.273648354821889,0,0,0,"LOC_203","LOC_203","",4,20,"SBK_PROFILE","",181825.893202299,488850.789720948,0,.612875094882207,"SYS_DEFAULT",0,"DU_68","DU_68","",4,24,"SBK_CULVERT","",181826.114756322,488850.950336131,0,.886523449704097,"SYS_DEFAULT",0
"WL_357_s7","",6,1,"SBK_CHANNEL","",0,0,0,0,392.744155284583,0,0,0,"LOC_D21","LOC_D21","",6,20,"SBK_PROFILE","",181827.128049734,488851.6849314,0,.350844684788141,"SYS_DEFAULT",0,"LOC_D02","LOC_D02","",6,20,"SBK_PROFILE","",181894.157084806,489223.200993678,0,393.094999969371,"SYS_DEFAULT",0
"WL_354_s2","",3,1,"SBK_CHANNEL","",0,0,0,0,.411646432732681,0,0,0,"LOC_D12","LOC_D12","",3,20,"SBK_PROFILE","",181825.063728081,488850.188375056,0,143.422023131132,"SYS_DEFAULT",0,"8","","",0,12,"SBK_CHANNELCONNECTION","",181825.397,488850.43,0,0,"SYS_DEFAULT",0
"WL_356_s2","",5,1,"SBK_CHANNEL","",0,0,0,0,1.08668195964856,0,0,0,"ST_3","P1695","",5,21,"SBK_WEIR","",181826.440931405,488850.541102778,0,1.08488560555839,"SYS_DEFAULT",0,"9","","",0,12,"SBK_CHANNELCONNECTION","",181826.844,488851.479,0,0,"SYS_DEFAULT",0
"*"

[Reach description]

 6
"WL_351","WL_351","4","5",4,24,181252.9,488331.892,181724.76,488753.474,754.222179025827,0,50,-1
"WL_353","WL_353","7","5",6,3,181724.76,488714.798,181753.474,488753.474,48.3155024004441,0,50,-1
"WL_354","WL_354","5","8",7,4,181724.76,488753.474,181825.397,488850.43,143.833669563864,0,50,-1
"WL_355","WL_355","8","9",8,2,181825.397,488850.43,181826.844,488851.479,1.78723529512057,0,50,-1
"WL_356","WL_356","8","9",9,4,181825.397,488850.407,181826.844,488851.479,2.17156756520695,0,50,-1
"WL_357","WL_357","9","10",10,19,181826.844,488851.479,181907.686,489371.059,555.187045245127,0,50,-1

[Model connection node]
"1.00"
59,4
12,"SBK_CHANNELCONNECTION","",1,"SOBEK","4"
20,"SBK_PROFILE","",3,"SOBEK","5","SOBEK","16","SOBEK","21"
21,"SBK_WEIR","",2,"SOBEK","6","RTC","1"
24,"SBK_CULVERT","",2,"SOBEK","70","RTC","1"

[Model connection branch]
"1.00"
22,1
1,"SBK_CHANNEL","",2,"SOBEK","0","SOBEK","31"

[Nodes with calculationpoint]
"1.00"
5
"DU_68"
"DU_4"
"DU_5"
"DU_6"
"ST_3"

[Reach options]
"1.00"
0

[NTW properties]
"1.00"
3
v1=4
v2=0
v3=970
'''
    value = {'SBK_CULVERT': {('DU_4', '181903.073057648', '489295.266858857'): True,
                             ('DU_68', '181826.114756322', '488850.950336131'): True,
                             ('DU_6', '181900.337947165', '489344.306968456'): True,
                             ('DU_5', '181898.174729063', '489335.49522329'): True,
                             },
             'SBK_PROFILE': {('LOC_R69', '181719.256897851', '488747.324091406'): True,
                             ('LOC_D01', '181731.773', '488770.378'): True,
                             ('LOC_R53', '181573.554', '488520.954'): True,
                             ('LOC_R60', '181614.35592023', '488651.244970215'): True,
                             ('LOC_201', '181737.652', '488732.964'): True,
                             ('LOC_5', '181895.173592905', '489236.837030347'): True,
                             ('LOC_203', '181825.893202299', '488850.789720948'): True,
                             ('LOC_R40', '181315.478165453', '488379.054838942'): True,
                             ('LOC_D12', '181825.063728081', '488850.188375056'): True,
                             ('LOC_R56', '181574.503906285', '488585.523130178'): True,
                             ('LOC_6', '181889.542877499', '489364.161938347'): True,
                             ('LOC_R65', '181656.259', '488716.423'): True,
                             ('LOC_R50', '181544.705711699', '488490.050269125'): True,
                             ('LOC_D02', '181894.157084806', '489223.200993678'): True,
                             ('LOC_D21', '181827.128049734', '488851.6849314'): True,
                             ('LOC_R43', '181369.977075031', '488421.706884734'): True,
                             ('LOC_202', '181825.965013713', '488850.414502591'): True,
                             },
             'SBK_WEIR': {('ST_3', '181826.440931405', '488850.541102778'): True,
                          },
             'SBK_CHANNELCONNECTION': {('4', '181252.9', '488342.074'): True,
                                       ('5', '181724.76', '488753.474'): True,
                                       ('7', '181753.474', '488714.798'): True,
                                       ('8', '181825.397', '488850.43'): True,
                                       ('9', '181826.844', '488851.479'): True,
                                       ('10', '181886.2', '489371.059'): True,
                                       },
             }

    def test01(self):
        "Network: object behaves as a dictionary"

        nn = Network(mock.Stream(self.input_str))
        for key, value in self.value.items():
            self.assertEqual(nn[key], value)

    def test11(self):
        "Network: crash on non existing file"

        self.assertRaises(IOError, Network, '/bin/not.existing.file.test')

    def test21(self):
        "Network: test connections in obsolete form"

        nn = Network(mock.Stream(self.input_str))
        self.assertTrue('SBK_CHANNEL' in nn)
        self.assertTrue(len(nn['SBK_CHANNEL']) > 0)
        for link_id, from_obj, to_obj in nn['SBK_CHANNEL']:
            (from_type, from_id) = from_obj
            (to_type, to_id) = to_obj
            from_x, from_y = nn.dict[from_type][from_id]
            to_x, to_y = nn.dict[to_type][to_id]
            self.assertTrue((from_id, from_x, from_y) in nn[from_type])
            self.assertTrue((to_id, to_x, to_y) in nn[to_type])

    def test22(self):
        "Network: test connections in compact form"

        nn = Network(mock.Stream(self.input_str))
        self.assertTrue('SBK_CHANNEL' in nn.dict)
        self.assertTrue(len(nn.dict['SBK_CHANNEL']) > 0)
        for link_id in nn.dict['SBK_CHANNEL']:
            (from_type, from_id), (to_type, to_id) = nn.dict['SBK_CHANNEL'][link_id]
            from_x, from_y = nn.dict[from_type][from_id]
            to_x, to_y = nn.dict[to_type][to_id]
            self.assertTrue((from_id, from_x, from_y) in nn[from_type])
            self.assertTrue((to_id, to_x, to_y) in nn[to_type])


class DoctestRunner(unittest.TestCase):
    def test0000(self):
        import doctest
        doctest.testmod(name=__name__[:-6])

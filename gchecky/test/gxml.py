import unittest

from gchecky import gxml

class XmlNodeTestCase(unittest.TestCase):
    def setUp(self):
        class A(gxml.Node):
            a = gxml.String('a', default='aa')
            b = gxml.String('b', required=False)
        self.A = A
        self.a = A()
        class B(A):
            c = gxml.String('c', required=True, values=('cc1', 'cc2'))
        self.B = B
        self.b = B()
    def testClassFields(self):
        assert (self.A.fields().keys() == ['a','b'])
    def testSubclassFields(self):
        fnames = self.B.fields().keys()
        fnames.sort()
        assert (fnames == ['a','b','c'])
    def testObjectValues(self):
        assert self.a.a == 'aa', 'Default value is not set to a field'
        assert self.a.b == None, 'None is not set to a non-required field'
    def testSubObjectValues(self):
        assert self.b.a == self.a.a and self.b.b == self.a.b, ''
        assert self.b.c == 'cc1', 'None is not set to a non-required field'

def xmlNodeSuite():
    suite = unittest.TestSuite()
    suite.addTest(XmlNodeTestCase('testClassFields'))
    suite.addTest(XmlNodeTestCase('testSubclassFields'))
    suite.addTest(XmlNodeTestCase('testObjectValues'))
    suite.addTest(XmlNodeTestCase('testSubObjectValues'))
    return suite

class XmlFieldTestCase(unittest.TestCase):
    def testDeconstructPath(self):
        """Test Field.deconstruct_path method"""
        assert gxml.Field.deconstruct_path('/') == ([], None)
        assert gxml.Field.deconstruct_path('//') == ([], None)
        assert gxml.Field.deconstruct_path('aa') == (['aa'], None)
        assert gxml.Field.deconstruct_path('/aa') == (['aa'], None)
        assert gxml.Field.deconstruct_path('aa/') == (['aa'], None)
        assert gxml.Field.deconstruct_path('/aa/') == (['aa'], None)
        assert gxml.Field.deconstruct_path('aa/bb/cc') == (['aa', 'bb', 'cc'], None)
        assert gxml.Field.deconstruct_path('a/b/c') == (['a', 'b', 'c'], None)
        assert gxml.Field.deconstruct_path('@bb') == ([], 'bb')
        assert gxml.Field.deconstruct_path('@b') == ([], 'b')
        assert gxml.Field.deconstruct_path('/@bb') == ([], 'bb')
        assert gxml.Field.deconstruct_path('//@bb') == ([], 'bb')
        assert gxml.Field.deconstruct_path('aa/@bb') == (['aa'], 'bb')
        assert gxml.Field.deconstruct_path('/aa/@bb') == (['aa'], 'bb')
        assert gxml.Field.deconstruct_path('aa/bb/@cc') == (['aa', 'bb'], 'cc')

    import gxml
    def testAnyFieldXml(self):
        class any_field_test_t(gxml.Document):
            tag_name = 'any-field-test-document'
            any1 = gxml.Any('any1', required=False)
            any2 = gxml.Any('any2', required=True)
            any3 = gxml.Any('any3')
            any4 = gxml.Any('any4')
            any5 = gxml.Any('any5', save_node_and_xml=True)
            any6 = gxml.Any('any6', save_node_and_xml=True)

        from xml.dom.Document import Node as XmlNode
        src = any_field_test_t(
                  any1=None,
                  any2='string',
                  any3=u'unicode_str',
                  any4=('tupe', 'with', 'values', 11, 1.5),
                  any5=('tuple', ('of', ((u'nested',), 'tuples'))),
                  any6={'some':'dictionary', u'with':u'values', 'aa':17})
        result = gxml.Document.fromxml(src.toxml())
        self.ensure_result_equals_source(result, src)
        assert isinstance(result.any5_dom, XmlNode)
        assert unicode(result.any5_xml) == result.any5_xml
        assert isinstance(result.any6_dom, XmlNode)
        assert unicode(result.any6_xml) == result.any6_xml
        return True
    def testZipFieldXml(self):
        class zip_field_test_t(gxml.Document):
            tag_name = 'zip-field-test-document'
            any1 = gxml.Zip('zip1', complete=False)
            any2 = gxml.Zip('zip2', complete=False)
            any3 = gxml.Zip('zip3', complete=False)
            any4 = gxml.Zip('zip4', complete=False)
            any5 = gxml.Zip('zip5', complete=True)
            any6 = gxml.Zip('zip6', complete=True)

        from xml.dom.Document import Node as XmlNode
        src = zip_field_test_t(
                  any1='10014-3433',
                  any2='10014-34*',
                  any3='10014-*',
                  any4='1001*',
                  any5='10014-34',
                  any6='75001'
                  )
        result = gxml.Document.fromxml(src.toxml())
        self.ensure_result_equals_source(result, src)
        return True
    def ensure_result_equals_source(self, result, source):
        for fname in vars(source):
            equals = hasattr(result, fname) and getattr(source, fname) == getattr(result, fname)
            assert equals, 'Field %s content does not match: "%s" vs "%s"' % (
                              fname,
                              getattr(source, fname),
                              getattr(source, fname, None)
                              )
def xmlFieldSuite():
    suite = unittest.TestSuite()
    suite.addTest(XmlFieldTestCase('testDeconstructPath'))
    suite.addTest(XmlFieldTestCase('testAnyFieldXml'))
    suite.addTest(XmlFieldTestCase('testZipFieldXml'))
    return suite

if __name__ == '__main__':
    unittest.main()


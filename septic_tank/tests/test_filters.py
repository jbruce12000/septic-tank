#!/usr/bin/env python
import unittest
from unittest import TestCase
from filters import LCFilter, RemoveFieldsFilter, GrepFilter, ZuluDateFilter, UniqFilter, AddFieldsFilter

class AddFieldsFilterTestCase(TestCase):
    def setUp(self):
        self.data = { 'key1' : 'val1' }

    def test_execute_none(self):
        aff = AddFieldsFilter()
        self.assertIsNone(aff.execute(None))

    def test_execute_fields_not_dict(self):
        aff = AddFieldsFilter(fields=[])
        self.assertEqual(aff.execute('unchanged'),'unchanged')

    def test_execute(self):
        aff = AddFieldsFilter(fields={'key2': 'val2','key3': 'val3'})
        out = aff.execute(self.data)
        self.assertEqual(out['key1'],'val1')
        self.assertEqual(out['key2'],'val2')
        self.assertEqual(out['key3'],'val3')

class UniqFilterTestCase(TestCase):
    def setUp(self):
        self.uf = UniqFilter()
        self.data = { 'key1' : 'val1', 'key2' : 'val2', 'key3' : 'val3' }

    def test_execute(self):
        hashed = 'c30161b2cdef35914690b0d42461eca7'
        self.assertEqual(self.uf.execute(self.data)['id'],hashed)
        # this is duplicated on purpose to make sure hashing many times
        # does not change the hash
        self.assertEqual(self.uf.execute(self.data)['id'],hashed)

    def test_execute_ignore_fields(self):
        self.uf = UniqFilter(ignore=['key3','blah'])
        self.data2 = { 'key1' : 'val1', 'key2' : 'val2'}
        self.uf2 = UniqFilter()
        self.assertEqual(self.uf.execute(self.data)['id'],
                         self.uf2.execute(self.data2)['id'])

class LCFilterTestCase(TestCase):
    def setUp(self):
        self.lcf = LCFilter()
        self.data = { 'field1' : 'VALUE1', 
                      'field2' : 'VaLuE2', 
                      'field3' : 'VALUE3' }

    def test_all_fields(self):
        lc = self.lcf.execute(self.data)
        self.assertEqual(lc['field1'],'value1')
        self.assertEqual(lc['field2'],'value2')
        self.assertEqual(lc['field3'],'value3')

    def test_subset_of_fields(self):
        self.lcf = LCFilter(fields=['field2','field1'])
        lc = self.lcf.execute(self.data)
        self.assertEqual(lc['field1'],'value1')
        self.assertEqual(lc['field2'],'value2')
        self.assertEqual(lc['field3'],'VALUE3')

    def test_bad_field(self):
        self.lcf = LCFilter(fields=['bad','field1'])
        lc = self.lcf.execute(self.data)
        self.assertEqual(lc['field1'],'value1')
        self.assertEqual(lc['field2'],'VaLuE2')
        self.assertEqual(lc['field3'],'VALUE3')

class RemoveFieldsFilterTestCase(TestCase):
    def test_execute(self):
        rff = RemoveFieldsFilter(fields=['field2','field3'])
        data = { 'field1' : 'here', 'field2' : 'I', 'field3' : 'am' }
        rff.execute(data)
        self.assertEqual('field2' in data, False)
        self.assertEqual('field1' in data, True)
        self.assertEqual('field3' in data, False)

class GrepFilterTestCase(TestCase):
    def setUp(self):
        self.data = { 'field1' : 'here', 'field2' : 'I', 'field3' : 'am' }

    def test_reverse_grep_string_no_match(self):
        gf = GrepFilter(regex='nomatch', reverse=True)
        string = 'testing a string'
        self.assertEqual(gf.execute(string),string)

    def test_reverse_grep_string_match(self):
        gf = GrepFilter(regex='a string', reverse=True)
        string = 'testing a string'
        self.assertNotEqual(gf.execute(string),string)

    def test_grep_string_match(self):
        gf = GrepFilter(regex='a string')
        string = 'testing a string'
        self.assertEqual(gf.execute(string),string)

    def test_grep_string_no_match(self):
        gf = GrepFilter(regex='nomatch')
        string = 'testing a string'
        self.assertNotEqual(gf.execute(string),string)

    def test_search_all_fields_match(self):
        gf = GrepFilter(regex='ere.*')
        self.assertNotEqual(gf.execute(self.data),None)

    def test_search_all_fields_no_match(self):
        gf = GrepFilter(regex='123')
        self.assertEqual(gf.execute(self.data),None)

    def test_search_fields_match(self):
        gf = GrepFilter(regex='ere.*',fields=['field1'])
        self.assertNotEqual(gf.execute(self.data),None)

    def test_search_fields_no_match(self):
        gf = GrepFilter(regex='123',fields=['field1'])
        self.assertEqual(gf.execute(self.data),None)

    def test_bad_field_no_keyerror(self):
        gf = GrepFilter(regex='123',fields=['notafield'])
        self.assertNotEqual(gf.execute(self.data),None)

    def test_reverse_grep_dict_no_fields(self):
        gf = GrepFilter(regex='123',reverse=True)
        self.assertEqual(gf.execute(self.data),None)

    def test_reverse_grep_dict_match(self):
        gf = GrepFilter(regex='h.*re',fields=['field1'],reverse=True)
        self.assertEqual(gf.execute(self.data),None)

    def test_reverse_grep_dict_no_match(self):
        gf = GrepFilter(regex='nomatch',fields=['field2'],reverse=True)
        self.assertNotEqual(gf.execute(self.data),None)

class ZuluDateFilterTestCase(TestCase):
    def test_execute(self):
        z = ZuluDateFilter(fields=['date'])
        data = z.execute({ 'date' : '2011-01-02 11:24:57,362' })
        self.assertEqual(data['date'],'2011-01-02T16:24:57Z')

        z = ZuluDateFilter(fields=['date'],informat ="%Y-%m-%d %H:%M:%S")
        data = z.execute({ 'date' : '2011-01-02 11:24:57' })
        self.assertEqual(data['date'],'2011-01-02T16:24:57Z')

        z = ZuluDateFilter(fields=['date'],informat ="%Y-%m-%d %H:%M")
        data = z.execute({ 'date' : '2011-01-02 11:24' })
        self.assertEqual(data['date'],'2011-01-02T16:24:00Z')

        z = ZuluDateFilter(fields=['date'],informat ="%Y-%m-%d %H:%M",outformat="%Y-%m-%d")
        data = z.execute({ 'date' : '2011-01-02 11:24' })
        self.assertEqual(data['date'],'2011-01-02')

if __name__ == '__main__':
    unittest.main()

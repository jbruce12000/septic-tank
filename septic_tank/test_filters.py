#!/usr/bin/env python
import unittest
from unittest import TestCase
from filters import LCFilter, RemoveFieldsFilter, GrepFilter, ZuluDateFilter, UniqFilter

class UniqFilterTestCase(TestCase):
    def setUp(self):
        self.uf = UniqFilter()
        self.data = { 'key1' : 'val1', 'key2' : 'val2', 'key3' : 'val3' }

    def test_execute(self):
        hashed = 'e16e52079dc94c9a05ed3ae1da5e3f48'
        self.assertEqual(self.uf.execute(self.data)['id'],hashed)
        # this is duplicated on purpose to make sure hashing many times
        # does not change the hash
        self.assertEqual(self.uf.execute(self.data)['id'],hashed)

    def test_flatten_dict(self):
        flat = 'key1val1key2val2key3val3'
        self.assertEqual(self.uf.flatten_dict(self.data),flat)

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

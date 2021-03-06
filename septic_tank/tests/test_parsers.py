#!/usr/bin/env python
import unittest
from unittest import TestCase
from parsers import RegexExpander, RegexParser, CSVParser
import re

class RegexExpanderTestCase(TestCase):

    def test_regex_expander_infinite_loop(self):
        regs = {
            'short' : '(?P<team>\w+){{long}}',
            'long' : '(?P<action>(get|post|head){{short}}',
            }
        self.assertRaises(Exception, RegexExpander, regs=regs)

    def test_key_exists(self):
        regs = {
            'one' : 'this is a {{two}} string',
            'two' : 'longer',
            }
        r = RegexExpander(regs=regs)
        self.assertEqual(r.regs['one'],'this is a longer string')

    def test_key_does_not_exist(self):
        regs = {
            'one' : 'has a reference that does not exist {{four}}',
            }
        self.assertRaises(Exception, RegexExpander, regs=regs)

    def test_recursion_works(self):
        regs = {
            'one' : 'this is a {{two}} string',
            'two' : '{{three}} long',
            'three' : 'super',
            }
        r = RegexExpander(regs=regs)
        self.assertEqual(r.regs['one'],'this is a super long string')

    def test_three_braces(self):
        '''
        {{{ was causing key errors
        '''
        regs = {
            'one' : 'this is a {{{two}}} string',
            'two' : 'long',
            }
        r = RegexExpander(regs=regs)
        self.assertEqual(r.regs['one'],'this is a {long} string')


class CSVParserTestCase(TestCase):

    def setUp(self):
        self.parser = CSVParser(fieldnames=['f1','f2','f3','f4'],
            record_type='postgres')

    def test_no_record_type(self):
        pass

    def test_execute_string(self):
        data = 'this,is,a,test'
        output = self.parser.execute(data)
        self.assertEqual(output['type'],'postgres')
        self.assertEqual(output['f1'],'this')
        self.assertEqual(output['f2'],'is')
        self.assertEqual(output['f3'],'a')
        self.assertEqual(output['f4'],'test')
  
    def test_execute_dict(self):
        data = { 'msg' : 'this,is,a,test' }
        output = self.parser.execute(data)
        self.assertEqual(output['f1'],'this')
        self.assertEqual(output['f2'],'is')
        self.assertEqual(output['f3'],'a')
        self.assertEqual(output['f4'],'test')

    def test_execute_dict_with_parse_field(self):
        self.parser = CSVParser(fieldnames=['f1','f2','f3','f4'],
            record_type='postgres',parse_field='myfield')
        data = { 'myfield' : 'this,is,a,test' }
        output = self.parser.execute(data)
        self.assertEqual(output['f1'],'this')
        self.assertEqual(output['f2'],'is')
        self.assertEqual(output['f3'],'a')

    def test_parser_kwargs(self):
        self.parser = CSVParser(fieldnames=['f1','f2','f3','f4'],
            record_type='postgres',delimiter='-')
        data = 'this-is-a-test'
        output = self.parser.execute(data)
        self.assertEqual(output['f1'],'this')
        self.assertEqual(output['f2'],'is')
        self.assertEqual(output['f3'],'a')

class RegexParserTestCase(TestCase):

    def setUp(self):
        self.regs = {
            "yyyy-mm-dd" : "(?P<date>\d{4}-\d{2}-\d{2})",
            "user" : "(?P<user>\w+)",
            "team" : "(?P<team>\w+)",
            "word" : "(?P<word>\w+)",
            "msg" : "(?P<msg>.*)",
            "irclog" : "{{team}}\|{{yyyy-mm-dd}} \< {{user}}\> {{msg}}"
            }
        self.parser = RegexParser(regs=self.regs,use=['irclog','team','word'])
        self.pattern_type = type(re.compile('\d{2}'))

    def test_compile(self):
        for key in self.parser.use:
            self.assertIsInstance(self.parser.compiled[key], self.pattern_type)

    def test_bad_use_key(self):
        self.assertRaises(Exception, RegexParser, regs=self.regs,use=['notakey'])

    def test_use_not_empty(self):
        self.assertRaises(Exception, RegexParser, self.regs, use=[])

    def test_search(self):
        m1 = self.parser.execute('team1|2012-02-27 < jbruce> testing123')
        self.assertEqual(m1['type'],'irclog')
        self.assertEqual(m1['team'],'team1')
        self.assertEqual(m1['user'],'jbruce')
        self.assertEqual(m1['date'],'2012-02-27')
        self.assertEqual(m1['msg'],'testing123')

    def test_search_cascade(self):
        '''
        note this also tests that the first match wins.
        both team and word will match, but team matches first.
        '''
        m1 = self.parser.execute('this is a test')
        self.assertEqual(m1['type'],'team')
        self.assertEqual(m1['team'],'this')

    def test_search_no_match(self):
        m1 = self.parser.execute('.%$#@.*')
        self.assertIsNone(m1)
        m1 = self.parser.execute('')
        self.assertIsNone(m1)

    def test_execute_dict(self):
        m1 = self.parser.execute({'msg' : 'team1|2012-02-27 < jbruce> testing123', 'other' : 'should be retained'})
        self.assertEqual(m1['type'],'irclog')
        self.assertEqual(m1['team'],'team1')
        self.assertEqual(m1['user'],'jbruce')
        self.assertEqual(m1['date'],'2012-02-27')
        self.assertEqual(m1['msg'],'testing123') 
        self.assertEqual(m1['other'],'should be retained')

    def test_execute_dict_with_parse_field(self):
        self.parser = RegexParser(regs=self.regs,use=['irclog','team','word'],parse_field='parse_this')
        m1 = self.parser.execute({'parse_this' : 'team1|2012-02-27 < jbruce> testing123', 'other' : 'should be retained'})
        self.assertEqual(m1['type'],'irclog')
        self.assertEqual(m1['team'],'team1')
        self.assertEqual(m1['user'],'jbruce')
        self.assertEqual(m1['date'],'2012-02-27')
        self.assertEqual(m1['msg'],'testing123')
        self.assertEqual(m1['other'],'should be retained')
       
    def test_execute_dict_with_parse_field_not_in_data(self):
        self.parser = RegexParser(regs=self.regs,use=['irclog','team','word'],parse_field='parse_this')
        m1 = self.parser.execute({'blah' : 'team1|2012-02-27 < jbruce> testing123', 'other' : 'should be retained'})
        self.assertIsNone(m1)

if __name__ == '__main__':
    unittest.main()

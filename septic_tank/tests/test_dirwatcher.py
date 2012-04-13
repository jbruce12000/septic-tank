#!/usr/bin/env python
import unittest
import re
#import mock
from unittest import TestCase
from dirwatcher import DirWatcher, FileWatcher


class FileWatcherTestCase(TestCase):
    def setUp(self):
        self.fw =FileWatcher(folder='',name='',testing=True)

    def test_execute(self):
        pass

    def test_combine_lines(self):
        lines = []
        lines.append('normal log line')
        lines.append('  starts with whitespace')
        lines.append('  starts with whitespace2')
        lines.append('normal log line2')
        out = self.fw.combine_lines(lines=lines,regex=re.compile('^\s+'))
        self.assertEqual(len(out),2)

    def test_combine_lines_drop_matches_at_start(self):
        lines = []
        lines.append('  starts with whitespace')
        lines.append('normal log line')
        lines.append('  starts with whitespace2')
        lines.append('normal log line2')
        out = self.fw.combine_lines(lines=lines,regex=re.compile('^\s+'))
        self.assertEqual(len(out),2)


class DirWatcherTestCase(TestCase):
    def setUp(self):
        pass

    def test_execute(self):
        pass

if __name__ == '__main__':
    unittest.main()

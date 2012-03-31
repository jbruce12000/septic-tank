#!/usr/bin/env python
import unittest
from unittest import TestCase
from outputs import ZeroMQOutput

class ZeroMQOutputTestCase(TestCase):
    def setUp(self):
        self.zmq = ZeroMQOutput()
        self.data = { 'key1' : 'val1', 'key2' : 'val2', 'key3' : 'val3' }

    def test_execute(self):
        # need help from Alfredo to mock this
        pass

if __name__ == '__main__':
    unittest.main()

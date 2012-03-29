#!/usr/bin/env python

import unittest
from unittest import TestCase
from pipeline import Pipe, Pipeline

class PipeTestCase(TestCase):
    def setUp(self):
        self.p1 = Pipe()

    def test_empty(self):
        self.assertEqual(self.p1.is_empty(), True)
        self.p1.cache = [ None ]
        self.assertEqual(self.p1.is_empty(), True)
        # not sure what I want this to do...
        # self.p1.cache = [ None, 'blah' ]
        # self.assertEqual(self.p1.is_empty(), True)

    def test_output(self):
        self.p1.cache = [1,2,3]
        self.assertEqual(self.p1.output(),1)
        self.assertEqual(self.p1.output(),2)
        self.assertEqual(self.p1.output(),3)
        self.assertEqual(self.p1.output(),None)

    def test_execute(self):
        self.assertEqual(self.p1.execute(1),1)

class PipelineTestCase(TestCase):

    def test_minimum_pipes(self):
        p1 = Pipe()
        pline = Pipeline(pipes=[p1])
        self.assertRaises(StopIteration, pline.next)

    def test_iteration(self):
        p1 = Pipe(name='p1')
        p1.cache = ['ok']
        p2 = Pipe(name='p2')
        p3 = Pipe(name='p3')
        pline = Pipeline(pipes=[p1,p2,p3])
        self.assertEqual(pline.next(),'ok')

if __name__ == '__main__':
    unittest.main()


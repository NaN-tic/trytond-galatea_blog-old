#!/usr/bin/env python
# This file is part galatea_blog module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import test_view, test_depends


class GalateaBlogTestCase(unittest.TestCase):
    'Test Galatea Blog module'

    def setUp(self):
        trytond.tests.test_tryton.install_module('galatea_blog')

    def test0005views(self):
        'Test views'
        test_view('galatea_blog')

    def test0006depends(self):
        'Test depends'
        test_depends()


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        GalateaBlogTestCase))
    return suite

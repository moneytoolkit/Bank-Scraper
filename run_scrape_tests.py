#!/usr/bin/env python

import unittest
import sys
import logging

from tests.script.test_scrape import TestScrape

def addSuite(suite, newclass):
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(newclass))


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
    
if __name__ == '__main__':

    mtkSuite = unittest.TestSuite()
    
    addSuite(mtkSuite, TestScrape)

    unittest.TextTestRunner(verbosity=3).run(mtkSuite)
    
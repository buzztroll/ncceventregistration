import unittest

from gchecky.test.gxml import *
from gchecky.test.controller import *

def allTestSuite():
    suite = unittest.TestSuite()
    suite.addTest(xmlFieldSuite())
    suite.addTest(xmlNodeSuite())
    suite.addTest(controllerSuite())
    return suite
 
if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(allTestSuite)

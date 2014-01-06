import unittest

from test.testSimulator import TestSimulator
from test.testMyAlgebra import TestMyAlgebra
from test.testAlgorithms import TestAlgorithms
from test.testFindFPDIT import TestFindFPDIT
from test.testTask import TestTask

if __name__ == '__main__':
    tests = [TestSimulator, TestMyAlgebra, TestAlgorithms, TestFindFPDIT, TestTask]
    for test in tests:
        suite = unittest.TestLoader().loadTestsFromTestCase(test)
        unittest.TextTestRunner(verbosity=1).run(suite)

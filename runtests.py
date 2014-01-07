import unittest

from test.testSimulator import TestSimulator, TestSimulatorWithKnownSystems
from test.testMyAlgebra import TestMyAlgebra
from test.testAlgorithms import TestAlgorithms
from test.testFindFPDIT import TestFindFPDIT
from test.testTask import TestTask

if __name__ == '__main__':
    tests = [
        TestMyAlgebra,
        TestTask,
        TestAlgorithms,
        TestFindFPDIT,
        TestSimulator,
        TestSimulatorWithKnownSystems
    ]
    for test in tests:
        suite = unittest.TestLoader().loadTestsFromTestCase(test)
        unittest.TextTestRunner(verbosity=2).run(suite)

import unittest

from test.testSimulator import TestSimulator
from test.TestScheduler import TestScheduler
from test.testMyAlgebra import TestMyAlgebra
from test.testAlgorithms import TestAlgorithms
from test.testTask import TestTask
from test.testCspace import TestCspace

if __name__ == '__main__':
    tests = [
        TestMyAlgebra,
        TestTask,
        TestAlgorithms,
        TestCspace,
        TestSimulator,
        TestScheduler
    ]
    for test in tests:
        suite = unittest.TestLoader().loadTestsFromTestCase(test)
        unittest.TextTestRunner(verbosity=2).run(suite)

import unittest

from helper import myAlgebra as mAlg


class TestMyAlgebra(unittest.TestCase):
    def setUp(self):
        pass

    def test_nextPeriodicArrival(self):
        self.assertEquals(mAlg.nextPeriodic(3, 10, 0), 10)
        self.assertEquals(mAlg.nextPeriodic(3, 3, 0), 6)
        self.assertEquals(mAlg.nextPeriodic(40, 12, 27), 51)
        self.assertEquals(mAlg.nextPeriodic(5, 5, 5), 10)

    def test_LCM(self):
        self.assertEquals(mAlg.lcm(2, 3), 6)
        self.assertEquals(mAlg.lcm(11, 121), 121)
        self.assertEquals(mAlg.lcm(12, 36, 30), 180)
        self.assertEquals(mAlg.lcmArray([12, 42]), 84)
        self.assertEquals(mAlg.lcmArray([2, 3, 15]), 30)
        self.assertEquals(mAlg.lcmArray([1, 12, 35]), 420)
        self.assertEquals(mAlg.lcmArray([6, 14]), 42)

    def test_EGCD(self):
        self.assertEquals(mAlg.egcd(9, 21), 3)
        self.assertEquals(mAlg.egcd(5, 125), 5)
        self.assertEquals(mAlg.egcd(36, 27, 45, 81), 9)

    def test_modinv(self):
        self.assertEquals(mAlg.modinv(3, 11), 4)
        self.assertEquals(mAlg.modinv(3, 5), 2)
        self.assertEquals(mAlg.modinv(17, 60), 53)

    def chineseRemainderTheorem(self):
        self.assertEquals(mAlg.chineseRemainderTheorem([2, 3, 1], [3, 4, 5]), 11)
        self.assertEquals(mAlg.chineseRemainderTheorem([3, 1, 4], [8, 9, 11]), 235)

    def testPrimeFactors(self):
        self.assertIn(2, mAlg.primeFactors(48))
        self.assertEquals(mAlg.primeFactors(48).count(2), 4)
        self.assertIn(3, mAlg.primeFactors(48))
        self.assertEquals(mAlg.primeFactors(48).count(3), 1)

    def testCongruence(self):
        self.assertEquals(mAlg.congruence([1, 0, 3, 2], [2, 3, 6, 7]), 9)
        self.assertEquals(mAlg.congruence([0, 0, 2, 8], [2, 8, 6, 9]), 8)

from simulator import Simulator
from simulator.scheduler import Scheduler, OldAndForgotten
from helper import systems
from model import algorithms

import unittest


class TestSimulator(unittest.TestCase):
    def setUp(self):
        pass

    def testStopAtDeadlineMiss(self):
        tau = systems.MustIdle
        sched = Scheduler.EDF(tau)
        simulator = Simulator.getLaunchedSimu(tau, sched)
        self.assertFalse(simulator.success())
        self.assertEqual(simulator.t, 5)

    def testStopAtStableConfig(self):
        tau = systems.LongTransitive2
        sched = Scheduler.EDF(tau)
        simulator = Simulator.getLaunchedSimu(tau, sched)
        self.assertTrue(simulator.success())
        self.assertTrue(simulator.isStable)
        self.assertEqual(simulator.t, 46)

    def testEnoughTest(self):
        assert False, "This need more test!"

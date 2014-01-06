import unittest
import random

from model import algorithms as algo
from model.Task import Task, TaskSystem


class TestAlgorithms(unittest.TestCase):
    def setUp(self):
        pass

    def test_Trivial(self):
        tasks = []
        tasks.append(Task(0, 1, 3, 6))
        tasks.append(Task(0, 1, 3, 3))
        tau = TaskSystem(tasks)
        self.assertEquals(algo.completedJobCount(tau.tasks[0], 15, 25), 1)
        self.assertEquals(algo.completedJobCount(tau.tasks[0], 0, 33), 6)
        self.assertEquals(algo.completedJobCount(tau.tasks[1], 0, 33), 11)
        self.assertEquals(algo.findBusyPeriod(tau), 2)
        self.assertEquals(algo.findFirstDIT(tau), 3)
        self.assertEquals(algo.findSynchronousInstant(tau), 0)
        self.assertTrue(algo.dbfTest(tau))

    def test_influenceDeadlineOnDIT(self):
        tasks = []
        tasks.append(Task(0, 1, 1, 6))
        tasks.append(Task(0, 1, 1, 3))
        tau = TaskSystem(tasks)
        self.assertEquals(algo.findBusyPeriod(tau),  2)
        self.assertEquals(algo.findFirstDIT(tau), 1)
        self.assertEquals(algo.findSynchronousInstant(tau), 0)
        self.assertFalse(algo.dbfTest(tau))

    def test_congruenceEdgeCase(self):
        tasks = []
        tasks.append(Task(0, 1, 2, 2))
        tasks.append(Task(0, 1, 3, 3))
        tau = TaskSystem(tasks)
        self.assertEquals(algo.findBusyPeriod(tau), 2)
        self.assertEquals(algo.findFirstDIT(tau), 6)
        self.assertEquals(algo.findSynchronousInstant(tau), 0)
        self.assertTrue(algo.dbfTest(tau))

    def test_asynchronous1(self):
        tasks = []
        tasks.append(Task(5, 1, 1, 3))
        tasks.append(Task(0, 4, 4, 8))
        tau = TaskSystem(tasks)
        # No busy period test as it does not make sense in asynchronous system
        self.assertEquals(algo.findFirstPeriodicDIT(tau), 6)
        self.assertEquals(algo.findSynchronousInstant(tau), 8)
        self.assertTrue(algo.dbfTest(tau))

    def test_asynchronous2(self):
        tasks = []
        tasks.append(Task(0, 1, 4, 6))
        tasks.append(Task(2, 1, 3, 6))
        tasks.append(Task(10, 1, 1, 2))
        tau = TaskSystem(tasks)
        self.assertEquals(algo.findFirstPeriodicDIT(tau), 11)
        self.assertIsNone(algo.findSynchronousInstant(tau))

    def test_asynchronous3(self):
        tasks = []
        tasks.append(Task(120, 6, 25, 25))
        tasks.append(Task(0, 4, 47, 48))
        tau = TaskSystem(tasks)
        self.assertEquals(algo.findFirstPeriodicDIT(tau), 720)
        self.assertEquals(algo.findSynchronousInstant(tau), 720)

    def test_longerSystem(self):
        tasks = []
        tasks.append(Task(0, 38, 73, 154))
        tasks.append(Task(0, 156, 381, 825))
        tasks.append(Task(0, 120, 381, 400))
        tau = TaskSystem(tasks)
        # I haven't checked these results so this test only check that the values do not change.
        self.assertEquals(algo.findBusyPeriod(tau),  390)
        self.assertEquals(algo.findFirstDIT(tau),  381)
        self.assertEquals(algo.findSynchronousInstant(tau), 0)
        self.assertFalse(algo.dbfTest(tau))

    def test_randomYAfindFPDIT(self):
        from model import TaskGenerator
        for i in range(1000):
            Utot = random.randint(25, 100) / 100
            n = random.randint(2, 5)
            maxHyperT = 5046
            Tmin = 5
            Tmax = 20
            tasks = TaskGenerator.generateTasks(Utot, n, maxHyperT, Tmin, Tmax, synchronous=False)
            tau = TaskSystem(tasks)
            self.assertEquals(algo.YAfindFPDIT(tau), algo.findFirstDIT(tau))

    # def test_randomSystem(self):
    #     from Model import TaskGenerator
    #     Utot = 1
    #     n = 4
    #     maxHyperT = 100
    #     Tmin = 5
    #     Tmax = 20
    #     tasks = TaskGenerator.generateTasks(Utot, n, maxHyperT, Tmin, Tmax, synchronous=False)
    #     return  # oracle ?

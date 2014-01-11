from model.Task import Task, TaskSystem

import unittest


class TestTask(unittest.TestCase):
    def setUp(self):
        tasks = []
        tasks.append(Task(0, 1, 3, 6))
        tasks.append(Task(0, 1, 3, 3))
        tasks.append(Task(1, 1, 5, 4))

        tasks2 = []
        tasks2.append(Task(0, 38, 73, 154))
        tasks2.append(Task(0, 156, 362, 825))
        tasks2.append(Task(0, 120, 362, 400))

        self.tau = TaskSystem(tasks)
        self.tau2 = TaskSystem(tasks[0:2])
        self.tau3 = TaskSystem(tasks2)

    def test_isSynchronous(self):
        self.assertFalse(self.tau.isSynchronous())
        self.assertTrue(self.tau2.isSynchronous())
        self.assertTrue(self.tau3.isSynchronous())

    def test_hasConstrainedDeadline(self):
        self.assertFalse(self.tau.hasConstrainedDeadline())
        self.assertTrue(self.tau2.hasConstrainedDeadline())
        self.assertTrue(self.tau3.hasConstrainedDeadline())

    def test_systemUtilization(self):
        self.assertEqual(self.tau2.systemUtilization(), 0.5)

    def test_hyperperiod(self):
        self.assertEqual(self.tau2.hyperPeriod(), 6)

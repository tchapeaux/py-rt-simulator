import unittest
import random

from model import cspace as cs
from model.Task import Task, TaskSystem
from model.TaskGenerator import generateTasks


class TestCspace(unittest.TestCase):
    def setUp(self):
        pass

    def test_simple(self):
        tasks = []
        tasks.append(Task(8, 1, 7, 15))
        tasks.append(Task(0, 1, 2, 5))
        tau = TaskSystem(tasks)
        cspace_tau = cs.Cspace(tau)
        self.assertEqual(len(cspace_tau), 11)
        self.assertEqual(cspace_tau.size(), 11)
        cspace_tau = cspace_tau.removeRedundancy()
        self.assertEqual(len(cspace_tau), 2)
        self.assertEqual(cspace_tau.size(), 11)

    def test_random(self):
        # this is a super simple example but a more complex would take too much time
        tasks = generateTasks(
            Utot=random.random(),
            n=2,
            maxHyperT=180, Tmin=20, Tmax=90,
            synchronous=False,
            constrDeadlineFactor=1
        )
        tau = TaskSystem(tasks)
        cspace_tau = cs.Cspace(tau)
        volume_redun = cspace_tau.size()
        nbr_cstr_redun = len(cspace_tau)
        print(nbr_cstr_redun)
        cspace_tau.removeRedundancy()
        self.assertEqual(volume_redun, cspace_tau.size())
        self.assertEqual(nbr_cstr_redun, len(cspace_tau))

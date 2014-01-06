import unittest
import random

from model.Task import Task, TaskSystem
from model import algorithms, TaskGenerator
from helper import findFPDIT

class TestFindFPDIT(unittest.TestCase):
    def setUp(self):
        pass

    def test_findFPDIT(self):
#         while(True):
#             tasks = TaskGenerator.generateTasks(random.random(), 3, 554400, 3, 25, synchronous=False)
#     #         tasks = []
#     #         tasks.append(Task(0, 1, 3, 5))
#     #         tasks.append(Task(2, 1, 22, 25))
#             tau = TaskSystem(tasks)
#             if not findFPDIT.findFPDIT(tau) == algorithms.findFirstDIT(tau):
#                 print(tau)

        tasks = []
        tasks.append(Task(0, 1, 17, 18, 0))
        tasks.append(Task(6, 1, 3, 10, 0))
        tasks.append(Task(6, 1, 8, 8, 0))
        tau = TaskSystem(tasks)
#         self.assertEquals(findFPDIT.findFPDIT(tau), algorithms.findFirstDIT(tau))


from helper import systems
from model import Task
from model import cspace as cs
from model import algorithms

import sys

tau = None

tasks = []
tasks.append(Task.Task(8, 1, 7, 15))
tasks.append(Task.Task(0, 1, 2, 5))
tau = Task.TaskSystem(tasks)

# tau = systems.generateSystemArray(1, 1, synchronous=True)[0]

if len(sys.argv) > 1:
    with open(sys.argv[1]) as f:
        tau = Task.TaskSystem.fromFile(f)

print(tau)
print("cspace...")
cspace = cs.Cspace(tau)
print("found ", len(cspace), "constraints")
for cstr in cspace:
    print(cstr)
print("")
print("remove redun...")
cspace_noredun = cspace.removeRedundancy(verbose=True)
print(len(cspace), "=>", len(cspace_noredun), "constraints left")
for cstr in cspace_noredun:
    print(cstr)
print("")
resultCSPACE = cs.testCVector(cspace_noredun, [task.C for task in tau.tasks])
resultCSPACENOREDUN = cs.testCVector(cspace, [task.C for task in tau.tasks])
resultDBF = algorithms.dbfTest(tau)
sizeCSPACE = cspace.size()
sizeCSPACENOREDUN = cspace_noredun.size()
assert resultCSPACE == resultCSPACENOREDUN == resultDBF, str(resultCSPACE) + str(resultCSPACENOREDUN) + str(resultDBF)
assert sizeCSPACE == sizeCSPACENOREDUN

print("synchronous instant", algorithms.findSynchronousInstant(tau))
print("The volume of the C-space is", cspace_noredun.size(tau))

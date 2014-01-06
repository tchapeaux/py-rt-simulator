import random
import time
# import pylab

from model import algorithms
from model import Task
from model import TaskGenerator
from model import cspace


def generateSystemArray(numberOfSystems, constrDeadlineFactor, verbose=False):
    systemArray = []
    for i in range(numberOfSystems):
        Umin = 0.25
        Umax = 0.75
        Utot = 1.0*random.randint(int(Umin*100), int(Umax*100))/100
        n = 3
        # maxHyperT = 554400  # PPCM(2, 3, 5, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 22, 24, 25, 28, 30, 32)
        maxHyperT = -1
        Tmin = 5
        Tmax = 20
        tasks = TaskGenerator.generateTasks(Utot, n, maxHyperT, Tmin, Tmax, synchronous=False, constrDeadlineFactor=constrDeadlineFactor)
        if (verbose and numberOfSystems <= 10):
            print(("Generated task system # ", i))
            for task in tasks:
                    print(("\t", task))
        systemArray.append(Task.TaskSystem(tasks))
    return systemArray

if __name__ == '__main__':
    NUMBER_OF_SYSTEMS = 10
    for constrDeadlineFactor in [1, 1/2, 1/3, 1/4, 1/5, 1/6, 1/7, 1/8, 1/9, 1/10]:
        print(("CONSTR DEAD FACTOR", constrDeadlineFactor))
        systemArray = generateSystemArray(NUMBER_OF_SYSTEMS, constrDeadlineFactor)
        firstDITs = []
        upLs = []
        for i, tau in enumerate(systemArray):
            start = time.clock()

            firstDITs.append(algorithms.findFirstPeriodicDIT(tau))
            if firstDITs[-1] is not None:
                firstDITs[-1] += tau.hyperPeriod()
            upLs.append(max([task.O for task in tau.tasks]) + 2 * tau.hyperPeriod())
            print(("\t", i, "Limit :", firstDITs[-1] if firstDITs[-1] is None else firstDITs[-1], "/", upLs[-1]))

            sizeWithDIT = len(cspace.Cspace(tau, upperLimit="def"))  # will use first DIT if it exists
            if firstDITs[-1] is None:
                sizeWithoutDIT = sizeWithDIT
            else:
                sizeWithoutDIT = len(cspace.Cspace(tau, upperLimit=upLs[-1]))
            stop = time.clock()
            print(("\tsize with DIT\t", sizeWithDIT))
            print(("\tsize no DIT\t", sizeWithoutDIT))
            print(("\ttime: ", stop - start, "s"))
            print("\t")

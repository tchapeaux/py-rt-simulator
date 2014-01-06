from model import Task
from model import TaskGenerator
from model import algorithms
from model import cspace

import random
import time


def testSystem(tau):
    print("TESTING SYSTEM")
    print(tau)

    Omax = max([task.O for task in tau.tasks])
    fpdit = algorithms.findFirstDIT(tau)
    H = tau.hyperPeriod()
    tau_cspace = cspace.Cspace(tau)
    tau_big_cspace = cspace.Cspace(tau, Omax + 2 * H)

    print(("firstDIT", fpdit))
    print(("H", H))
    print("intervals")
    for (a, d) in tau.dbf_intervals(fpdit, fpdit + H):
        print([a, d])
    print(("#cstr of cspace", len(tau_cspace)))
    print(("#cstr of big cspace", len(tau_big_cspace)))

    smallStart = time.clock()
    cspacePruned = tau_cspace.removeRedundancy()
    smallStop = time.clock()

    bigStart = time.clock()
    big_cspacepruned = tau_big_cspace.removeRedundancy()
    bigStop = time.clock()

    print(("#cstr of cspace after pruning ", len(cspacePruned), "(time", smallStop - smallStart, ")"))
    print(("#cstr of big cspace after pruning ", len(big_cspacepruned), "time", bigStop - bigStart))
    # print "size :", cspace.CspaceSize(tau, cspacePruned)
    print(("comparison of sizes", tau.cSpaceSize(tau_cspace), "|", tau.cSpaceSize(cspacePruned)))
    return tau.cSpaceSize(cspacePruned)


def generateSystemArray(numberOfSystems, constrDeadlineFactor, verbose=False):
    systemArray = []
    for i in range(numberOfSystems):
        Umin = 0.25
        Umax = 0.75
        Utot = 1.0*random.randint(int(Umin*100), int(Umax*100))/100
        n = 2
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
    tasks = []
    tasks.append(Task.Task(8, 2, 7, 15))
    tasks.append(Task.Task(0, 1, 2, 5))

    systemArray = [Task.TaskSystem(tasks)]
    #systemArray = generateSystemArray(100, 1)

    for i, tau in enumerate(systemArray):
        print(("TEST NUMBER", i))
        sizeAsynchr = testSystem(tau)
        synchrTasks = []
        for task in tau.tasks:
            synchrTasks.append(Task.Task(0, task.C, task.D, task.T))
        synchrTau = Task.TaskSystem(synchrTasks)
        sizeSynchr = testSystem(synchrTau)
        assert sizeSynchr <= sizeAsynchr

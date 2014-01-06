import time
import random

import pylab  # http://matplotlib.org/

from model import Task, TaskGenerator
from model import algorithms
from functools import reduce


def generateSystemArray(numberOfSystems, constrDeadlineFactor, verbose=False):
    systemArray = []
    for i in range(numberOfSystems):
        Umin = 0.25
        Umax = 0.75
        Utot = 1.0*random.randint(int(Umin*100), int(Umax*100))/100
        n = random.randint(1, 4)
        maxHyperT = 554400  # PPCM(2, 3, 5, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 22, 24, 25, 28, 30, 32)
        # maxHyperT = -1
        Tmin = 2
        Tmax = 25
        tasks = TaskGenerator.generateTasks(Utot, n, maxHyperT, Tmin, Tmax, synchronous=False, constrDeadlineFactor=constrDeadlineFactor)
        if (verbose and numberOfSystems <= 10):
            print("Generated task system # ", i)
            for task in tasks:
                    print(("\t", task))
        systemArray.append(Task.TaskSystem(tasks))
    return systemArray


def test(numberOfSystems, constrDeadlineFactor):
    systemArray = generateSystemArray(numberOfSystems, constrDeadlineFactor, verbose=False)
    verbose = False

    # Upper Limit Arrays
    busyPeriods = []
    firstDITs = []
    hyperTs = []
    # Feasibility Arrays
    bpResults = []
    ditResults = []
    hyperTResults = []

    # Compare algorithms

    print("start busy period tests...")
    bpStart = time.clock()
    if len([x for x in systemArray if not x.isSynchronous()]) == 0:
        for tau in systemArray:
            busyPeriods.append(algorithms.findBusyPeriod(tau))
        bpMedium = time.clock()
        for i, tau in enumerate(systemArray):
            bpResults.append(algorithms.dbf_test(tau, busyPeriods[i]))
    else:
        bpMedium = time.clock()
    bpStop = time.clock()

    print("Starting hyperT value...")
    hyperTStart = time.clock()
    for i, tau in enumerate(systemArray):
        hyperTs.append(tau.hyperPeriod())
    hyperTMedium = time.clock()
    print("Starting hyperT test...")
    for i, tau in enumerate(systemArray):
        hyperTResults.append(algorithms.dbfTest(tau))
    hyperTStop = time.clock()

    print("starting DIT value computation...")
    ditStart = time.clock()
    for i, tau in enumerate(systemArray):
        #print i
        firstDITs.append(algorithms.findFirstDIT(tau))
    ditMedium = time.clock()
    print("starting DIT dbf test...")
    for i, tau in enumerate(systemArray):
        ditResults.append(algorithms.dbfTest(tau, firstDITs[i]))
    ditStop = time.clock()
    print("done")

    for i in range(len(systemArray)):
        assert ditResults[i] == hyperTResults[i]

    print("== Test Results (on " + str(numberOfSystems) + " tasks system)")
    if (verbose and len(systemArray) <= 10):
        for i in range(len(systemArray)):
            print("=== System", i)
            print("\tbusy period:", busyPeriods[i])
            print("\tfirst DIT:", firstDITs[i])
            print("\tPPCM:", hyperTs[i])
    print("\tAlgorithms performance (upper limit computation + dbf test)")
    print("\t\tTime with busy period:", bpMedium - bpStart, "+", bpStop - bpMedium, " = ", bpStop - bpStart, "s")
    print("\t\tTime with DIT:", ditMedium - ditStart, "+", ditStop - ditMedium, " = ", ditStop - ditStart, "s")
    print("\t\tTime with hyperT:", hyperTMedium - hyperTStart, "+", hyperTStop - hyperTMedium, " = ", hyperTStop - hyperTStart, "s")
    feasibleSystemCnt = reduce(lambda x, y: x + (y is True), hyperTResults)
    print("\tFeasible?", feasibleSystemCnt, ", or about", int(round((feasibleSystemCnt * 100.0)/len(systemArray))), "%")

    return bpStop - bpMedium, bpMedium - bpStart, ditStop - ditMedium, ditMedium - ditStart, hyperTStop - hyperTMedium, hyperTMedium - hyperTStart

if __name__ == '__main__':
    NUMBER_OF_SYSTEMS = 100
    bpValue = []
    bpTest = []
    bpAll = []
    ditValue = []
    ditTest = []
    ditAll = []
    hyperTValue = []
    hyperTTest = []
    hyperTAll = []
    cdfRange = [2/f for f in range(2, 11)]
    for constrDeadFactor in cdfRange:
        print("TEST WITH CONSTR DEAD FACTOR", constrDeadFactor)
        result = test(NUMBER_OF_SYSTEMS, constrDeadFactor)
        bpValue.append(result[1])
        bpTest.append(result[0])
        bpAll.append(result[0] + result[1])
        ditValue.append(result[3])
        ditTest.append(result[2])
        ditAll.append(result[2] + result[3])
        hyperTValue.append(result[5])
        hyperTTest.append(result[4])
        hyperTAll.append(result[4] + result[5])

    pylab.figure()
    pylab.plot(cdfRange, bpAll, "k-", label="BP ALL")
    pylab.plot(cdfRange, bpValue, "k--", label="BP VALUE")
    pylab.plot(cdfRange, ditAll, "b-", label="DIT ALL")
    pylab.plot(cdfRange, ditValue, "b--", label="DIT VALUE")
    pylab.plot(cdfRange, hyperTAll, "r-", label="HYPERT ALL")
    pylab.plot(cdfRange, hyperTValue, "r--", label="HYPERT VALUE")
    pylab.ylabel("time (s)")
    pylab.xlabel("e")
    pylab.title("Computation time for some values of e (" + str(NUMBER_OF_SYSTEMS) + " systems)")
    pylab.legend(loc=0)
#   pylab.axis([cdfRange[0], cdfRange[-1], -0.5, 6])
    pylab.savefig("./plots/001_" + str(time.time()).replace(".", "") + ".png")
    pylab.show()

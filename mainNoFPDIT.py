import random
import math
import concurrent.futures
import pickle

from model import algorithms
from model import Task
from model import TaskGenerator

from helper import myAlgebra


def generateSystemArray2(numberOfSystems, constrDeadlineFactor, tasksCnt):
    systemArray = []
    i = 0
    while i < numberOfSystems:
        tasks = []
        Tarray = []
        for j in range(tasksCnt):
            Tarray.append(random.randint(5, 20))
        H = myAlgebra.lcmArray(Tarray)
        for j in range(tasksCnt):
            T = Tarray[j]
            O = random.randint(0, H)
            D = max(1, random.randint(math.floor(T - constrDeadlineFactor * T), T))
            tasks.append(Task.Task(O, 1, D, T))
        tau = Task.TaskSystem(tasks)
        if tau.systemUtilization() <= 1:
            systemArray.append(Task.TaskSystem(tasks))
            i += 1
    return systemArray


def generateSystemArray(numberOfSystems, constrDeadlineFactor, tasksCnt, verbose=False):
    systemArray = []
    for i in range(numberOfSystems):
        Umin = 0.25
        Umax = 0.75
        Utot = 1.0*random.randint(int(Umin*100), int(Umax*100))/100
        n = tasksCnt
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
    noFPDITpcts = {}
    CDFvalues = [0.1, 0.3, 0.5, 0.7, 0.9, 1.0]
    nValues = [2, 3, 4, 5]
    for taskCnt in nValues:
        print("n", taskCnt)
        noFPDITpcts[taskCnt] = {}
        for constrDeadlineFactor in CDFvalues:
            print("cdf", constrDeadlineFactor)
            systemArray = generateSystemArray2(NUMBER_OF_SYSTEMS, constrDeadlineFactor, taskCnt)
            firstDitsCnt = 0
            executor = concurrent.futures.ProcessPoolExecutor()
            futures = [executor.submit(algorithms.findFirstDIT, tau) for tau in systemArray]
            for f in futures:
                if f.result() is None:
                    firstDitsCnt += 1
            noFPDITpcts[taskCnt][constrDeadlineFactor] = (100*firstDitsCnt)/NUMBER_OF_SYSTEMS

    with open("noFPDIT_results.pickle", "wb") as output:
        print("Writing result to memory...")
        pickle.dump((noFPDITpcts, CDFvalues, nValues, NUMBER_OF_SYSTEMS), output, pickle.HIGHEST_PROTOCOL)
        print("Done.")

import random
import math
import concurrent.futures
import pickle

from model import algorithms
from model import Task
from model import TaskGenerator

from simulator import Simulator
from simulator.scheduler import Scheduler

from helper import systems

# FIND A WAY TO CALCULATE THE LENGTH OF THE PERIODIC PERIOD

def generateSystemArray(numberOfSystems, constrDeadlineFactor, tasksCnt, verbose=False):
    systemArray = []
    for i in range(numberOfSystems):
        Umin = 0.25
        Umax = 1
        Utot = 1.0*random.randint(int(Umin*100), int(Umax*100))/100
        n = tasksCnt
        maxHyperT = 360  # PPCM(2, 3, 5, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 22, 24, 25, 28, 30, 32)
        # maxHyperT = -1
        Tmin = 5
        Tmax = 20
        tasks = TaskGenerator.generateTasks(Utot, n, maxHyperT, Tmin, Tmax, preemptionCost=2, synchronous=False, constrDeadlineFactor=constrDeadlineFactor)
        if (verbose and numberOfSystems <= 10):
            print(("Generated task system # ", i))
            for task in tasks:
                    print(("\t", task))
        systemArray.append(Task.TaskSystem(tasks))
    return systemArray


def oneTest(i, tau):
    if i % 100 == 0:
        print(i, "/", NUMBER_OF_SYSTEMS)
    sched = Scheduler.EDF(tau)
    omax = tau.omax()
    H = tau.hyperPeriod()
    stop = omax + 30 * H

    simu = Simulator.Simulator(tau, stop=stop, nbrCPUs=1, scheduler=sched, abortAndRestart=False, verbose=False, drawing=False)
    simu.run()

    if simu.success() and simu.t > omax + 2 * H and simu.t < stop:
        print(tau)
        print("stopped at:", simu.t, "period length", simu.permanentPeriodLength(), "H")


if __name__ == '__main__':
    NUMBER_OF_SYSTEMS = 1000
    tauArray = generateSystemArray(NUMBER_OF_SYSTEMS, 0, 3)
    tauArray.append(systems.LongTransitive)
    for i, tau in enumerate(tauArray):
        oneTest(i, tau)

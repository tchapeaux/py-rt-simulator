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


def generateSystemArray(numberOfSystems, constrDeadlineFactor, tasksCnt, verbose=False):
    systemArray = []
    Umin = 0.25
    Umax = 1
    n = tasksCnt
    Tmin = 5
    Tmax = 100
    maxHyperT = 554400  # PPCM(2, 3, 5, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 22, 24, 25, 28, 30, 32)
    # maxHyperT = -1
    for i in range(numberOfSystems):
        Utot = 1.0*random.randint(int(Umin*100), int(Umax*100))/100
        tasks = TaskGenerator.generateTasks(Utot, n, maxHyperT, Tmin, Tmax, preemptionCost=2, synchronous=False, constrDeadlineFactor=constrDeadlineFactor)
        if (verbose and numberOfSystems <= 10):
            print(("Generated task system # ", i))
            for task in tasks:
                    print(("\t", task))
        systemArray.append(Task.TaskSystem(tasks))
    return systemArray


def periodicBehavior(tau):
    sched = Scheduler.EDF(tau)
    omax = tau.omax()
    H = tau.hyperPeriod()
    stop = omax + 30 * H

    simu = Simulator.Simulator(
        tau,
        stop=stop,
        nbrCPUs=1,
        scheduler=sched,
        abortAndRestart=False,
        verbose=False,
        drawing=False
    )
    simu.run(stopAtDeadlineMiss=True, stopAtStableConfig=True)

    if (
        simu.success() and
        simu.t > omax + 2 * H and
        simu.t < stop and
        simu.permanentPeriodLength() > 1 and
        simu.transientPeriodLength() > 1
    ):
        return (
            tau,
            simu.t,
            simu.permanentPeriodLength(),
            simu.transientPeriodLength()
        )

if __name__ == '__main__':
    NUMBER_OF_SYSTEMS = 100
    tauArray = generateSystemArray(NUMBER_OF_SYSTEMS, 0, 3)
    # tauArray.append(systems.LongTransitive) # used to be sure the functions work
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        for result in executor.map(periodicBehavior, tauArray):
            if result:
                tau, stop, permLength, transLength = result
                print(tau)
                print("Permanent Period achieved at t = ", stop)
                print("Permanent Period Length:", permLength, "H")
                print("Transient Period Length:", transLength, "H")

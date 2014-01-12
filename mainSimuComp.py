from model import algorithms
from model import Task, TaskGenerator
from simulator import Simulator
from simulator.scheduler import Scheduler, ChooseKeepEDF, PALLF, LBLScheduler

import random
import pickle
import concurrent.futures
import sys


def oneTest(utilization):
    global schedulers
    global generate_synchronous_only
    # print(utilization)
    Utot = utilization
    maxHyperT = 554400
    # maxHyperT = -1
    Tmin = 3
    Tmax = 50
    n = random.randint(2, 5)
    preemptionCost = 2
    constrDeadlineFactor = 0  # 0 is implicit, 1 is constrained
    tasks = TaskGenerator.generateTasks(Utot, n, maxHyperT, Tmin, Tmax, preemptionCost=preemptionCost, synchronous=generate_synchronous_only, constrDeadlineFactor=constrDeadlineFactor)
    tau = Task.TaskSystem(tasks)
    # print(tau)

    Omax = max([task.O for task in tau.tasks])
    H = tau.hyperPeriod()
    fpdit = algorithms.findFirstDIT(tau)
    stop = Omax + 10 * H  # FIXME
    if fpdit:
        stop = fpdit + H
    # print("stop", stop)
    successes = {}
    for schedClass in schedulers:
        if schedClass is Scheduler.ExhaustiveFixedPriority:
            sched = schedClass(tau, 1, False)
        else:
            sched = schedClass(tau)
        simu = Simulator.Simulator(tau, stop=stop, nbrCPUs=1, scheduler=sched, abortAndRestart=False, drawing=False)
        simu.run(stopAtDeadlineMiss=True, stopAtStableConfig=True)
        successes[schedClass] = simu.success()
    return utilization, successes, tau


def recognizeSchedulerName(name):
    if name == "EDF":
        return Scheduler.EDF
    elif name == "PALLF":
        return PALLF.PALLF
    elif name == "PTEDF":
        return Scheduler.PTEDF
    return None


if __name__ == '__main__':
    domin_scores = {}
    scores = {}
    NUMBER_OF_SYSTEMS = 100
    uRange = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    schedulers = [Scheduler.PTEDF, Scheduler.EDF]
    names = ["PTEDF", "EDF"]
    generate_synchronous_only = False
    outFile = open("out.txt", "w")

    helpString = \
        "Usage: python3 mainSimuComp.py <-paramName> <paramValue>\n\
        Parameters:\n\
        -sched1 / sched2 : Name of the compared schedulers\n\
        -o : log file (default: out.txt)\n\
        -p : pickle file (default: mainSimuComp_results.pickle)\n\
        -n : number of systems per data point (default: 1000)\n\
        -synchr : generate synchronous system only (1/0) (default: 0)\
        "
    argv = sys.argv[1:]
    argc = len(argv)
    assert argc % 2 == 0, "Invalid number of arguments\n" + helpString
    for i in range(0, argc, 2):
        paramV = argv[i + 1]
        if argv[i] == "-o":
            outFile = open(paramV, "w")
        elif argv[i] == "-n":
            NUMBER_OF_SYSTEMS = int(paramV)
        elif argv[i] == "-synchr":
            generate_synchronous_only = True if int(paramV) == 1 else False
        elif argv[i] == "-sched1":
            newSched = recognizeSchedulerName(paramV)
            if newSched is None:
                raise AssertionError("Scheduler name not recognized:", paramV)
            schedulers[0] = newSched
            names[0] = paramV
        elif argv[i] == "-sched2":
            newSched = recognizeSchedulerName(paramV)
            if newSched is None:
                raise AssertionError("Scheduler name not recognized:", paramV)
            schedulers[1] = newSched
            names[1] = paramV
        else:
            raise AssertionError("Invalid parameters\n" + helpString)
    del argv
    del argc

    failures = []
    victories = []

    outFile.write("Initializing data structures..." + "\n")
    for u in uRange:
        domin_scores[u] = {}
        scores[u] = {}
        for sched in schedulers:
            scores[u][sched] = 0
            domin_scores[u][sched] = 0

    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = set()
        outFile.write("Launching simulations..." + "\n")
        for u in uRange:
            futures.update([executor.submit(oneTest, u) for n in range(NUMBER_OF_SYSTEMS)])

        outFile.write("Waiting for all threads to complete..." + "\n")

        for i, f in enumerate(concurrent.futures.as_completed(futures)):
            if i % (NUMBER_OF_SYSTEMS) == 0:  # this is 1/10th of the total count
                outFile.write("Completed " + str(i) + " systems")
            u, success, tau = f.result()
            for sched in success.keys():
                    if success[sched]:
                        scores[u][sched] += 1
                    otherSuccess = False
                    for otherSched in [s for s in success.keys() if s is not sched]:
                        otherSuccess = otherSuccess or success[otherSched]
                    if success[sched] and not otherSuccess:
                        domin_scores[u][sched] += 1
            if success[schedulers[1]] and not success[schedulers[0]]:
                failures.append(tau)
            if success[schedulers[0]] and not success[schedulers[1]]:
                victories.append(tau)

    outFile.write("Writing result to memory...")
    with open("mainSimuComp_results.pickle", "wb") as output:
        pickle.dump((domin_scores, scores, NUMBER_OF_SYSTEMS, uRange, schedulers, names, generate_synchronous_only, failures), output, pickle.HIGHEST_PROTOCOL)
        outFile.write("Done.")

    for fail in failures:
        outFile.write("FAIL", str(fail))
    # for vict in victories:
    #     outFile.write("VICT", str(vict))

from model import algorithms
from model import Task, TaskGenerator
from simulator import Simulator
from simulator.scheduler import Scheduler, LBLScheduler, PMImp

import random
import pickle
import concurrent.futures
import sys


def oneTest(utilization):
    global schedulers
    global CDF
    global generate_synchronous_only
    # print(utilization)
    Utot = utilization
    maxHyperT = 554400
    # maxHyperT = -1
    Tmin = 3
    Tmax = 50
    n = random.randint(2, 5)
    preemptionCost = 2
    tasks = TaskGenerator.generateTasks(
        Utot,
        n,
        maxHyperT,
        Tmin,
        Tmax,
        preemptionCost=preemptionCost,
        synchronous=generate_synchronous_only,
        constrDeadlineFactor=CDF
    )
    tau = Task.TaskSystem(tasks)
    # print(tau)

    Omax = max([task.O for task in tau.tasks])
    H = tau.hyperPeriod()
    stop = Omax + 10 * H  # FIXME
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
    elif name == "PTEDF":
        return Scheduler.PTEDF
    elif name == "PMImp":
        return PMImp.PMImp
    elif name == "LLF":
        return Scheduler.LLF
    elif name == "Meumeu":
        return Scheduler.ExhaustiveFixedPriority
    return None


if __name__ == '__main__':
    NUMBER_OF_SYSTEMS = 10
    uRange = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    schedulers = [PMImp.PMImp, Scheduler.ExhaustiveFixedPriority]
    names = ["PMImp", "Meumeu"]
    CDF = 0
    generate_synchronous_only = False
    outFilePath = "mainSimuComp_log.txt"
    pickFilePath = "mainSimuComp_results.pickle"
    writeVict = False
    writeFail = True

    helpString = \
        "Usage: python3 mainSimuComp.py <-paramName> <paramValue>\n\
        Parameters:\n\
        -sched1 : Name of the supposed 'best' schedulers\n\
        -sched2 : Name of the supposed 'worst' schedulers\n\
        -writeVict : Log systems scheduled by 1 but not by 2 (1/0, def: 0)\n\
        -writeFail : Log systems scheduled by 2 but not by 1 (1/0, def: 0)\n\
        -o : log file (default: " + outFilePath + "\n\
        -p : pickle file (default: " + pickFilePath + "\n\
        -n : number of systems per data point (def: 1000)\n\
        -synchr : generate synchronous system only (1/0 def: 0)\
        -cdf : float value of the CDF (0: implicit, 1: fully constrained) \
        "
    argv = sys.argv[1:]
    argc = len(argv)
    assert argc % 2 == 0, "Invalid number of arguments\n" + helpString
    for i in range(0, argc, 2):
        paramV = argv[i + 1]
        if argv[i] == "-o":
            outFile = open(paramV, "w")
        elif argv[i] == "-p":
            pickFilePath = paramV
        elif argv[i] == "-n":
            NUMBER_OF_SYSTEMS = int(paramV)
        elif argv[i] == "-synchr":
            generate_synchronous_only = True if int(paramV) == 1 else False
        elif argv[i] == "-writeVict":
            writeVict = True if int(paramV) == 1 else False
        elif argv[i] == "-writeFail":
            writeFail = True if int(paramV) == 1 else False
        elif argv[i] == "-cdf":
            CDF = int(paramV)
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

    print("Initializing data structures...")
    domin_scores = {}
    scores = {}
    failures = []
    victories = []
    for u in uRange:
        domin_scores[u] = {}
        scores[u] = {}
        for sched in schedulers:
            scores[u][sched] = 0
            domin_scores[u][sched] = 0

    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = set()
        print("Launching simulations...")
        for u in uRange:
            futures.update([executor.submit(oneTest, u) for n in range(NUMBER_OF_SYSTEMS)])

        print("Waiting for all threads to complete...")

        for i, f in enumerate(concurrent.futures.as_completed(futures)):
            if i % (NUMBER_OF_SYSTEMS) == 0:  # this is 1/10th of the total count
                print("Completed ", str(i), "/", NUMBER_OF_SYSTEMS * 10, " systems")
            u, success, tau = f.result()
            for sched in success.keys():
                    if success[sched]:
                        scores[u][sched] += 1
                    otherSuccess = False
                    for otherSched in [s for s in success.keys() if s is not sched]:
                        otherSuccess = otherSuccess or success[otherSched]
                    if success[sched] and not otherSuccess:
                        domin_scores[u][sched] += 1
            if writeFail:
                if success[schedulers[1]] and not success[schedulers[0]]:
                    failures.append(tau)
            if writeVict:
                if success[schedulers[0]] and not success[schedulers[1]]:
                    victories.append(tau)

    with open(outFilePath, "w") as outFile:
        outFile.write(
            "Report out of " + str(NUMBER_OF_SYSTEMS * len(uRange))
            + " systems\n"
        )
        outFile.write("===============================\n")
        if writeVict:
            if len(victories) == 0:
                outFile.write("No victories.\n")
            for vict in victories:
                outFile.write("VICT " + str(vict) + "\n")
            outFile.write("====================\n")
        if writeFail:
            if len(failures) == 0:
                outFile.write("No failures.\n")
            for fail in failures:
                outFile.write("FAIL " + str(fail) + "\n")

    print("Writing result to memory...")
    with open(pickFilePath, "wb") as output:
        pickle.dump((domin_scores, scores, NUMBER_OF_SYSTEMS, uRange, schedulers, names, generate_synchronous_only, failures), output, pickle.HIGHEST_PROTOCOL)
        print("Done.")

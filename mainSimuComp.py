from model import algorithms
from model import Task, TaskGenerator
from simulator import Simulator
from simulator.scheduler import Scheduler, ChooseKeepEDF, PALLF, LBLScheduler

import random
import pickle
import concurrent.futures


def oneTest(utilization):
    print(utilization)
    Utot = utilization
    maxHyperT = 360  # PPCM(2, 3, 5, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 22, 24, 25, 28, 30, 32)
    # maxHyperT = -1
    Tmin = 3
    Tmax = 50
    n = random.randint(2, 5)
    preemptionCost = 2
    constrDeadlineFactor = 0  # 0 is implicit, 1 is constrained
    tasks = TaskGenerator.generateTasks(Utot, n, maxHyperT, Tmin, Tmax, preemptionCost=preemptionCost, synchronous=False, constrDeadlineFactor=constrDeadlineFactor)
    tau = Task.TaskSystem(tasks)
    # print(tau)

    Omax = max([task.O for task in tau.tasks])
    H = tau.hyperPeriod()
    fpdit = algorithms.findFirstDIT(tau)
    stop = Omax + 4 * H  # FIXME
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

domin_scores = {}
scores = {}
NUMBER_OF_SYSTEMS = 1
uRange = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
schedulers = [Scheduler.EDF, Scheduler.PTEDF]
names = ["EDF", "PA-EDF"]

failures = []

executor = concurrent.futures.ProcessPoolExecutor()
futures = set()
for u in uRange:
    domin_scores[u] = {}
    scores[u] = {}
    for sched in schedulers:
        scores[u][sched] = 0
        domin_scores[u][sched] = 0

for u in uRange:
    futures.update([executor.submit(oneTest, u) for n in range(NUMBER_OF_SYSTEMS)])

for f in futures:
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


with open("mainSimuComp_results.pickle", "wb") as output:
    print("Writing result to memory...")
    pickle.dump((domin_scores, scores, NUMBER_OF_SYSTEMS, uRange, schedulers, names, failures), output, pickle.HIGHEST_PROTOCOL)
    print("Done.")

for fail in failures:
    print("FAIL", str(fail))

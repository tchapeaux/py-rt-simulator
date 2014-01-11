from model import algorithms
from model import Task, TaskGenerator
from simulator import Simulator
from simulator.scheduler import Scheduler, ChooseKeepEDF, PALLF, LBLScheduler

import random
import pickle
import concurrent.futures


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

domin_scores = {}
scores = {}
NUMBER_OF_SYSTEMS = 100
uRange = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
schedulers = [Scheduler.PTEDF, Scheduler.EDF]
names = ["PTEDF", "EDF"]
generate_synchronous_only = False

failures = []
victories = []

print("Initializing data structures...")
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

    print("Waiting for all threads to complete")

    for i, f in enumerate(concurrent.futures.as_completed(futures)):
        if i % (NUMBER_OF_SYSTEMS) == 0:  # this is 1/10th of the total count
            print("Completed", i, "systems")
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

print("Writing result to memory...")
with open("mainSimuComp_results.pickle", "wb") as output:
    pickle.dump((domin_scores, scores, NUMBER_OF_SYSTEMS, uRange, schedulers, names, generate_synchronous_only, failures), output, pickle.HIGHEST_PROTOCOL)
    print("Done.")

for fail in failures:
    print("FAIL", str(fail))
# for vict in victories:
#     print("VICT", str(vict))

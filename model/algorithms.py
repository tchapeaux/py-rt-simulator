import itertools
import math

from helper import myAlgebra
from model import newChineseRemainder
from functools import reduce


def findFirstDIT(tau):
    # language abuse ;-)
#   return findFirstPeriodicDIT(tau)
    return newChineseRemainder.newFindFirstPeriodicDIT(tau)


def isDefinitelyIdle(task, t):
    loc_t = (t - task.O) % task.T
    return t <= task.O or loc_t >= task.D or loc_t == 0


def YAfindFPDIT(tau):
    H = tau.hyperPeriod()
    omax, latestTask = max([(task.O, task) for task in tau.tasks])
    t = omax + 1  # omax is never a FPDIT (by definition)
    while t <= omax + H:
        # print("YA: t = ", t)
        notDefIdle = [task for task in tau.tasks if not isDefinitelyIdle(task, t)]
        if len(notDefIdle) > 0:
            # print("Not def idle:", notDefIdle)
            nextDeadlines = [myAlgebra.nextPeriodic(t, ta.T, ta.O + ta.D) for ta in notDefIdle]
            # print("deadlines:", nextDeadlines)
            t = max(nextDeadlines)
            continue
        else:
            return t
    return None


def LIPARIfindFPDIT(tau):
    omax = tau.omax()
    H = tau.hyperPeriod()
    arrivals = {}
    deadlines = {}
    for task in tau.tasks:
        arrivals[task] = task.O
        deadlines[task] = task.O + task.D
    aMin = 0
    while(aMin <= omax + H):
        d_next, task_d_next = min([(task.D, task) for task in tau.tasks])
        arrivals[task_d_next] += task_d_next.T
        aMin = min([arrivals[task] for task in tau.tasks])
        if aMin >= d_next:
            return d_next
    return None


def findFirstPeriodicDIT(tau):
    # Requires to solve several system of modular equations

    # Construction of the intervals
    intervals = [list(range(task.D, task.T)) for task in tau.tasks]
    for i, task in enumerate(tau.tasks):
        # 0, corresponding to the last/first case is missing from each interval
        intervals[i].append(0)
        # add Oi for the asynchronous case
        # This should have no effect in the synchronous case
        for j in range(len(intervals[i])):
            intervals[i][j] += task.O
            intervals[i][j] %= task.T

    T = [task.T for task in tau.tasks]
    Omax = max([task.O for task in tau.tasks])

    # Pre-processing for our congruence algorithm
    primalSystem_T = myAlgebra.toPrimalPowerSystem(T)
    currentMin = None
    numberOfCombinations = reduce(lambda x, y: x*len(y), intervals, 1)
    for i, combination in enumerate(itertools.product(*intervals)):
        # if i % 1000 == 0: print "combination ", i, "/", numberOfCombinations
        tIdle = myAlgebra.congruencePrimalPower(primalSystem_T, combination)

        if tIdle is not None and tIdle <= Omax:
            while tIdle <= Omax:
                tIdle += tau.hyperPeriod()
        if tIdle is not None:
            if currentMin is None or tIdle < currentMin:
                currentMin = tIdle
    return currentMin


def findSynchronousInstant(tau):
    T = [task.T for task in tau.tasks]
    primalSystem_T = myAlgebra.toPrimalPowerSystem(T)
    offsets = [task.O % task.T for task in tau.tasks]
    tSync = myAlgebra.congruencePrimalPower(primalSystem_T, offsets)
    return tSync


def findBusyPeriod(tau):
    # for synchronous arbitrary deadline:
    # fixed-point-iteration
    # w0 = sum_i Ci
    # w{k+1} = sum_{i} ceil(w_k / Ti) Ci
    assert tau.isSynchronous(), "findBusyPeriod: not a synchronous system"

    Cset = [task.C for task in tau.tasks]
    wNew = sum(Cset)
    wOld = 0
    hyperT = tau.hyperPeriod()
    while(wNew != wOld and wNew < hyperT):
        wOld = wNew
        wNew = 0
        assert wOld > wNew, "findBusyPeriod: wOld <= wNew. Old:" + str(wOld) + ", new:" + str(wNew)
        for task in tau.tasks:
            wNew += int(math.ceil(wOld*1.0 / task.T)*task.C)
    return wNew


def dbf_synchr(tau, t):
    return tau.dbf(0, t)


def dbf(tau, t1, t2):
    return tau.dbf(t1, t2)


def completedJobCount(task, t1, t2):
    return task.completedJobCount(t1, t2)


def dbfTest(tau, firstDIT=None):
    # TODO : add lowerLimit (already present in all subfunctions)
    Omax = max([task.O for task in tau.tasks])
    if firstDIT is None:
        if Omax == 0:
            upperLimit = findBusyPeriod(tau)
        else:
            upperLimit = Omax + 2 * tau.hyperPeriod()
        lowerLimit = Omax
    else:
        lowerLimit = Omax
        upperLimit = firstDIT + tau.hyperPeriod()

    for arrival, deadline in tau.dbf_intervals(lowerLimit, upperLimit):
        testResult = dbf(tau, arrival, deadline) <= deadline
        if testResult is False:
            return False

    # If all previous tests succeed, the system is feasible
    return True

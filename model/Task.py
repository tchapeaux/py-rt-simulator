import math
from helper import myAlgebra
from model import Job
from model import cspace

import array
import heapq
import copy

import re


class Task(object):
    def __init__(self, O, C, D, T, alpha=0):
        self.O = O
        self.C = C
        self.D = D
        self.T = T
        self.alpha = alpha

    @staticmethod
    def fromText(taskStr):
        taskRegex = r"((?P<O>[0-9]+), (?P<C>[0-9]+), (?P<D>[0-9]+), (?P<T>[0-9]+), (?P<a>[0-9]+))"
        reRes = re.search(
            taskRegex,
            str(taskStr),
            re.DOTALL
        )
        assert reRes, "Task.fromText -- Incorrect task string:\t" + taskStr
        (O, C, D, T, alpha) = tuple((int(reRes.group(c)) for c in "OCDTa"))
        return Task(O, C, D, T, alpha=alpha)

    def __repr__(self):
        reprStr = ""
        reprStr += "("
        reprStr += str(self.O)
        reprStr += ", "
        reprStr += str(self.C)
        reprStr += ", "
        reprStr += str(self.D)
        reprStr += ", "
        reprStr += str(self.T)
        reprStr += ", "
        reprStr += str(self.alpha)
        reprStr += ")"
        return reprStr

    def utilization(self):
        return (1.0 * self.C) / self.T

    def completedJobCount(self, t1, t2):
        jobBeforeT2 = int(math.floor(1.0 * (t2 - self.O - self.D) / self.T))
        jobBeforeT1 = int(math.ceil(1.0 * (t1 - self.O) / self.T))
        return max(0, jobBeforeT2 - jobBeforeT1 + 1)

    def getJob(self, arrival):
        assert (arrival - self.O) % self.T == 0
        return Job.Job(self, arrival)

    def __lt__(self, other):  # will be used to deterministically solve conflict
        return id(self) < id(other)

    # def __eq__(self, other):
    #     return id(self) == id(other)

    # def __ne__(self, other):
    #     return not self.__eq__(other)

    # def __hash__(self):  # required to be used in a set
    #     return (
    #         hash(self.O) ^
    #         hash(self.C) ^
    #         hash(self.D) ^
    #         hash(self.T) ^
    #         hash(self.alpha)
    #         )


class TaskSystem(object):
    def __init__(self, tasks):
        self.tasks = tasks
        self._hyperperiod = None
        #self.hyperT = self.hyperPeriod()

    @staticmethod
    def fromText(systemLines):
        tasks = []
        for taskStr in systemLines:
            taskStr = taskStr.strip()
            if len(taskStr) > 2 and '#' not in taskStr:
                tasks.append(Task.fromText(taskStr))
        return TaskSystem(tasks)

    @staticmethod
    def fromFile(f):
        string = f.readlines()
        return TaskSystem.fromText(string)

    def hyperPeriod(self):
        if not self._hyperperiod:
            Tset = [task.T for task in self.tasks]
            self._hyperperiod = myAlgebra.lcmArray(Tset)
        return self._hyperperiod

    def hasConstrainedDeadline(self):
        check = True
        for task in self.tasks:
            check = check and task.D <= task.T
        return check

    def isSynchronous(self):
        return max([task.O for task in self.tasks]) == 0

    def systemUtilization(self):
        u = 0
        for task in self.tasks:
            u += task.utilization()
        return u

    def omax(self):
        return max([task.O for task in self.tasks])

    def util(self):
        return self.systemUtilization()

    def __repr__(self):
        tauString = "TASK SYSTEM"
        for task in self.tasks:
            tauString += "\n\t" + str(task)
        return tauString

    def synchronousEquivalent(self):
        if self.isSynchronous():
            return self
        else:
            sync = copy.deepcopy(self)
            for t in sync.tasks:
                t.O = 0
            return sync

    def firstSynchronousInstant(self):
        if(self.isSynchronous()):
            return 0
        else:
            T = [task.T for task in self.tasks]
            primalSystem_T = myAlgebra.toPrimalPowerSystem(T)
            offsets = [task.O % task.T for task in self.tasks]
            H = self.hyperPeriod()
            Omax = self.omax()
            tSync = myAlgebra.congruencePrimalPower(primalSystem_T, offsets)
            if tSync:
                while tSync < Omax:
                    tSync += H
            return tSync

    def dbf(self, t1, t2):
        dbfSum = 0
        for task in self.tasks:
            dbfSum += task.completedJobCount(t1, t2) * task.C
        return dbfSum

    def dbf_intervals(self, lowerLimit, upperLimit):
        starts = {}  # will contain all tasks first arrival
        for task in self.tasks:
            starts[task] = int(task.O + task.T * max(0, math.ceil((lowerLimit - task.O) / float(task.T))))
        dSet = set()
        for task in self.tasks:
            deadlineInRange = list(range(starts[task] + task.D, upperLimit + 1, task.T))
            if len(deadlineInRange) == 0:  # then add one anyway
                deadlineInRange = [starts[task] + task.D]
            dSet.update(deadlineInRange)
        deadlines = sorted(array.array('i', dSet))
        arrivals = []
        if not self.isSynchronous():
            heapq.heapify(arrivals)
            for task in self.tasks:
                heapTuple = (starts[task], task)
                heapq.heappush(arrivals, heapTuple)
        else:
            arrivals.append((0, self.tasks[0]))

        lastArrival = None
        lastDeadlineIndex = 0
        while arrivals:
            arrival, task = heapq.heappop(arrivals)
            if arrival != lastArrival:
                lastArrival = arrival
                dTuples = [(cnt, d) for cnt, d in enumerate(deadlines[lastDeadlineIndex:]) if d > arrival]
                if dTuples:
                    dIndexes, dValues = list(zip(*dTuples))
                    lastDeadlineIndex += dIndexes[0]  # add number of skipped deadlines
                    for deadline in dValues:
                        yield arrival, deadline
            nextArrival = arrival + task.T
            if not self.isSynchronous() and nextArrival + task.D <= upperLimit:
                heapTuple = (nextArrival, task)
                heapq.heappush(arrivals, heapTuple)

    def cSpaceSize(self, acspace=None):
        if acspace is None:
            acspace = cspace.Cspace(self)
        return acspace.size(self)

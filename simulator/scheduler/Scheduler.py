import itertools
import pdb
from helper import myAlgebra


class SchedulerDP(object):
    def __init__(self, tau):
        pass

    def priority(self, job, simu):
        pass

    def preemptEqualPriorities(self):
        return True

    def initInstant(self):
        # called at the start of each instant (when time is incremented)
        pass

    # General purpose functions for schedulers

    def isJobExecuting(self, job, simu):
        return job in [cpu.job for cpu in simu.CPUs]

    def finishTime(self, job, simu):
        return simu.t + job.computationLeft()

    def nextArrival(self, task, t):
        """ returns the earliest job arrival of task after or at t """
        return myAlgebra.nextPeriodic(t, task.T, task.O)


class LLF(SchedulerDP):
    def __init__(self, tau, preemptionAware=True):
        super().__init__(tau)
        self.prioOffset = max([task.C for task in tau.tasks]) + 1
        self.tau = tau
        self.preemptionAware = preemptionAware

    def priority(self, job, simu):
        # Is LLF supposed to be aware of the added preemption cost?
        # Here we suppose that yes
        slackTime = max(0, job.deadline - (simu.t + job.computationLeft()))
        if not self.preemptionAware and self.isJobExecuting(job, simu):
            slackTime += job.alpha()
        return 1 / (self.prioOffset + slackTime)

    def preemptEqualPriorities(self):
        return False


class PTEDF(SchedulerDP):
    def __init__(self, tau):
        super().__init__(tau)
        self.tau = tau
        self.prioOffset = max([task.alpha for task in tau.tasks])

    def shouldPreempt(self, simu, t2, job):  # TODO and TOUSE
        """ check if job will be preempted at t2
            args :
                - simu: Simulation at instant t
                - t2: instant >= t
                - job: current job at instant t """
        assert simu.t <= t2
        # check for future arrivals between t and t2
        futureJobs = []
        for otherTask in [T for T in self.tau.tasks if T is not job.task]:
            nA = self.nextArrival(otherTask, simu.t)
            futureJobs.append(otherTask.getJob(nA) if nA <= t2 else None)
        futureJobs = [j for j in futureJobs if j]  # filter
        sortedOtherJobs = sorted(simu.getCurrentJobs(getBusyJobs=False) + futureJobs, key=lambda j: j.deadline)
        sortedOtherJobs = [j for j in sortedOtherJobs if j is not job and j.deadline <= job.deadline]  # filter
        minimalCompLeft = job.computationLeft() - (t2 - simu.t)
        for otherJob in sortedOtherJobs:
            laxOther = (otherJob.deadline - t2) - otherJob.computationLeft()
            # print("\t\t\tjob", otherJob, "is waiting with laxity", laxOther, "compLeft:", minimalCompLeft)
            if laxOther < minimalCompLeft:
                return True
            else:
                minimalCompLeft += otherJob.computationLeft()
        return False

    def default_priority(self, job, simu):
        # lax = (job.deadline - simu.t) - job.computationLeft()
        return 1 / job.deadline

    def priority(self, job, simu):
        # print("\t\tPriority of job", job)
        t = simu.t
        busyJobs = [J for J in simu.getCurrentJobs(getWaitingJobs=False)]
        idleInstant = len(busyJobs) == 0
        if idleInstant:
            # print("\t\t\tIdle instant")
            # check if other jobs will be preemptive
            if self.shouldPreempt(simu, t + job.alpha(), job):
                    return float("-inf")
            # print("\t\t\tNo reason to idle")
            return self.default_priority(job, simu)
        elif job in busyJobs:
            # print("\t\t\tBusy job")
            # check if continuing this job is viable for all waiting jobs
            # consider each job by order of deadline
            if self.shouldPreempt(simu, t, job):
                return float("-inf")
            # print("\t\t\tNo arrival")
            return 1
        # Waiting job in a non-idle instant (should have a priority > 0)
        # print("\t\t\tWaiting job in a non-idle instant")
        return self.default_priority(job, simu)


class ArbitraryScheduler(SchedulerDP):
    """
    Allow the user to define his own scheduling.
        format of userSchedule : userSchedule[t] = task to execute
        if t > len(userSchedule), userSchedule is assumed periodic
    """
    def __init__(self, tau, userSchedule):
        super().__init__(tau)
        self.tau = tau
        self.userSchedule = userSchedule

    def priority(self, job, simu):
        t = simu.t % len(self.userSchedule)
        return 1 if job.task == self.userSchedule[t] else -1


class SpotlightEDF(SchedulerDP):
    """ Non-optimal algorithm taking preemption cost into account."""
    def __init__(self, tau):
        super().__init__(tau)
        self.prioOffset = max([task.alpha for task in tau.tasks])

    def priority(self, job, simu):
        if self.isJobExecuting(job, simu):
            return 1.0/(self.prioOffset + job.deadline - job.alpha())
        else:
            return 1.0/(self.prioOffset + job.deadline)


class SchedulerFJP(SchedulerDP):
    def priority(self, job, simu=None):
        if job.priority is not None:
            return job.priority

    def preemptEqualPriorities(self):
        return False


class EDF(SchedulerFJP):
    def priority(self, job, simu=None):
        super().priority(job, simu)
        return 1 / job.deadline


class SchedulerFTP(SchedulerFJP):
    def __init__(self, tau):
        super().__init__(tau)
        self.priorities = self.orderPriorities(tau.tasks)

    def orderPriorities(self, taskArray):
        # return priorities array in priority order (decreasing)
        pass

    def priority(self, job, simu=None):
        super().priority(job, simu)
        for i, task in enumerate(reversed(self.priorities)):  # priorities is decreasing
            if job.task is task:
                return i + 1  # prio = 0 is for idle cpu
        raise ValueError("Task of job " + str(job) + "not recognized")


class FixedPriority(SchedulerFTP):
    """Schedule the jobs according to given task priorities"""

    def __init__(self, tau, prioArray):
        """prioArray : list of priorities in the same order as tau.tasks"""
        self.prioArray = prioArray
        super().__init__(tau)

    def orderPriorities(self, taskArray):
        assert len(self.prioArray) == len(taskArray), str(len(taskArray)) + "\t" + str(len(self.prioArray))
        priorities = []
        for prio, task in sorted(zip(self.prioArray, taskArray)):
            priorities.append(task)
        return priorities


class ExhaustiveFixedPriority(FixedPriority):
    def __init__(self, tau, nbrCPUs, abortAndRestart):
        self.tau = tau
        self.m = nbrCPUs
        self.abortAndRestart = abortAndRestart
        self.foundFeasible = None
        feasiblePriorities = self.exhaustiveSearch()
        super().__init__(tau, feasiblePriorities)

    def exhaustiveSearch(self):
        from simulator.Simulator import Simulator
        taskArray = self.tau.tasks
        priorities = [i for i in range(0, len(taskArray))]
        self.foundFeasible = False
        for prio in itertools.permutations(priorities):
            simu = Simulator(self.tau, None, self.m, FixedPriority(self.tau, prio), self.abortAndRestart, drawing=False)
            simu.run(stopAtDeadlineMiss=True)
            if simu.success():
                self.foundFeasible = True
                return prio
        return priorities  # foundFeasible is still False


class RM(SchedulerFTP):

    def orderPriorities(self, taskArray):
        priorities = []
        for task in taskArray:
            for i in range(len(priorities)):
                if task.T < priorities[i].T:
                    priorities.insert(i, task)
            if task not in priorities:
                priorities.append(task)
        return priorities


class DM(SchedulerFTP):

    def orderPriorities(self, taskArray):
        return sorted(taskArray, key=lambda t: t.D)

from heapq import heapify, heappop, heappush
import pdb

from model.CPU import CPU
from model import algorithms
from simulator.drawer import Drawer
from simulator.JobConfiguration import JobConfiguration


def heappeek(heap):
    return heap[0] if len(heap) > 0 else None


class Simulator(object):  # Global multiprocessing only
    def __init__(self, tau, stop, nbrCPUs, scheduler, abortAndRestart, verbose=False, drawing=True):
        """stop can be set to None for default value"""
        self.verbose = verbose
        self.system = tau
        self.m = nbrCPUs
        self.AR = abortAndRestart
        if stop is None:
            fpdit = algorithms.findFirstDIT(tau)
            if fpdit:
                stop = fpdit + tau.hyperPeriod()
            else:
                stop = tau.omax() + tau.hyperPeriod()
        self.stop = stop + 1  # I just solved every OBOE in the world
        self.lastConfig = None

        # CPUs are accessible via either
        # - CPUs : a list with fixed ordering
        # - activeCPUsHeap and preemptedCPUs : where the ordering is not guaranteed
        self.CPUs = [CPU() for i in range(self.m)]
        self.activeCPUsHeap = []
        heapify(self.activeCPUsHeap)
        for cpu in self.CPUs:
            heappush(self.activeCPUsHeap, cpu)
        self.preemptedCPUs = set()

        self.scheduler = scheduler

        self.t = -1
        self.deadlineMisses = []
        self.isStable = False  # stable = periodic phase attained
        self.activeJobsHeap = []
        heapify(self.activeJobsHeap)

        if drawing:
            from simulator.drawer import CairoDrawer
            self.drawer = CairoDrawer.CairoDrawer(self, stop)
            # from simulator.drawer import PILDrawer
            # self.drawer = PILDrawer.PILDrawer(self, stop)
        else:
            self.drawer = None

    def saveConfiguration(self):
        jobs = self.getCurrentJobs()
        self.lastConfig = set()
        for job in jobs:
            self.lastConfig.add(JobConfiguration(job, self.t))

    def checkConfig(self):
        # TODO: adapt for arbitrary deadline (make copy of lastConfig and current jobs and remove pairs)
        assert self.lastConfig is not None, "checkConfig: save config first"
        jobs = self.getCurrentJobs()
        if len(self.lastConfig) != len(jobs):
            return False
        for jobConfig in self.lastConfig:
            foundJob = False
            for job in jobs:
                if job.task is not jobConfig.task:
                    continue
                if self.t - job.arrival != jobConfig.activeTime:
                    continue
                if job.computation != jobConfig.computedTime:
                    continue
                if job.preemptionTimeLeft != jobConfig.preemptionTime:
                    continue
                foundJob = True
                break  # try next job config
            if not foundJob:
                return False
        return True

    def activateCPUs(self):
    # move active CPU from preemptedCPUs to activeCPUsHeap
        cpuToActivate = []
        for cpu in self.preemptedCPUs:
            if cpu.job.preemptionTimeLeft == 0:
                cpuToActivate.append(cpu)
        for cpu in cpuToActivate:
            self.preemptedCPUs.remove(cpu)
            heappush(self.activeCPUsHeap, cpu)

    def getCurrentJobs(self, getWaitingJobs=True, getBusyJobs=True):
        waitingJobs = []
        busyJobs = []
        if getWaitingJobs:
            waitingJobs = [job for prio, job in self.activeJobsHeap]
        if getBusyJobs:
            busyJobs = [job for job in [cpu.job for cpu in self.CPUs] if job]
        return waitingJobs + busyJobs

    def updatePriorities(self, job="all"):
        jobs = []
        if job == "all":
            jobs.extend(self.getCurrentJobs())
        else:
            jobs.append(job)
        for job in jobs:
            job.priority = self.scheduler.priority(job, self)
            if self.verbose:
                print("\t\tpriority of ", job, "is now", job.priority)

    def updateHeaps(self):
        # possible bottleneck
        newJobHeap = []
        for prio, job in self.activeJobsHeap:
            newJobHeap.append((-1 * job.priority, job))
        self.activeJobsHeap = newJobHeap
        heapify(self.activeCPUsHeap)
        heapify(self.activeJobsHeap)

    def mostPrioritaryJob(self):
        return heappeek(self.activeJobsHeap)[1] if len(self.activeJobsHeap) > 0 else None

    def leastPrioritaryCPU(self):
        return heappeek(self.activeCPUsHeap)

    def cleanFinishedJobs(self):
        self.activateCPUs()
        for cpu in self.activeCPUsHeap:
            if cpu.job and cpu.job.isFinished():
                if self.verbose:
                    print("\tCPU ", cpu, "is finished")
                cpu.job = None
        self.updatePriorities()
        self.updateHeaps()

    def checkDeadlineMiss(self):
        for job in self.getCurrentJobs():
            assert job
            if self.t >= job.deadline:
                assert job.computation < job.task.C
                self.deadlineMisses.append((self.t, job))

    def checkJobArrival(self):
        for task in self.system.tasks:
            if self.t >= task.O and self.t % task.T == task.O % task.T:
                newJob = task.getJob(self.t)
                newJob.priority = self.scheduler.priority(newJob, self)
                if self.verbose:
                    print("\tarrival of job", newJob)
                heappush(self.activeJobsHeap, (-1 * newJob.priority, newJob))

    def handlePreemptions(self):
        # update priorities
        self.updatePriorities()
        self.updateHeaps()
        # check for preemptions
        if self.verbose:
            print("\t", self.mostPrioritaryJob(), "(", str(self.mostPrioritaryJob().priority if self.mostPrioritaryJob() else None), ") vs.", self.leastPrioritaryCPU(), "(", str(self.leastPrioritaryCPU().priority() if self.leastPrioritaryCPU() else None), ")")
        if self.mostPrioritaryJob() and self.leastPrioritaryCPU() and self.mostPrioritaryJob().priority >= self.leastPrioritaryCPU().priority():
            # special case of equal priorities : decided by the scheduler
            if self.mostPrioritaryJob().priority == self.leastPrioritaryCPU().priority():
                if self.verbose:
                    print("equal priority: preemption policy of scheduler :", self.scheduler.preemptEqualPriorities())
                if not self.scheduler.preemptEqualPriorities():
                    return
            if self.verbose:
                print("\tpremption!")
            preemptiveJob = heappop(self.activeJobsHeap)[1]
            preemptedCPU = heappop(self.activeCPUsHeap)
            preemptedJob = preemptedCPU.job  # may be None

            # assign preemptive job to the CPU and push CPU in the correct heap
            self.updatePriorities(job=preemptiveJob)
            preemptedCPU.job = preemptiveJob
            if preemptiveJob.preempted and preemptiveJob.alpha() > 0:
                self.preemptedCPUs.add(preemptedCPU)
            else:
                heappush(self.activeCPUsHeap, preemptedCPU)
            if preemptiveJob.preempted:
                preemptiveJob.preempted = False

            # put the preempted job back in the active job heap
            if preemptedJob:
                preemptedJob.preempted = True
                preemptedJob.preemptionTimeLeft = preemptedJob.alpha()
                if self.AR:
                    preemptedJob.computation = 0
                    if self.drawer:
                        self.drawer.drawAbort(preemptedJob.task, self.t)
                heappush(self.activeJobsHeap, (-1 * preemptedJob.priority, preemptedJob))

            if self.verbose:
                print("\t", self.mostPrioritaryJob(), "(", str(self.mostPrioritaryJob().priority if self.mostPrioritaryJob() else None), ") vs.", self.leastPrioritaryCPU(), "(", str(self.leastPrioritaryCPU().priority() if self.leastPrioritaryCPU() else None), ")")

    def computeBusyJobs(self):
        for cpu in self.activeCPUsHeap:
            if cpu.job:
                cpu.job.computation += 1

    def computePreemptionRecovery(self):
        for cpu in self.preemptedCPUs:
            cpu.job.preemptionTimeLeft -= 1

    def incrementTime(self):
        self.t += 1
        # if self.t == 2:
        #     pdb.set_trace()
        if self.verbose: print("t=", self.t)
        if self.t > self.system.omax() and (self.t - self.system.omax()) % self.system.hyperPeriod() == 0:
            if self.lastConfig is not None and self.checkConfig() is True:
                self.isStable = True
                if self.verbose:
                    print("Stable Config !")
            else:
                self.isStable = False
            self.saveConfiguration()
        self.scheduler.initInstant()
        self.cleanFinishedJobs()  # remove finished job from CPUs
        self.checkDeadlineMiss()
        self.checkJobArrival()
        self.handlePreemptions()
        self.computeBusyJobs()
        self.computePreemptionRecovery()
        if self.verbose:
            for i, cpu in enumerate(self.CPUs):
                print("\t", i, cpu)
                if cpu in self.preemptedCPUs:
                    print("\t(preempt)", cpu.job.preemptionTimeLeft, "left")

    def run(self, stopAtDeadlineMiss=True, stopAtStableConfig=True):
        try:
            while(self.t < self.stop):
                self.incrementTime()
                # if self.t % 100 == 0:
                #     print("t", self.t, "/", self.stop)
                if self.drawer:
                    self.drawer.drawInstant(self.t)

                for missT, job in self.deadlineMisses:
                    if missT == self.t:
                        # new deadline miss
                        if self.drawer:
                            self.drawer.drawDeadlineMiss(self.t, job.task)
                        if self.verbose:
                            print("DEADLINE MISS at t=", (missT - 1), "for job", job)
                        if stopAtDeadlineMiss:
                            break
                if stopAtStableConfig and self.isStable:
                    break
        finally:
            if self.drawer:
                self.drawer.terminate()

    def success(self):
        assert self.t >= 0, "Simulator.success: call run() first"
        if len(self.deadlineMisses) > 0:
            if self.verbose:
                print("FAILURE: some deadlines were missed")
            return False
        if not self.isStable:
            if self.verbose:
                print("FAILURE: stable schedule not attained")
            return False
        return True

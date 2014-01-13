from simulator.scheduler import Scheduler


class PMImp(Scheduler.SchedulerDP):
    PRIO_MIN = -1 * float("inf")
    PRIO_MAX = float("inf")

    def __init__(self, tau):
        super(PMImp, self).__init__(tau)
        self.prioOffset = max([task.alpha for task in tau.tasks]) + 1
        self.laxitiesCounter = None

    def initInstant(self):
        super().initInstant()

    def preemptEqualPriorities(self):
        # quick hack to prevent looping in free-preemption systems
        if self.prioOffset > 1:
            return True
        else:
            return False

    def getLaxity(self, job, simu):
        compLeft = job.computationLeft()
        lax = job.deadline - (simu.t + compLeft)
        return max(0, lax)

    def busyJobPriority(self, job, simu):
        assert self.isJobExecuting(job, simu)
        # must stop only if another job has no (cumulative) slack time
        waitingJobs = simu.getCurrentJobs(getBusyJobs=False)
        sortedWJ = sorted(waitingJobs, key=lambda x: x.deadline)
        cumulExecTimeLeft = 0
        for waitingJ in sortedWJ:
            if self.getLaxity(waitingJ, simu) - cumulExecTimeLeft <= 0:
                return PMImp.PRIO_MIN
            cumulExecTimeLeft += waitingJ.computationLeft()
        # if no job has laxity 0
        return PMImp.PRIO_MAX

    def waitingJobPriority(self, job, simu):
        assert not self.isJobExecuting(job, simu)
        return 1 / (job.deadline + self.prioOffset)

    def priority(self, job, simu):
        if self.isJobExecuting(job, simu):
            return self.busyJobPriority(job, simu)
        else:
            return self.waitingJobPriority(job, simu)

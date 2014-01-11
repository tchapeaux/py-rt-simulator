from simulator.scheduler import Scheduler


class PALLF(Scheduler.SchedulerDP):
    def __init__(self, tau):
        super(PALLF, self).__init__(tau)
        self.prioOffset = max([task.alpha for task in tau.tasks]) + 1

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

    def earliestPreempArrival(self, job, simu):
        # return earliest time at which job will be preempted if it is chosen now
        t = simu.t
        finishTime = self.finishTime(job, simu)
        # Find next preemptive job arrival amongst tasks
        candidate = None
        for task in simu.system.tasks:
            nextArrival = self.nextArrival(task, t)
            # expected priorities (based on lax)
            jobExecLeftAtArrival = max(0, finishTime - nextArrival)
            arrivalLax = task.D - task.C
            if (
                nextArrival < finishTime and
                arrivalLax < jobExecLeftAtArrival and
                (candidate is None or nextArrival < candidate)
            ):
                candidate = nextArrival
        return candidate

    def priority(self, job, simu):
        lax = self.getLaxity(job, simu)
        if self.isJobExecuting(job, simu):
            return 1 / (self.prioOffset + lax - job.alpha())
        if job.alpha() > 1:
            # If executing now is sure to result in costly preemption, idle
            epa = self.earliestPreempArrival(job, simu)
            if epa and epa - simu.t <= job.alpha():
                return -1 * float("inf")
        # Is it necessary to preempt the least prioritary busy job?
        lpbCPU = simu.leastPrioritaryCPU()
        if lpbCPU and lpbCPU.job and lpbCPU.job.computationLeft() <= lax:
            return -1 * float("inf")
        return 1/(self.prioOffset + lax)

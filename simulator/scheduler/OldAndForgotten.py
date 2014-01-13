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


class ChooseKeepEDF(Scheduler.SchedulerDP):
    def __init__(self, tau):
        super(ChooseKeepEDF, self).__init__(tau)
        self.prioOffset = max([task.alpha for task in tau.tasks])

    def idleCPUsCount(self, simu):
        return len([cpu for cpu in simu.CPUs if cpu.job is None])

    def earliestPreempArrival(self, job, simu):
        # return earliest time at which job will be preempted if it is chosen now
        t = simu.t
        jobP = 1/(self.prioOffset + job.deadline - job.alpha())
        finishTime = self.finishTime(job, simu)
        # test against priority of next arrival of each task
        candidate = None
        for task in simu.system.tasks:
            nextArrival = self.nextArrival(task, t)
            prio = 1.0/(self.prioOffset + nextArrival + task.D)
            if prio >= jobP and nextArrival < finishTime and (candidate is None or nextArrival < candidate):
                candidate = nextArrival
        return candidate

    def priority(self, job, simu):
        # if simu.t == 2 and job.deadline == 9:
        #     pdb.set_trace()
        if self.isJobExecuting(job, simu):
            return 1.0/(self.prioOffset + job.deadline - job.alpha())
        epa = self.earliestPreempArrival(job, simu)
        if epa and epa - simu.t <= job.alpha():  # execution would cost more than idling
            return -1 * float("inf")
        else:
            return 1.0/(self.prioOffset + job.deadline)

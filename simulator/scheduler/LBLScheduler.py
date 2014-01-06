from simulator.scheduler import Scheduler


class LBLScheduler(Scheduler.SchedulerDP):
    def __init__(self, tau, schedFJPClass):
        super(LBLScheduler, self).__init__(tau)
        self.tau = tau
        self.schedFJP = schedFJPClass(tau)

    def preemptEqualPriorities(self):
        return False

    def earliestPreemptiveArrival(self, job, t):
        """ returns the earliest time after t at which job would be preempted """
        assert job.task in self.tau.tasks
        candidate = None
        jobP = self.schedFJP.priority(job)
        for otherTask in [ta_ for ta_ in self.tau.tasks if ta_ is not job.task]:
            if t <= otherTask.O:
                nextArrival = otherTask.O
            else:
                nextArrival = t + (otherTask.T - (t - otherTask.O) % otherTask.T)
            arrivJob = otherTask.getJob(nextArrival)
            arrivP = self.schedFJP.priority(arrivJob)
            if (candidate is None or nextArrival < candidate) and arrivP > jobP:
                candidate = nextArrival
        return candidate

    def priority(self, job, simu):
        if job in simu.getCurrentJobs(getBusyJobs=False):
            epa = self.earliestPreemptiveArrival(job, simu.t)
            finishTime = simu.t + job.computationLeft()
            if epa and epa < finishTime and epa < simu.t + job.alpha():
                return float("-inf")
        return self.schedFJP.priority(job)


class LBLEDF(LBLScheduler):
    """LBL Scheduler based on EDF"""
    def __init__(self, tau):
        super(LBLEDF, self).__init__(tau, Scheduler.EDF)

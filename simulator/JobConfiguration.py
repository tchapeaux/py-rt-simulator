class JobConfiguration(object):
    def __init__(self, job, t):
        self.task = job.task
        self.activeTime = t - job.arrival
        self.computedTime = job.computation
        self.preemptionTime = job.preemptionTimeLeft

    def __repr__(self):
        reprString = "("
        reprString += ", ".join([str(self.task), str(self.activeTime), str(self.computedTime), str(self.preemptionTime)])
        reprString += ")"
        return reprString

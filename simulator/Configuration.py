import pdb


class JobConfiguration(object):
    def __init__(self, job, t):
        self.task = job.task
        self.activeTime = t - job.arrival
        self.computedTime = job.computation
        self.preemptionTime = job.preemptionTimeLeft

    def __eq__(self, otherConfig):
        return self.__dict__ == otherConfig.__dict__

    def __ne__(self, otherConfig):
        return not self.__eq__(otherConfig)

    def __hash__(self):  # required to be used in a set
        return (
            hash(self.task) ^
            hash(self.activeTime) ^
            hash(self.computedTime) ^
            hash(self.preemptionTime)
            )

    def __repr__(self):
        reprString = "("
        reprString += ", ".join([str(self.task), str(self.activeTime), str(self.computedTime), str(self.preemptionTime)])
        reprString += ")"
        return reprString


class SystemConfiguration(object):
    def __init__(self, jobs, t):
        self.jobConfigs = set()
        for job in jobs:
            self.jobConfigs.add(JobConfiguration(job, t))

    def __eq__(self, otherConfig):
        # pdb.set_trace()
        if len(self.jobConfigs) != len(otherConfig.jobConfigs):
            return False
        # find a job config in other for each of our own job config
        otherFounds = set()  # mark already matched job config of other
        for jC in self.jobConfigs:
            found = False
            for otherJC in otherConfig.jobConfigs:
                if otherJC not in otherFounds and jC == otherJC:
                    found = True
                    continue
            if not found:
                return False
        return True

    def __hash__(self):
        if len(self.jobConfigs) > 0:
            currentHash = 0
            for jobC in self.jobConfigs:
                currentHash ^= hash(jobC)
            return currentHash
        else:
            return 0

    def __repr__(self):
        reprString = "System Config:\n"
        reprString += "\n".join([str(jC) for jC in self.jobConfigs])
        if len(self.jobConfigs) == 0:
            reprString += "Empty!"
        return reprString

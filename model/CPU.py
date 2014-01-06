class CPU(object):
    def __init__(self):
        self.job = None

    def isIdle(self):
        return self.job is None

    def priority(self):
        return self.job.priority if self.job else 0

    def __lt__(self, other):
        return self.priority() < other.priority()

    def __str__(self):
        return "CPU " + str(id(self)) + " containing " + str(self.job)

class Drawer(object):
    """Abstract drawer class used by a Simulator to display results"""
    def __init__(self, simu, stop):
        """param:
        - Simu is the instance of Simulator which shall be drawn
        - stop is the maximal time which shall be simulated"""
        self.simu = simu
        self.stop = stop

    def drawInstant(self, t):
        """Draw instant t in the simulation"""
        raise NotImplementedError("Drawer: attempted to call abstract method")

    def drawAbort(self, task, t):
        """Draw an abort of task at time t in the Abort/Restart model"""
        raise NotImplementedError("Drawer: attempted to call abstract method")

    def drawDeadlineMiss(self, t, task):
        """Draw a deadline miss for task at time t"""
        raise NotImplementedError("Drawer: attempted to call abstract method")

    def terminate(self):
        """Called at the end of the simulation"""
        raise NotImplementedError("Drawer: attempted to call abstract method")

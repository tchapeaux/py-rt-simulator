from simulator.drawer.Reporter import Reporter

from model import algorithms

import math


class PictureDrawer(Reporter):

    """Abstract reporter which display a single picture of the execution when it stops"""

    def __init__(self, simu, stop, showLabels=True, showPrio=False, blackandwhite=False):
        self.showLabels = showLabels
        self.showPrio = showPrio
        self.blackandwhite = blackandwhite
        super().__init__(simu, stop)
        self.colors = [self.preferredTaskColor()]
        if self.simu.m > 1:
            self.colors += [self.randomColor() for j in range(self.simu.m - 1)]
        self.instantWidth = 10
        self.widthMargin = 20
        self.taskHeight = 20
        self.heightMargin = 30
        self.width = (stop + 1) * self.instantWidth + 2 * self.widthMargin
        self.height = len(simu.system.tasks) * self.taskHeight + 2 * self.heightMargin

        self.custom_init()

        self.drawRectangle(0, 0, self.width, self.height, self.white(), self.white())
        self.drawGrid(stop)
        self.drawArrivalsAndDeadlines()

    def custom_init(self):
        """Used to initialize custom drawing libraries and such"""
        raise NotImplementedError("PictureDrawer: attempted to call abstract method")

    def randomColor(self):
        """return a random color that can be used by methdos"""
        raise NotImplementedError("PictureDrawer: attempted to call abstract method")

    def black(self):
        """return a representation of the color black that can be used by methods"""
        raise NotImplementedError("PictureDrawer: attempted to call abstract method")

    def white(self):
        """return a representation of the color black that can be used by methods"""
        raise NotImplementedError("PictureDrawer: attempted to call abstract method")

    def preferredTaskColor(self):
        """return the preferred color for tasks in a format usable by methods"""
        raise NotImplementedError("PictureDrawer: attempted to call abstract method")

    def gray(self):
        """return a representation of the color gray that can be used by methods"""
        raise NotImplementedError("PictureDrawer: attempted to call abstract method")

    def red(self):
        """return a representation of the color red that can be used by methods"""
        raise NotImplementedError("PictureDrawer: attempted to call abstract method")

    def blue(self):
        """return a representation of the color blue that can be used by methods"""
        raise NotImplementedError("PictureDrawer: attempted to call abstract method")

    def drawLine(self, x1, y1, x2, y2, width, color):
        """draw a line between (x1, y1) and (x2, y2) on the final picture"""
        raise NotImplementedError("PictureDrawer: attempted to call abstract method")

    def drawRectangle(self, x1, y1, x2, y2, fillColor, outlineColor):
        """draw a rectangle parallel to the axes whose top-left corner is (x1, y1) and bottom-right corner is (x2, y2)"""
        raise NotImplementedError("PictureDrawer: attempted to call abstract method")

    def drawCircle(self, xC, yC, rad, color):
        """draw a circle centered at (xC, yC) of radius rad"""
        raise NotImplementedError("PictureDrawer: attempted to call abstract method")

    def drawText(self, xT, yT, text, size, color):
        """Print text at coordinate (xT, yT)"""
        raise NotImplementedError("PictureDrawer: attempted to call abstract method")

    def outputName(self):
        """Returns the name of the default output file"""
        raise NotImplementedError("PictureDrawer: attempted to call abstract method")

    def getTaskNbr(self, task):
        taskNbr = None
        for i, eachTask in enumerate(self.simu.system.tasks):
            if eachTask is task:
                taskNbr = i
                break
        return taskNbr

    def drawArrow(self, x, y1, y2, color):
        r = 1.5
        direction = (y2 - y1) / math.fabs(y2 - y1)
        self.drawLine(x , y1 + r * direction, x, y2 - r * direction, width=1, color=color)
        self.drawCircle(x, y2 - r * direction, r, color)

    def drawGrid(self, stop):
        self.drawLine(self.widthMargin, self.height - self.heightMargin, self.widthMargin + self.instantWidth * (stop + 1), self.height - self.heightMargin, width=1, color=self.black())
        # - horizontal lines to separate tasks
        for i, task in enumerate(self.simu.system.tasks):
            self.drawLine(
                self.widthMargin,
                self.height - self.heightMargin - (i + 1) * self.taskHeight,
                self.widthMargin + self.instantWidth * (stop + 1),
                self.height - self.heightMargin - (i + 1) * self.taskHeight,
                width=1,
                color=self.black())
        # - vertical lines to separate instants
        for i in range(stop + 1):
            x = self.widthMargin + i * self.instantWidth
            y = self.height - self.heightMargin
            self.drawLine(x, self.heightMargin, x, y, width=1, color=self.gray())
            # timeline markers
            if i % 5 == 0:
                self.drawLine(x, y, x, y + 10, width=1, color=self.black())
                self.drawText(x + 3, y + 3, str(i), size=10, color=self.black())
        # special timeline markers - Omax + k H
        H = self.simu.system.hyperPeriod()
        y = self.height - self.heightMargin
        if self.showLabels:
            specialDict = {
                'Omax': self.simu.system.omax(),
                'fpdit': algorithms.findFirstDIT(self.simu.system)
            }
            for specialName, specialTime in specialDict.items():
                i = 0
                while specialTime and specialTime + i * H < stop:
                    x = self.widthMargin + (specialTime + i * H) * self.instantWidth
                    self.drawLine(x, y, x, y + 23, width=1, color=self.black())
                    textString = specialName
                    if i > 0:
                        textString += " + " + str(i) + " H"
                    self.drawText(x + 3, y + 15, textString, size=10, color=self.black())
                    i += 1

    def drawDeadlineMiss(self, t, task):
        taskNbr = self.getTaskNbr(task)
        x = self.widthMargin + t * self.instantWidth
        y1 = self.height - self.heightMargin - (taskNbr + 1) * self.taskHeight
        y2 = self.height - self.heightMargin - taskNbr * self.taskHeight
        color = self.black() if self.blackandwhite else self.red()
        self.drawCircle(x, (y2 + y1) // 2, 5, color)

    def drawOneExecutionUnit(self, taskNbr, CPUnbr, t, prio, preemp):
        color = self.colors[CPUnbr]
        if preemp:
            color = self.greyColor(color)

        x1 = self.widthMargin + t * self.instantWidth
        y1 = self.height - self.heightMargin - (taskNbr + 1) * self.taskHeight
        x2 = self.widthMargin + (t + 1) * self.instantWidth
        y2 = self.height - self.heightMargin - taskNbr * self.taskHeight
        self.drawRectangle(x1, y1, x2, y2, outlineColor=self.black(), fillColor=color)

        if self.showPrio:
            self.drawText(x1, y2 - (y2 - y1)/2, str(round(prio, 2)), size=5, color=self.black())

    def drawAbort(self, task, t):
        taskNbr = self.getTaskNbr(task)
        assert taskNbr is not None, "drawAbort: task " + str(task) + " was not found in " + str(self.simu.system)
        x1 = self.widthMargin + t * self.instantWidth
        y1 = self.height - self.heightMargin - taskNbr * self.taskHeight - self.taskHeight // 2
        r = 3
        self.outDraw.ellipse([x1 - r, y1 - r, x1 + r, y1 + r], outline="black", fill="red")

    def drawInstant(self, t):
        for cpuNbr, cpu in enumerate(self.simu.CPUs):
            if cpu.job:
                taskNbr = self.getTaskNbr(cpu.job.task)
                prio = cpu.job.priority
                if cpu in self.simu.preemptedCPUs:
                    self.drawOneExecutionUnit(taskNbr, cpuNbr, t, prio, preemp=True)
                else:
                    self.drawOneExecutionUnit(taskNbr, cpuNbr, t, prio, preemp=False)

    def terminate(self):
        # self.drawGrid(self.stop)
        self.drawArrivalsAndDeadlines()

    def drawArrivalsAndDeadlines(self):
        for taskNbr, task in enumerate(self.simu.system.tasks):
            for t in range(task.O, self.simu.stop + 1, task.T):
                x1 = self.widthMargin + t * self.instantWidth
                y1 = self.height - self.heightMargin - taskNbr * self.taskHeight
                # arrivals
                arrivalColor = self.black() if self.blackandwhite else self.blue()
                self.drawArrow(x1, y1 - (self.taskHeight // 2), y1 - self.taskHeight, arrivalColor)
                # deadlines
                t += task.D
                x2 = self.widthMargin + t * self.instantWidth
                deadlineColor = self.black() if self.blackandwhite else self.red()
                self. drawArrow(x2, y1 - (self.taskHeight) // 2, y1, deadlineColor)

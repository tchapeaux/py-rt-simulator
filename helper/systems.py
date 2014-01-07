import random
from model import Task
from model import TaskGenerator


def generateSystemArray(numberOfSystems, constrDeadlineFactor, synchronous=False, n=4, preemptionCost=2, verbose=False):
    systemArray = []
    for i in range(numberOfSystems):
        Umin = 0.55
        Umax = 0.95
        Utot = 1.0*random.randint(int(Umin*100), int(Umax*100))/100
        maxHyperT = 360  # PPCM(2, 3, 5, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 22, 24, 25, 28, 30, 32)
        # maxHyperT = -1
        Tmin = 3
        Tmax = 50
        tasks = TaskGenerator.generateTasks(Utot, n, maxHyperT, Tmin, Tmax, preemptionCost=preemptionCost, synchronous=synchronous, constrDeadlineFactor=constrDeadlineFactor)
        if (verbose and numberOfSystems <= 10):
            print(("Generated task system # ", i))
            for task in tasks:
                    print(("\t", task))
        systemArray.append(Task.TaskSystem(tasks))
    return systemArray


# SmallExample
tasks = []
tasks.append(Task.Task(0, 3, 5, 5, alpha=1))
tasks.append(Task.Task(1, 2, 6, 10, alpha=1))
SmallExample = Task.TaskSystem(tasks)


# exemple from Patrick Meumeu's thesis pp. 128 (Fig. 4.13)
tasks = []
tasks.append(Task.Task(0, 3, 7, 15, alpha=1))
tasks.append(Task.Task(5, 2, 6, 6, alpha=1))
tasks.append(Task.Task(3, 4, 10, 10, alpha=1))
Meumeu = Task.TaskSystem(tasks)

# exemple from Wong/Burns paper (Improved Priority Assignment for the Abort-and-Restart (AR) Model)
tasks = []
tasks.append(Task.Task(0, 6, 60, 60))
tasks.append(Task.Task(0, 4, 32, 32))
tasks.append(Task.Task(0, 3, 25, 25))
tasks.append(Task.Task(0, 5, 50, 50))
tasks.append(Task.Task(0, 2, 100, 100))
WongBurns = Task.TaskSystem(tasks)

# exemple of non-optimality of EDF with preemptions
tasks = []
tasks.append(Task.Task(0, 3, 6, 6, alpha=2))
tasks.append(Task.Task(1, 2, 4, 4, alpha=2))
EDFNonOptimal = Task.TaskSystem(tasks)

# Anomaly: removing Task (0,1,2,4) renders the system unfeasible!
# This is also an example of necessary idle time and non-optimality of EDF/SpotlightEDF
tasks = []
tasks.append(Task.Task(0, 2, 4, 4, alpha=2))
#tasks.append(Task.Task(0, 1, 2, 4, alpha=2))
tasks.append(Task.Task(1, 1, 1, 4, alpha=2))
Anomaly1 = Task.TaskSystem(tasks)

# # Example of non-optimality of SpotlightEDF
# TODO: replace this system by another with same property but which does not require idling
tasks = []
tasks.append(Task.Task(0, 3, 6, 7, alpha=2))
tasks.append(Task.Task(0, 2, 7, 7, alpha=2))
tasks.append(Task.Task(2, 1, 1, 7, alpha=2))
SpotlightEDFNonOptimal = Task.TaskSystem(tasks)

# # PreemptNoIdle
tasks = []
tasks.append(Task.Task(0, 6, 9, 11, alpha=1))
tasks.append(Task.Task(0, 2, 11, 11, alpha=1))
tasks.append(Task.Task(3, 2, 2, 11, alpha=1))
PreemptNoIdle = Task.TaskSystem(tasks)

# # Must Idle
tasks = []
tasks.append(Task.Task(0, 3, 8, 8, alpha=2))
tasks.append(Task.Task(0, 3, 5, 8, alpha=2))
tasks.append(Task.Task(1, 1, 1, 8, alpha=2))
MustIdle = Task.TaskSystem(tasks)

# UnfeasibleLongTransitive
tasks = []
tasks.append(Task.Task(0, 7, 11, 11))
tasks.append(Task.Task(4, 1, 1, 11))
tasks.append(Task.Task(6, 4, 11, 11))
UnfeasibleLongTransitive = Task.TaskSystem(tasks)

# EDFFailTransitiveNotPeriodic
tasks = []
tasks.append(Task.Task(0, 5, 11, 11, alpha=3))
tasks.append(Task.Task(4, 1, 1, 11))
tasks.append(Task.Task(6, 4, 11, 11))
EDFFailTransitiveNotPeriodic = Task.TaskSystem(tasks)

# DPOnly
tasks = []
tasks.append(Task.Task(0, 4, 8, 8, alpha=1))
tasks.append(Task.Task(0, 1, 5, 8, alpha=1))
tasks.append(Task.Task(3, 1, 1, 8, alpha=1))
tasks.append(Task.Task(5, 1, 1, 8, alpha=1))
DPOnly = Task.TaskSystem(tasks)

# KeepForLater
tasks = []
tasks.append(Task.Task(0, 4, 9, 9, alpha=2))
tasks.append(Task.Task(0, 1, 5, 9, alpha=2))
tasks.append(Task.Task(3, 1, 1, 9, alpha=2))
tasks.append(Task.Task(5, 1, 1, 9, alpha=2))
KeepForLater = Task.TaskSystem(tasks)

# Meat Grinder (unfeasible for preemptTime > 0 although U = ~0.5)
tasks = []
tasks.append(Task.Task(0, 2, 100, 100, alpha=1))
tasks.append(Task.Task(1, 1, 1, 2, alpha=1))
MeatGrinder = Task.TaskSystem(tasks)

# LongTransitive
tasks = []
tasks.append(Task.Task(0, 45, 150, 150, alpha=23))
tasks.append(Task.Task(20, 10, 50, 50, alpha=23))
tasks.append(Task.Task(20, 10, 50, 50, alpha=23))
LongTransitive = Task.TaskSystem(tasks)
tasks = []
tasks.append(Task.Task(0, 5, 10, 10, alpha=1))
tasks.append(Task.Task(4, 1, 1, 10, alpha=1))
tasks.append(Task.Task(6, 4, 10, 10, alpha=1))
LongTransitive2 = Task.TaskSystem(tasks)

# FailByTransitive
tasks = []
tasks.append(Task.Task(0, 3, 5, 5, alpha=2))
tasks.append(Task.Task(0, 1, 1, 5))
FailByTransitive = Task.TaskSystem(tasks)


# SamePriorityTrap
tasks = []
tasks.append(Task.Task(1, 1, 1, 10, alpha=2))
tasks.append(Task.Task(0, 2, 4, 10, alpha=2))
tasks.append(Task.Task(4, 3, 6, 10, alpha=2))
tasks.append(Task.Task(6, 1, 2, 10, alpha=2))
SamePriorityTrap = Task.TaskSystem(tasks)
#############################################
tasks = []
#tasks.append(Task.Task(0, 1, 8, 15, alpha=2))
tasks.append(Task.Task(0, 1, 2, 8, alpha=2))
#tasks.append(Task.Task(20, 1, 35, 36, alpha=2))
tasks.append(Task.Task(0, 4, 7, 45, alpha=2))
SamePriorityTrap2 = Task.TaskSystem(tasks)
#############################################
tasks = []
tasks.append(Task.Task(0, 3, 7, 7, alpha=2))
tasks.append(Task.Task(1, 2, 4, 7, alpha=2))
tasks.append(Task.Task(5, 2, 2, 7, alpha=2))
SamePriorityTrap3 = Task.TaskSystem(tasks)

# CKEDFNonOptimal
tasks = []
tasks.append(Task.Task(0, 3, 9, 9, alpha=2))
tasks.append(Task.Task(2, 2, 4, 9, alpha=2))
tasks.append(Task.Task(3, 1, 1, 9, alpha=2))
tasks.append(Task.Task(7, 1, 1, 9, alpha=2))
CKEDFNonOptimal = Task.TaskSystem(tasks)

# AtomicPreemptionCost
tasks = []
tasks.append(Task.Task(0, 5, 11, 11, alpha=2))
tasks.append(Task.Task(4, 1, 1, 11, alpha=2))
tasks.append(Task.Task(6, 1, 2, 11, alpha=2))
AtomicPreemptionCost = Task.TaskSystem(tasks)


# HardPreemptionChoice
tasks = []
tasks.append(Task.Task(0, 4, 12, 12, alpha=1))
tasks.append(Task.Task(3, 5, 6, 12, alpha=1))
tasks.append(Task.Task(8, 1, 1, 12, alpha=1))
HardPreemptionChoice = Task.TaskSystem(tasks)
##############################################
tasks = []
tasks.append(Task.Task(0, 4, 12, 12, alpha=1))
tasks.append(Task.Task(3, 5, 6, 12, alpha=1))
tasks.append(Task.Task(8, 1, 2, 12, alpha=1))
HardPreemptionChoice2 = Task.TaskSystem(tasks)
##############################################
tasks = []
tasks.append(Task.Task(0, 3, 10, 10, alpha=1))
tasks.append(Task.Task(1, 3, 6, 10, alpha=1))
tasks.append(Task.Task(1, 3, 6, 10, alpha=1))
HardPreemptionChoice3 = Task.TaskSystem(tasks)
##############################################
tasks = []
tasks.append(Task.Task(14, 4, 4, 18, alpha=2))
tasks.append(Task.Task(0, 4, 18, 18, alpha=2))
tasks.append(Task.Task(1, 4, 13, 18, alpha=2))
tasks.append(Task.Task(2, 3, 8, 18, alpha=2))
tasks.append(Task.Task(3, 2, 4, 18, alpha=2))
tasks.append(Task.Task(4, 1, 1, 18, alpha=2))
CloudAtlas = Task.TaskSystem(tasks)

# EDFNonOptimalMultiprocessor
tasks = []
tasks.append(Task.Task(0, 5, 7, 13))
tasks.append(Task.Task(0, 3, 7, 13))
tasks.append(Task.Task(0, 9, 11, 13))
EDFNonOptimalMultiprocessor = Task.TaskSystem(tasks)


# RequireClairvoyance
tasks = []
t1 = Task.Task(22, 2, 2, 24, alpha=1)
t2 = Task.Task(0, 5, 12, 12, alpha=1)
t3 = Task.Task(4, 5, 6, 12, alpha=1)
t4 = Task.Task(9, 1, 1, 24, alpha=1)
tasks.extend([t1, t2, t3, t4])
RequireClairvoyance = Task.TaskSystem(tasks)
clairvoyanceSchedule = [t2, t2, t2, t2, t3, t3, t3, t3, t3, t4, t2, t2, t2, t2, t2, t2, t2, t3, t3, t3, t3, t3, t1, t1]


# ULessThanOneImplicitUnfeasible
tasks = []
tasks.append(Task.Task(0, 7, 10, 10, alpha=1))
tasks.append(Task.Task(0, 1, 4, 4, alpha=1))
ULessThanOneImplicitUnfeasible = Task.TaskSystem(tasks)

# MustPreemptAtNoArrival
tasks = []
t1 = Task.Task(0, 3, 6, 6, alpha=1)
t2 = Task.Task(3, 1, 1, 6, alpha=1)
t3 = Task.Task(1, 1, 3, 6, alpha=1)
tasks.append(t1)
tasks.append(t2)
tasks.append(t3)
MustPreemptAtNoArrival = Task.TaskSystem(tasks)
mpanaSchedule = []
mpanaSchedule.append(t1)
mpanaSchedule.append(t1)
mpanaSchedule.append(t3)
mpanaSchedule.append(t2)
mpanaSchedule.append(t1)
mpanaSchedule.append(t1)

# ImpCumulLaxity
tasks = []
tasks.append(Task.Task(0, 1, 12, 12, alpha=2))
tasks.append(Task.Task(2, 3, 20, 20, alpha=2))
tasks.append(Task.Task(0, 26, 45, 45, alpha=2))
ImpCumulLaxity = Task.TaskSystem(tasks)

# ImpFTPNonOptimal
tasks = []
tasks.append(Task.Task(0, 1, 3, 3, alpha=1))
tasks.append(Task.Task(0, 5, 9, 9, alpha=1))
ImpFTPNonOptimal = Task.TaskSystem(tasks)

# DifferentPreemptionCost_PTFNonOptimal
tasks = []
tasks.append(Task.Task(1, 11, 18, 18, alpha=2))
tasks.append(Task.Task(0, 7, 30, 30, alpha=0))
tasks.append(Task.Task(1, 1, 9, 9, alpha=0))
DifferentPreemptionCost_PTFNonOptimal = Task.TaskSystem(tasks)


# ImpPTEFTNonOptimal
tasks = []
tasks.append(Task.Task(0, 9, 45, 45, alpha=2))
tasks.append(Task.Task(0, 1, 6, 6, alpha=2))
tasks.append(Task.Task(0, 6, 12, 12, alpha=2))
ImpPTEFTNonOptimal = Task.TaskSystem(tasks)

# DITPaperExample
tasks = []
tasks.append(Task.Task(8, 0, 7, 15, alpha=0))
tasks.append(Task.Task(0, 0, 2, 5, alpha=0))
DITPaperExample = Task.TaskSystem(tasks)


# test
tasks = []
tasks.append(Task.Task(0, 1, 3, 3, alpha=2))
tasks.append(Task.Task(0, 4, 30, 30, alpha=2))
tasks.append(Task.Task(0, 1, 12, 12, alpha=2))

test = Task.TaskSystem(tasks)

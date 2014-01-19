from model import algorithms
from model import TaskGenerator
from model import Task
from simulator import Simulator
from simulator.scheduler import Scheduler
from simulator.scheduler.recognizeSchedulerName import recognizeSchedulerName
from helper import systems

import subprocess
import sys

# default parameters
tau = systems.PMImpRequireIdle
schedName = "PMImp"

# Read user parameters
helpString = \
    "Usage: python3 mainSimu.py [<paramName> <paramValue>]\n\
    Parameters:\n\
    -sched : Name of the scheduler\n\
    -sys : Name of the system (or 'RAND')\n\
    "
argv = sys.argv[1:]
argc = len(argv)
assert argc % 2 == 0, "Invalid number of arguments\n" + helpString
for i in range(0, argc, 2):
    paramV = argv[i + 1]
    if argv[i] == "-sched":
        schedName = paramV
    elif argv[i] == "-sys":
        if paramV == "RAND":
            tau = Task.TaskSystem(TaskGenerator.generateTasks(
                Utot=0.7, n=20, maxHyperT=33750, Tmin=10, Tmax=50,
                synchronous=True, constrDeadlineFactor=0
                )
            )
        else:
            with open(paramV) as f:
                tau = Task.TaskSystem.fromFile(f)
    else:
        raise AssertionError("Invalid parameters\n" + helpString)
del argv
del argc
del helpString

Omax = max([task.O for task in tau.tasks])
H = tau.hyperPeriod()
fpdit = algorithms.findFirstDIT(tau)

print("Omax", Omax)
print("H", H)
print("fpdit", fpdit)
print("U", tau.systemUtilization())

schedClass = recognizeSchedulerName(schedName)
if schedClass == Scheduler.ExhaustiveFixedPriority:
    scheduler = schedClass(tau, nbrCPUs=1)
else:
    scheduler = schedClass(tau)

try:
    simu = Simulator.getLaunchedSimu(tau, scheduler, verbose=True, drawing=True)
    if simu.success():
        print("Success.")
    else:
        print("Failure.")
except AssertionError:
    print("Something went wrong ! Close the image preview to see the stack trace")
    raise
finally:
    if "linux" in sys.platform:
        subprocess.Popen(['eog', simu.drawer.outputName()])
    elif "win" in sys.platform:
        subprocess.Popen(['rundll32', '"C:\Program Files\Windows Photo Viewer\PhotoViewer.dll"', simu.drawer.outputName()])

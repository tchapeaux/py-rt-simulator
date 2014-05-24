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
# tau = systems.LimitedPreemptionExample
# with open("systems/task_example2.system") as f:
#     tau = Task.TaskSystem.fromFile(f)
tasks = [Task.Task(0, 5, 11, 11, 3), Task.Task(4, 1, 1, 11, 3), Task.Task(6, 4, 11, 11, 3)]
tau = Task.TaskSystem(tasks)
schedName = "EDF"
# stop = tau.omax() + 10 * tau.hyperPeriod()  # None for default value
stop = 45

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

# Short circuit for arbitrary scheduler (use if you know what you're doing)
# schedule = [
#     tau.tasks[2],
#     tau.tasks[1],
#     tau.tasks[1],
#     ]
# scheduler = Scheduler.ArbitraryScheduler(tau, schedule)

try:
    simu = Simulator.getLaunchedSimu(tau, scheduler, stop=stop, verbose=False, drawing=True, stopAtDeadlineMiss=False, stopAtStableConfig=False)
    if simu.success():
        print("Success.")
    else:
        print("Failure.")
except AssertionError:
    print("Something went wrong ! Close the image preview to see the stack trace")
    raise
finally:
    outputName = simu.drawer.outputName()
    if "linux" in sys.platform:
        if ".eps" in outputName:
            subprocess.Popen(['okular', simu.drawer.outputName()])
        else:
            subprocess.Popen(['eog', simu.drawer.outputName()])
    elif "win" in sys.platform:
        subprocess.Popen(['rundll32', '"C:\Program Files\Windows Photo Viewer\PhotoViewer.dll"', simu.drawer.outputName()])

from model import algorithms
from model import TaskGenerator
from model import Task
from simulator import Simulator
from simulator.scheduler import Scheduler, ChooseKeepEDF, PALLF, LBLScheduler
from helper import systems

import subprocess
import sys

# tau = Task.TaskSystem(TaskGenerator.generateTasks(0.7, 3, 33750, 5, 20, synchronous=False, constrDeadlineFactor=0))
tau = systems.test

if len(sys.argv) > 1:
    with open(sys.argv[1]) as f:
        tau = Task.TaskSystem.fromFile(f)


Omax = max([task.O for task in tau.tasks])
H = tau.hyperPeriod()
fpdit = algorithms.findFirstDIT(tau)

print(("Omax", Omax))
print(("H", H))
print(("fpdit", fpdit))
print(("U", tau.systemUtilization()))

stop = Omax + 4 * H
# if fpdit:
#     stop = fpdit + H

print(("stop", stop))

# scheduler = Scheduler.EDF(tau)
scheduler = Scheduler.LLF(tau)
# scheduler = Scheduler.SpotlightEDF(tau)
# scheduler = ChooseKeepEDF.ChooseKeepEDF(tau)
# scheduler = Scheduler.PTEDF(tau)
# scheduler = PALLF.PALLF(tau)
# scheduler = Scheduler.ArbitraryScheduler(tau, systems.mpanaSchedule)
# scheduler = LBLScheduler.LBLEDF(tau)

# scheduler = Scheduler.FixedPriority(tau, [1, 2, 3])
# !!! exhaustive: set the parameters right !!!
# scheduler = Scheduler.ExhaustiveFixedPriority(tau, nbrCPUs=1, abortAndRestart=False)
# if scheduler.foundFeasible:
#   print "found feasible priorities :", scheduler.prioArray
# else:
#   print "No feasible priorities found !"

simu = Simulator.Simulator(tau, stop=stop, nbrCPUs=1, scheduler=scheduler, abortAndRestart=False, verbose=True)

try:
    simu.run(stopAtDeadlineMiss=True, stopAtStableConfig=True)
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
        subprocess.Popen(['rundll32', '"C:\Program Files\Windows Photo Viewer\PhotoViewer.dll"', '"C:\\00012.tif"'])

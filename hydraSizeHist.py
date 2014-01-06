from Model import TaskGenerator
from Model import Task
from Model import cspace

import pickle
# import time
import concurrent.futures
import random


def parallelFunc():
    tasks = TaskGenerator.generateTasks(Utot=random.random(), n=3, maxHyperT=554400, Tmin=5, Tmax=20, synchronous=False, constrDeadlineFactor=random.random())
    tau = Task.TaskSystem(tasks)
    res = None

    tSync = tau.firstSynchronousInstant()
    if not tSync:
        asyncCSpace = cspace.Cspace(tau)
        asyncCSpaceSize = asyncCSpace.size(tau)
        if asyncCSpaceSize > 0:
            syncTau = tau.synchronousEquivalent()
            syncCSpaceSize = syncTau.cSpaceSize()
            res = syncCSpaceSize/asyncCSpaceSize
    return res

if __name__ == "__main__":
    nSystems = 50000

    print("Starting size ratio histogram for "+str(nSystems)+" systems")

    executor = concurrent.futures.ProcessPoolExecutor()
    parallelArgs = list(range(nSystems))
    futuresList = [executor.submit(parallelFunc) for n in range(nSystems)]

    results = [f.result() for f in futuresList]
    results = [r for r in results if r is not None]
    paramInfo = (nSystems)

    with open("results", "wb") as output:
        pickle.dump((paramInfo, results), output, pickle.HIGHEST_PROTOCOL)

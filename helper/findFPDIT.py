from helper import myAlgebra

import math
import heapq
import array
import copy

def isGoodResult(res, intervals, tasks):
    for t in tasks:
        foundGoodA = False
        for aValue in intervals[t]:
            if res % t.T == aValue % t.T:
                foundGoodA = True
                break
        if not foundGoodA:
            return False
    return True

class TaskCongruenceSystem(object):
	def __init__(self,xList,pList):
		self.xList = xList
		self.pList = pList

def findFPDIT(tau):
    # Requires to solve several system of modular equations

    # Construction of the intervals
    intervals = {task: list(range(task.D, task.T)) for task in tau.tasks}
    for task in tau.tasks:
        # 0, corresponding to the last/first case is missing from each interval
        intervals[task].append(0)
        # add Oi for the asynchronous case
        # This should have no effect in the synchronous case
        for j in range(len(intervals[task])):
            intervals[task][j] += task.O
            intervals[task][j] %= task.T

    T = [task.T for task in tau.tasks]
    Omax = max([task.O for task in tau.tasks])
    congruenceDict = {}
    primeDict = {}

    for task in tau.tasks:
        pFactors = myAlgebra.primeFactors(task.T)
        primalPowers = [pow(t,pFactors.count(t)) for t in set(pFactors)]
        congruenceDict[task] = TaskCongruenceSystem(intervals[task],primalPowers)
#         newPrimalPowers = copy.copy(primalPowers)
#         for pTuple in zip(set(pFactors),primalPowers):
#             prime = pTuple[0]
#             primalPower = pTuple[1]
#             if prime in primeDict.keys():
#                 for taskpp in primeDict[prime]:
#                     task2 = taskpp[0]
#                     pp2 = taskpp[1]
#                     if primalPower > pp2:
#                         l = congruenceDict[task2].pList
#                         if pp2 in l:
#                             l.remove(pp2)
#                         if primalPower not in l:
#                             l.append(primalPower)
#                         taskpp[1] = primalPower
#                     elif primalPower < pp2:
#                         if primalPower in newPrimalPowers:
#                             newPrimalPowers.remove(primalPower)
#                         if pp2 not in newPrimalPowers:
#                             newPrimalPowers.append(pp2)
#                 primeDict[prime].append([task,primalPower])
#             else:
#                 primeDict[prime] = [[task,primalPower]]
#         congruenceDict[task].pList = newPrimalPowers
    tgsList = congruenceDict.values()
    ppSet = set()
    for t in tgsList:
        ppSet.update(t.pList)

    for pp in ppSet:
        for task in tau.tasks:
            taskPList = congruenceDict[task].pList
            newTaskPList = []
            for taskp in taskPList:
                if pp > taskp and pp % taskp == 0:
                    newTaskPList.append(pp)
                else:
                    newTaskPList.append(taskp)
            congruenceDict[task].pList = newTaskPList

    allResults = multiCRP(congruenceDict)

    if not allResults:
        return None

    idles = list(zip(allResults, [False for i in range(len(allResults))]))
    heapq.heapify(idles)
    idleTuple = heapq.heappop(idles)
    tIdle = idleTuple[0]

    while(not isGoodResult(tIdle, intervals, tau.tasks)):
        if not idles:
            return None
        idleTuple = heapq.heappop(idles)
        tIdle = idleTuple[0]

    while(tIdle <= Omax):
        heapq.heappush(idles, (tIdle+tau.hyperPeriod(), True))
        idleTuple = heapq.heappop(idles)
        tIdle = idleTuple[0]
        alreadyTested = idleTuple[1]
        while(not alreadyTested and not isGoodResult(tIdle, intervals, tau.tasks)):
            if not idles:
                return None
            idleTuple = heapq.heappop(idles)
            tIdle = idleTuple[0]
            alreadyTested = idleTuple[1]

    return tIdle


def multiCRP(congruenceDict):
    tgsList = congruenceDict.values()
    ppSet = set()
    for t in tgsList:
        ppSet.update(t.pList)
    H = myAlgebra.lcmArray(list(ppSet))

#   calculate all terms of the sums
    sumChunks = {}
    for t in tgsList:
        tgsSumList = array.array('i', [0])*len(t.xList)
        for cnt,x in enumerate(t.xList):
            tgsSum = 0
            for p in t.pList:
                Mi = H // p
                invMi = myAlgebra.modinv(Mi, p)
                tgsSum += (x * Mi * invMi) % H
            tgsSumList[cnt] = tgsSum
        sumChunks[t] = tgsSumList

#   calculate the sums from the precomputed terms
    results = [0]
    for t in tgsList:
        newResults = array.array('i', [0])*(len(t.xList)*len(results))
        index = 0
        for cnt,x in enumerate(t.xList):
            for r in results:
                newResults[index] = (r + sumChunks[t][cnt]) % H
                index += 1
        results = newResults

    return [r % H for r in results]


if __name__ == '__main__':
    pass

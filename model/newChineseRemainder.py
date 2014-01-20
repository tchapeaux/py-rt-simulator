from helper import myAlgebra
# from model import Task
# from model import TaskGenerator

import math
import heapq
import array


def newChineseRemainder(a, n):
    '''
    a is a list of lists, each sublist containing all possible a_i for the same n
    n is a list of the n_i values
    '''
    H = myAlgebra.lcmArray(n)

#   calculate all terms of the sums
    sumChunks = []
    for i in range(len(n)):
        sumChunks.append(array.array('i', [0])*len(a[i]))
        Mi = H // n[i]
        invMi = myAlgebra.modinv(Mi, n[i])
        for cnt, aValue in enumerate(a[i]):
            sumChunks[i][cnt] = (aValue * Mi * invMi) % H

#   calculate the sums from the precomputed terms
    results = [0]
    for i in range(len(n)):
        newResults = array.array('i', [0])*(len(a[i])*len(results))
        index = 0
        for j in range(len(a[i])):
            for r in results:
                newResults[index] = (r + sumChunks[i][j]) % H
                index += 1
        results = newResults

    return [r % H for r in results]


#not used anymore
def removeBadChineseRemainderResults(results, a, n):
    badResults = []
    for r in results:
        for cnt, i in enumerate(n):
            if len([_f for _f in [r % i == aValue for aValue in a[cnt]] if _f]) == 0:
                badResults.append(r)
                break

    for badR in badResults:
        results.remove(badR)

    return results


def isGoodResult(res, a, n):
    for cnt, i in enumerate(n):
        foundGoodA = False
        for aValue in a[cnt]:
            if res % i == aValue:
                foundGoodA = True
                break
        if not foundGoodA:
            return False
    return True


def newCongruencePrimalPower(primalSystem, aList):
    # Source : http://math.stackexchange.com/questions/120070/chinese-remainder-theorem-with-non-pairwise-coprime-moduli

    # Return a value x such that
    # x = a1 (mod p1^b1)
    # x = a2 (mod p2^b2)
    # ...
    # x = ak (mod pk^bk)
    # Returns None if no such x exists

    # Check that the values of aList are coherent in the primalSystem
    # and replace them by their value modulo p^b
    ps = {}
    for p in primalSystem:
        ps[p] = {}
        for b in primalSystem[p]:
            ps[p][b] = None
            for cnt, indice in enumerate(primalSystem[p][b]):
                if cnt == 0:
                    prime = int(math.pow(p, b))
                    aSet = set()
                    aSet.update([a % prime for a in aList[indice]])
                else:
                    aSet.intersection_update([a % prime for a in aList[indice]])
                    if not aSet:  # no a values in common
                        return None  # Impossible system
                ps[p][b] = list(aSet)

    # Group system into subsystems of the same p and solve them separately
    subX = {}
    maxB = {}
    for p in list(ps.keys()):
        maxB[p] = max(ps[p].keys())
        maxA = ps[p][maxB[p]]
        subX[p] = maxA

        # Check that all values are consistent modulo p^b
        # For that we check that ai = aj mod p^(b_min(i,j)) for all pairs
        # if the equations are coherent, we can only keep the one of biggest b

    # 3) Now we have a system respecting the condition of the CRT:
    # x = subX1 mod p1^maxB1
    # ...
    # x = subXk mod pk^maxBk

    # Create lists to use as parameters of our CRT function
    subXList = []
    pbArray = array.array('i', [0])*len(list(ps.keys()))
    for cnt, p in enumerate(ps.keys()):
        subXList.append(subX[p])
        pbArray[cnt] = int(math.pow(p, maxB[p]))

    return newChineseRemainder(subXList, pbArray)


def newFindFirstPeriodicDIT(tau):
    # Requires to solve several system of modular equations

    # Construction of the intervals
    intervals = [list(range(task.D, task.T)) for task in tau.tasks]
    for i, task in enumerate(tau.tasks):
        # 0, corresponding to the last/first case is missing from each interval
        intervals[i].append(0)
        # add Oi for the asynchronous case
        # This should have no effect in the synchronous case
        for j in range(len(intervals[i])):
            intervals[i][j] += task.O
            intervals[i][j] %= task.T

    T = [task.T for task in tau.tasks]
    Omax = max([task.O for task in tau.tasks])

    # Pre-processing for our congruence algorithm
    primalSystem_T = myAlgebra.toPrimalPowerSystem(T)
    allResults = newCongruencePrimalPower(primalSystem_T, intervals)

    if not allResults:
        return None

    idles = list(zip(allResults, [False for i in range(len(allResults))]))
    heapq.heapify(idles)
    idleTuple = heapq.heappop(idles)
    tIdle = idleTuple[0]

    while(not isGoodResult(tIdle, intervals, T)):
        if not idles:
            return None
        idleTuple = heapq.heappop(idles)
        tIdle = idleTuple[0]

    while(tIdle <= Omax):
        heapq.heappush(idles, (tIdle+tau.hyperPeriod(), True))
        idleTuple = heapq.heappop(idles)
        tIdle = idleTuple[0]
        alreadyTested = idleTuple[1]
        while(not alreadyTested and not isGoodResult(tIdle, intervals, T)):
            if not idles:
                return None
            idleTuple = heapq.heappop(idles)
            tIdle = idleTuple[0]
            alreadyTested = idleTuple[1]

    return tIdle


def newCRLoop(systems):
    l = list()
    for s in systems:
        l.append(newFindFirstPeriodicDIT(s))
    return l


# def oldCRLoop(systems):
#     l = list()
#     for s in systems:
#         l.append(algorithms.findFirstPeriodicDIT(s))
#     return l

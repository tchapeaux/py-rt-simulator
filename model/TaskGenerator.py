import math
import random
from model import Task
from functools import reduce


def UUniSort(n, Utot):
    # return a vector of n values of utilizations s.t. their sum is Utot
    # "Measuring the performance of schedulability tests", E. Bini, GC Buttazzo

    # 1) generate n-1 uniform values in the interval [0, Utot]
    v = [(random.randrange(1, int(Utot*1000), 1)*1.0)/1000 for i in range(n-1)]
    # 2) Add 0 and Utot to the vector
    v.append(0)
    v.append(Utot)
    # 3) Return the difference between adjacent values
    v = sorted(v)
    return [round(v[i + 1] - v[i], 3) for i in range(n)]


def UUniFast(n, Utot):
#   Does the same thing as UUniSort, but better faster stronger
    utils = []
    curU = Utot
    for i in range(1, n):
        nextU = curU * math.pow(random.random(), (1.0 / (n - i)))
        utils.append(curU - nextU)
        curU = nextU
    utils.append(curU)
    return [round(u, 4) for u in utils]


def generateTasks(Utot, n, maxHyperT, Tmin, Tmax, preemptionCost=0, synchronous=True, constrDeadlineFactor=1):
    # Utot will be delivered in a "best effort" way
    # constrDeadlineFactor: D will be in the interval [T-(T-C)/constrDeadlineFactor, T]

    assert 0 < Utot <= 1, "Utot out of bounds " + str(Utot)
    utilizations = UUniFast(n, Utot)
    assert sum(utilizations) - Utot <= 0.001, str(sum(utilizations)) + ", \t" + str(Utot)
    tasks = generateTasksFrom(utilizations, maxHyperT, Tmin, Tmax, preemptionCost, synchronous, constrDeadlineFactor)
    return tasks


def generateTasksFrom(utilizations, T_LCM, Tmin, Tmax, preemptionCost, synchronous, constrDeadlineFactor):
    # Set T_LCM to -1 to deactivate the limitation of hyperperiod

    assert T_LCM == -1 or T_LCM > 0, "The value of T_LCM does not make sense: " + str(T_LCM)

    if T_LCM > -1:
        # find divisors of T_LCM
        divisors = []
        for i in range(Tmin, Tmax):
            if T_LCM % i == 0:
                divisors.append(i)

    tasks = []
    for u in utilizations:
        O = 0 if synchronous else max(0, int(random.normalvariate(Tmin, (Tmax-Tmin)/2)))
        T = random.randrange(Tmin, Tmax) if T_LCM == -1 else random.choice(divisors)
        C = max(1, int(round(math.floor(u * T))))
        D = random.randint(int(T - (T - C) * constrDeadlineFactor), T)
        a = preemptionCost if preemptionCost >= 0 else random.randrange(0, 5)
        tasks.append(Task.Task(O, C, D, T, a))

    # translate offset so that Omin=0
    Omin = min([task.O for task in tasks])
    for task in tasks:
        task.O -= Omin
    return tasks


if __name__ == '__main__':
    Utot = 0.95
    n = 5
    maxHyperT = 554400  # PPCM(2, 3, 5, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 22, 24, 25, 28, 30, 32)
    Tmin = 50
    Tmax = 1000

    tasks = generateTasks(Utot, n, maxHyperT, Tmin, Tmax, synchronous=True)
    for task in tasks:
            print(task)

    print("UUniSort", UUniSort(5, 1.0))
    print("UUniFast", UUniFast(5, 1.0))

    # check that the function does not generate values of Ci equals to 0
    # and that the total utilization is relatively close to the desired one
    for i in range(1000):
        Utot = 0.5 + random.random()/2
        n = random.randint(1, 10)
        maxHyperT = -1
        Tmin = random.randint(2, 50)
        Tmax = random.randint(Tmin + 1, 100)
        tasks = generateTasks(Utot, n, maxHyperT, Tmin, Tmax, synchronous=False)
        """
        print "\n=========="
        print "Utot", Utot
        print "n", n
        print "Tmin", Tmin
        print "Tmax", Tmax
        print "tasks", tasks
        if not (-0.1 <= Utot - reduce(lambda x, y: x + y.utilization(), tasks, 0) <= 0.1):
            print "Error: ", Utot - reduce(lambda x, y: x + y.utilization(), tasks, 0), "Tmin", Tmin
        """
        for task in tasks:
            assert task.C > 0, str(task)


# ####################################

# def oldGenerateTasks(Umax, Umin, u_max, u_min, maxHyperT, Tmin, Tmax, lowPPCM=True, synchronous=True, Kmax=1, Rmax=1):

#     # assertions
#     assert 0 < Umin <= Umax <= 1, "Umin or Umax out of bound " + str(Umin) + "|" + str(Umax)
#     assert 0 < u_min <= u_max <= 1, "u_min or u_max out of bound" + str(Umin) + "|" + str(Umax)
#     assert (u_min*Tmin*1.0)/math.pow(Rmax, Kmax) > 1, "Not enough granularity! (u_min, Tmin, Rmax, Kmax)"


#     # generation of the utilizations
#     # generate a list of values between u_min and u_max
#     # s.t. their sum is between Umin and Umax
#     utilizations = []
#     cnt = 0
#     while reduceSum(utilizations) > Umax or reduceSum(utilizations) < Umin:
#         cnt += 1
#         if cnt > 1000:
#             # relax constraints
#             print("did not respect bounds after 1000 steps. Please give more relaxed constraints")
#             utilization_goal_below = Umin
#             utilization_goal_above = Umax
#         elif reduceSum(utilizations) <= Umin:
#             new_utiliz = random.uniform(u_min, u_max)
#             new_utiliz = round(new_utiliz, 2)
#             utilizations.append(new_utiliz)
#         else:  # reduceSum(utilizations) > Umax
#             utilizations.pop(random.randint(0, len(utilizations) - 1))

#     tasks = generateTasksFrom(utilizations, maxHyperT, Tmin, Tmax, Kmax, Rmax)
#     return tasks

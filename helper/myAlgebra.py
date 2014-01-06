import math
from functools import reduce


def nextPeriodic(t, period, offset):
    """
        return the smallest t' > t such that (t' - offset) mod period = 0
    """
    return t + (period - (t - offset) % period)


def egcd_couple(a, b):
    # from https://en.wikibooks.org/wiki/Algorithm_Implementation/Mathematics/Extended_Euclidean_algorithm
    x, y, u, v = 0, 1, 1, 0
    while a != 0:
        q, r = b // a, b % a
        m, n = x - u * q, y - v * q
        b, a, x, y, u, v = a, r, u, v, m, n
    return b, x, y


def egcd(*integers):
    return egcdArray(integers)


def egcdArray(intArray):
    assert len(intArray) > 1
    return reduce(lambda x, y: egcd_couple(x, y)[0], intArray)


def modinv(a, m):
    # from https://en.wikibooks.org/wiki/Algorithm_Implementation/Mathematics/Extended_Euclidean_algorithm
    g, x, y = egcd_couple(a, m)
    if g != 1:
        return None  # modular inverse does not exist
    else:
        return x % m


def lcm_couple(x, y):
    return int(math.fabs(x * y)/egcd_couple(x, y)[0])


def lcm(*integers):
    return lcmArray(integers)


def lcmArray(intArray):
    if len(intArray) == 1:
        return intArray[0]
    else:
        return reduce(lambda x, y: lcm_couple(x, y), intArray)


def chineseRemainderTheorem(aList, nList):
    # http://en.wikipedia.org/wiki/Chinese_remainder_theorem
    # aList is a list() containing the residues
    # nList is a list() containing the moduli (must be pairwise coprime)
    # Return the unique solution

    assert len(aList) == len(nList), "ChineseRemainderTheorem: parameters must be of the same size"
    n = len(aList)

    # check for coprime property
    for i in range(n):
        for j in range(i + 1, n):
            assert egcd(nList[i], nList[j]) == 1, "ChineseRemainderTheorem: some Ns are not coprime:\t" + str(nList[i]) + " , " + str(nList[j])

    H = lcmArray(nList)

    # Compute x value
    chineseSum = 0
    for i in range(n):
        Mi = H / nList[i]
        invMi = modinv(Mi, nList[i])
        chineseSum += aList[i] * Mi * invMi

    # Each values equal modulo H to chineseSum is valid, we return the smallest > 0
    chineseSum %= H

    return chineseSum


def primesBelow(n):
    # Sieve of Eratosthenes
    if n <= 2:
        return []
    sieve = [True] * (n + 1)
    for x in range(3, int(math.sqrt(n)) + 1, 2):
        for y in range(3, (n // x) + 1, 2):
            sieve[(x * y)] = False

    return [2] + [i for i in range(3, n, 2) if sieve[i]]


def primeFactors(n, listOfPrimes=None):
    # return an array containing all prime factors of n, with explicit doubles
    # e.g. primeFactors(48) = (2,2,2,2,3)
    # order is not guaranteed
    # listOfPrimes can be provided to speed up the process
    factors = []
    primes = listOfPrimes
    if primes is None:
        primes = primesBelow(n + 1)
    for p in [x for x in primes if x <= n]:
        while n % p == 0:
            factors.append(p)
            n /= p
    return factors


def congruence(aList, nList):
    # Source : http://math.stackexchange.com/questions/120070/chinese-remainder-theorem-with-non-pairwise-coprime-moduli
    # 1) Transform the system into another equivalent system
    primalSystem = toPrimalPowerSystem(nList)
    # 2) Solve the equivalent system (for details see function code)
    return congruencePrimalPower(primalSystem, aList)


def toPrimalPowerSystem(nList):
    # Source : http://math.stackexchange.com/questions/120070/chinese-remainder-theorem-with-non-pairwise-coprime-moduli
    # Transform a system into another equivalent system of the form
    # x = a1 (mod p1^b1)
    # x = a2 (mod p2^b2)
    # ...
    # x = ak (mod pk^bk)
    # (where p values are prime)

    # Return a dictionary encoding equalities (x = a (mod p^b)) of an equivalent primal system as primalSystem[p][b] = (list of indices of a)
    # Later, the list of values of a must be checked to be consistent
    n = len(nList)
    primalSystem = {}

    # preprocess the primes below max(n)
    nMax = max(nList)
    primes = primesBelow(nMax)

    for i in range(n):
        nFactors = primeFactors(nList[i])
        for p in nFactors:
            if p not in primalSystem:
                primalSystem[p] = {}
            b = nFactors.count(p)
            if b not in primalSystem[p]:
                primalSystem[p][b] = []
            # Add the indices to the list of indices to check
            primalSystem[p][b].append(i)
    return primalSystem


def congruencePrimalPower(primalSystem, aList):
    # Source : http://math.stackexchange.com/questions/120070/chinese-remainder-theorem-with-non-pairwise-coprime-moduli

    # Return a value x such that
    # x = a1 (mod p1^b1)
    # x = a2 (mod p2^b2)
    # ...
    # x = ak (mod pk^bk)
    # Returns None if no such x exists

    # Check that the values of aList for the same p^b are coherent
    # and replace them by their value (modulo p^b)
    ps = {}  # we need a new dictionary to keep the original const
    for p in primalSystem:
        ps[p] = {}
        for b in primalSystem[p]:
            ps[p][b] = None
            for cnt, indice in enumerate(primalSystem[p][b]):
                if cnt == 0:
                    ps[p][b] = aList[indice] % int(math.pow(p, b))
                else:
                    if ps[p][b] != aList[indice] % int(math.pow(p, b)):
                        return None  # Impossible system

    # Group system into subsystems of the same p and solve them separately
    subX = {}
    maxB = {}
    for p in list(ps.keys()):
        # Check that all values are consistent modulo p^b
        # For that we check that ai = aj mod p^(b_min(i,j)) for all pairs
        for bi in ps[p]:  # TODO : verify should we only check for the smallest bi
            for bj in [x for x in primalSystem[p] if x > bi]:
                ai = ps[p][bi]
                aj = ps[p][bj]
                # by construction we know that bi < bj
                if ai % int(math.pow(p, bi)) != aj % int(math.pow(p, bi)):
                    return None
        # if the equations are coherent, we can only keep the one of biggest b
        maxB[p] = max(ps[p].keys())
        subX[p] = ps[p][maxB[p]]

    # 3) Now we have a system respecting the condition of the CRT:
    # x = subX1 mod p1^maxB1
    # ...
    # x = subXk mod pk^maxBk

    # Create lists to use as parameters of our CRT function
    subXList = []
    pbList = []
    for p in list(ps.keys()):
        subXList.append(subX[p])
        pbList.append(int(math.pow(p, maxB[p])))

    return chineseRemainderTheorem(subXList, pbList)

from model import algorithms

import subprocess  # in order to launch GLPSOL
import itertools
import os.path
import re


class Cspace(object):
    def __init__(self, tau, upperLimit='def', lowerLimit=0, fromList=False):
        #    return a system of inequations of the form
        # cst_1 * C_1 + cst_2 * C_2 + ... + cst_n * C_n <= CST
        # encoded as a list
        # [cst_1, cst_2, ..., cst_n, CST]

        if fromList:
            self.constraints = tau
        else:
            Omax = tau.omax()
            isSynchronous = (Omax == 0)

            if upperLimit == "def":
                firstDIT = algorithms.findFirstDIT(tau)
                if isSynchronous:
                    upperLimit = firstDIT
                    lowerLimit = 0
                else:
                    if firstDIT is not None:
                        upperLimit = firstDIT + tau.hyperPeriod()
                        lowerLimit = firstDIT
                    else:
                        upperLimit = Omax + 2 * tau.hyperPeriod()
                        lowerLimit = Omax

            # for each arrival and each deadline, create an equation
            self.constraints = []
            for a, d in tau.dbf_intervals(lowerLimit, upperLimit):
                constraint = CSpaceConstraint([algorithms.completedJobCount(t, a, d) for t in tau.tasks], a, d)
                self.constraints.append(constraint)

    def __getitem__(self, key):
        return self.constraints.__getitem__(key)

    def __setitem__(self, key, val):
        return self.constraints.__getitem__(key, val)

    def __delitem__(self, key):
        return self.constraints.__getitem__(key)

    def __len__(self):
        return self.constraints.__len__()

# def Cspace(tau, upperLimit="def", lowerLimit = 0):
#   # return a system of inequations of the form
#   # cst_1 * C_1 + cst_2 * C_2 + ... + cst_n * C_n <= CST
#   # encoded as a list
#   # [cst_1, cst_2, ..., cst_n, CST]
#
#   Omax = max([task.O for task in tau.tasks])
#   isSynchronous = (Omax == 0)
#
#   if upperLimit == "def":
#       firstDIT = algorithms.findFirstDIT(tau)
#       if isSynchronous:
#           upperLimit = firstDIT
#           lowerLimit = 0
#       else:
#           if firstDIT is not None:
#               upperLimit = firstDIT + tau.hyperPeriod()
#               lowerLimit = firstDIT
#           else:
#               upperLimit = Omax + 2 * tau.hyperPeriod()
#               lowerLimit = Omax
#
#   # for each arrival and each deadline, create an equation
#   constraints = []
#   for a, d in tau.dbf_intervals(lowerLimit, upperLimit):
#       constraints.append([algorithms.completedJobCount(t, a, d) for t in tau.tasks] + [d - a])
#
#   return constraints

    def removeRedundancy(self, firstPass=True, verbose=False):
        # Idea:
        # start with an empty list of cstr,
        # add each cstr only if it is not redundant
        # THEN test every remaining cstr against the others

        # first pass - filter against previous cstr
        newCspace = []
        if firstPass:
            for i, cstr in enumerate(self):
                if not cstr.isRedundant(newCspace):
                    if verbose: print("\tNon-redundant at step ", i, ":", cstr)
                    newCspace.append(cstr)
        else:
            newCspace.extend(self)

        # second pass - filter against all cstr
        # Note that the number of cstr should be small
        i = 0
        while i < len(newCspace):
            cstr = newCspace.pop(i)
            if not cstr.isRedundant(newCspace):
                newCspace.insert(i, cstr)
                i += 1
            elif verbose:
                print("\t", cstr, "was redundant against", newCspace)
        return Cspace(newCspace, fromList=True)

    def numTasks(self):
        return len(self.constraints[0])

    def calculateBoundingBox(self):
        boxLimits = []
        numTasks = self.numTasks()
        for i in range(numTasks):
            cvector = [1]*numTasks
            while(testCVector(self, cvector)):
                cvector[i] += 1
            boxLimits.append(cvector[i])
        return boxLimits

    def size(self, tau=None):
        cValues = []
        if tau:
            for task in tau.tasks:
                cValues.append((c for c in range(1, task.D + 1)))
        else:
            boxLimits = self.calculateBoundingBox()
            for limit in boxLimits:
                cValues.append([c for c in range(1, limit)])
        return len([cvector for cvector in itertools.product(*cValues) if testCVector(self, cvector)])


# def CspaceSize(tau, cspace=None):
#   if cspace is None:
#       cspace = Cspace(tau)
#   cValues = []
#   for task in tau.tasks:
#       cValues.append((c for c in range(1, task.D + 1)))
#   return len(filter(lambda cvector: testCVector(cspace, cvector), itertools.product(*cValues)))


def testCVector(cspace, cvector):
    for i, constraint in enumerate(cspace):
        res = 0
        for j in range(len(cvector)):
            res += constraint[j]*cvector[j]
        if res > constraint.t:
            #print "testCVector: error at constraint ", i, constraint, "with vector", cvector, "res:", res
            return False
    return True


class CSpaceConstraint(object):
    def __init__(self, coeffs, a, d):
        self.coeffs = coeffs
        self.a = a
        self.d = d
        self.t = d - a

    def __repr__(self):
        reprStr = "\t+\t".join([str(a) + "\tx" + str(i+1) for i, a in enumerate(self.coeffs)])
        reprStr += "\t<=\t" + str(self.t)
        reprStr += "\t[" + str(self.a) + ", " + str(self.d) + "]"
        return reprStr

    def isRedundant(self, cspace):
        # cspace descibes constraints A X <= B
        # cstr is another C X <= d
        # We want to know if cstr is redundant w.r.t. cspace
        # Linear problem (solved by GLPK)
        # max C X
        # s.t.
        #   AX <= b
        #   C X <= d + 1
        # If the optimal value of the LP is > d, the
        if len(cspace) == 0:
            return False
        self.writeRedundancyGLPSOLData(cspace, "redundant_temp.dat")
        p = subprocess.Popen(args=["glpsol", "-m", os.path.join("GLPK", "redundant.mod"), "-d", "redundant_temp.dat"], stdout=subprocess.PIPE)
        (output, err) = p.communicate()
        reRes = re.search(r".*?Display\ statement\ at\ line\ 28.*?(?P<number>[0-9]+).*", str(output), re.DOTALL)
        resultMaximization = int(reRes.group('number'))
        return resultMaximization <= self.t

    def writeRedundancyGLPSOLData(self, cspace, filename):
        assert len(cspace) >= 1
        assert len(cspace[0]) >= 1
        with open(filename, 'w') as f:
            constrK = len(cspace)
            taskN = len(cspace[0])
            f.write("param constrK := " + str(constrK) + ";\n")
            f.write("param taskN := " + str(taskN) + ";\n")

            f.write("param nJob: ")
            for i in range(taskN):
                f.write(str(i + 1) + " ")
            f.write(":=\n")
            for i, eq in enumerate(cspace):
                f.write(str(i + 1) + "\t")
                for nJob in eq.coeffs:
                    f.write(str(nJob) + " ")
                if i == constrK - 1:
                    f.write(";")
                f.write("\n")

            f.write("param tk := \n")
            for i, eq in enumerate(cspace):
                f.write(str(i + 1) + "\t")
                f.write(str(eq.t))
                if i < constrK - 1:
                    f.write(",\n")
                else:
                    f.write(";\n")

            f.write("param nJobNew := \n")
            for i, nJobNew in enumerate(self.coeffs):
                f.write(str(i + 1) + "\t" + str(nJobNew))
                if i < taskN - 1:
                    f.write(",\n")
                else:
                    f.write(";\n")

            f.write("param tkNew := ")
            f.write(str(self.t))
            f.write(";\n")

    def __getitem__(self, key):
        return self.coeffs.__getitem__(key)

    def __setitem__(self, key, val):
        return self.coeffs.__getitem__(key, val)

    def __delitem__(self, key):
        return self.coeffs.__getitem__(key)

    def __len__(self):
        return self.coeffs.__len__()

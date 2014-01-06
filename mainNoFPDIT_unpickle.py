import pylab

import pickle

if __name__ == '__main__':
    symbols = ['D', 'o', 's', '*', 'v', '^']
    with open('noFPDIT_results.pickle', 'rb') as inputR:
        (noFPDITpcts, CDFvalues, nValues, NUMBER_OF_SYSTEMS) = pickle.load(inputR)
    pylab.figure()
    for i, taskCnt in enumerate(reversed(nValues)):
        noFPDITpctsPerCDF = []
        for cdf in CDFvalues:
            noFPDITpctsPerCDF.append(noFPDITpcts[taskCnt][cdf])
        pylab.plot(CDFvalues, noFPDITpctsPerCDF, "-" + str(symbols[i]), label=str(taskCnt) + " Tasks")
    pylab.ylabel("%")
    pylab.xlabel("CDF")
    pylab.title("Number of systems with no FPDIT (" + str(NUMBER_OF_SYSTEMS) + " systems/point)")
    pylab.legend(loc=0)
    # pylab.axis()
    # pylab.savefig("./plots/001_" + str(time.time()).replace(".", "") + ".png")
    pylab.show()

import matplotlib.pylab as pylab
import pickle
import time

if __name__ == '__main__':
    with open('results', 'rb') as input:
        (paramInfo, results) = pickle.load(input)

    print(results)
    nSystems = paramInfo
    pylab.ylabel("Amount of systems")
    pylab.xlabel("Synchronous/asynchronous C-space size ratio")
    pylab.hist(results, bins=10)
    pylab.title(" ("+str(nSystems)+" systems)")
    pylab.savefig("./plots/cspaceHist_n"+str(nSystems)+"_"+str(time.time()).replace(".", "") + ".png")
    pylab.show()

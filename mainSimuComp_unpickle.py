
from matplotlib import pylab
import pickle
import sys

argv = sys.argv[1:]
argc = len(argv)
# default values
pickFilePath = "mainSimuComp_results.pickle"
otherPickFilesPath = None
aggregate = False
# parameter -i : give one pickle file
if argc == 2 and argv[0] == "-i":
    pickFilePath = argv[1]
# parameter -a : aggregate pickle files
if argc > 2 and argv[0] == "-a":
    aggregate = True
    pickFilePath = argv[1]
    otherPickFilesPath = argv[2:]

with open(pickFilePath, 'rb') as inputR:
    (domin_scores, scores, NUMBER_OF_SYSTEMS, uRange, schedulers, names, generate_synchronous_only, CDF, failures) = pickle.load(inputR)

if aggregate:
    for fp in otherPickFilesPath:
        with open(fp, 'rb') as otherInput:
            (domin_scores2, scores2, NUMBER_OF_SYSTEMS2, uRange2, schedulers2, names2, generate_synchronous_only2, CDF2, failures2) = pickle.load(otherInput)
            # sanity check
            assert NUMBER_OF_SYSTEMS2 == NUMBER_OF_SYSTEMS, "incompatible aggregation (different NUMBER_OF_SYSTEMS)"
            assert CDF2 == CDF, "incompatible aggregation (different CDF)"
            assert generate_synchronous_only == generate_synchronous_only2, "incompatible aggregation (different generate_synchronous_only)"
            assert len(scores) == len(scores2) == len(uRange) == len(uRange2)
            for sched, name, score in zip(schedulers2, names2, scores2):
                if sched not in schedulers:
                    schedulers.append(sched)
                    names.append(name)
                    for u in uRange:
                        scores[u][sched] = scores2[u][sched]


symbols = ['D', 'o', 's', '*', 'v', '^']

pylab.figure()
for i, sched in enumerate(schedulers):
    # dom_pct = [100 * domin_scores[u][sched] / NUMBER_OF_SYSTEMS for u in uRange]
    result = [scores[u][sched] for u in uRange]
    result_pct = list(map(lambda r: 100 * r / NUMBER_OF_SYSTEMS, result))
    print("result_pct of ", names[i], result_pct)
    pylab.plot(uRange, result_pct, "--" + symbols[i], label=names[i])

pylab.ylabel("% schedulable")
pylab.xlabel("System utilization")
arrivalTypeString = "synchronous" if generate_synchronous_only else "asynchronous"
deadlineTypeString = "implicit" if CDF == 0 else "constrained-deadline"
graph_title = "Schedulability of " + deadlineTypeString + " " + arrivalTypeString + " systems\n" + str(NUMBER_OF_SYSTEMS) + " systems per point"
pylab.title(graph_title)
pylab.legend(loc=0)
pylab.axis([uRange[0] - 0.1, uRange[-1] + 0.1, 0,  100])
pylab.grid()
pylab.show()

for fail in failures:
    print("FAIL", str(fail))

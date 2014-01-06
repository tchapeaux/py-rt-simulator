
import pylab
import pickle


symbols = ['D', 'o', 's', '*', 'v', '^']
with open('mainSimuComp_results.pickle', 'rb') as inputR:
    (domin_scores, scores, NUMBER_OF_SYSTEMS, uRange, schedulers, names, failures) = pickle.load(inputR)

pylab.figure()
for i, sched in enumerate(schedulers):
    dom_pct = [100 * domin_scores[u][sched] / NUMBER_OF_SYSTEMS for u in uRange]
    result = [scores[u][sched] for u in uRange]
    result_pct = list(map(lambda r: 100 * r / NUMBER_OF_SYSTEMS, result))
    print("result_pct of ", names[i], result_pct)
    pylab.plot(uRange, result_pct, "--o", label=names[i])

pylab.ylabel("% schedulable")
pylab.xlabel("System utilization")
pylab.title("Schedulability of implicit systems (n = " + str(NUMBER_OF_SYSTEMS) + ")")
pylab.legend(loc=0)
pylab.axis([uRange[0] - 0.1, uRange[-1] + 0.1, 0,  100])
pylab.grid()
pylab.show()

for fail in failures:
    print("FAIL", str(fail))

from . import main
import algorithms

import multiprocessing
import array
import time
import pylab	
import sys
import atexit
import os
import signal

def cleanup():
	pList = multiprocessing.active_children()
	for p in pList:
		os.kill(p.pid(),signal.SIGKILL)
# 		p.terminate()
		
atexit.register(cleanup)
	

class Worker(object):
	def __init__(self, cdfIndex, numSystems, numCdfValues):
		self.cdfIndex = cdfIndex
		self.numCdfValues = numCdfValues
		self.numSystems = numSystems
	
	def run(self,resQueue,globalCdfIndex,cdfArray,resLock,outLock):
		self.globalCdfIndex = globalCdfIndex
		self.resQueue = resQueue
		self.cdfArray = cdfArray
		self.outLock = outLock
		allDone = False
		while(not allDone):
			result = self.runSystems(self.numSystems, self.cdfArray[self.cdfIndex])
			resQueue.put((self.cdfIndex,result))
  			resLock.acquire()
			if(globalCdfIndex.value < self.numCdfValues):
				self.cdfIndex = self.globalCdfIndex.value
				self.globalCdfIndex.value += 1
			else:
				allDone = True
   			resLock.release()
			
	def runSystems(self,numberOfSystems, constrDeadlineFactor):
		systemArray = main.generateSystemArray(numberOfSystems, constrDeadlineFactor, verbose=False)
		print("systems generated")
		sys.stdout.flush()
		verbose = False
	
		# Upper Limit Arrays
		busyPeriods = []
		firstDITs = []
		hyperTs = []
		# Feasibility Arrays
# 		bpResults = []
		ditResults = []
		hyperTResults = []
	
		# Compare algorithms
	
# # 		print "Thread", self.cdfIndex, "start busy period tests..."
 		bpStart = time.clock()
# 		for tau in systemArray:
# 			busyPeriods.append(algorithms.findBusyPeriod(tau))
 		bpMedium = time.clock()
# 		for i, tau in enumerate(systemArray):
# 			bpResults.append(algorithms.dbf_test(tau, busyPeriods[i]))
 		bpStop = time.clock()
	
	
		print(("CDF Index", self.cdfIndex, "starting hyperperiod computation..."))
		sys.stdout.flush()
		hyperTStart = time.clock()
		for i, tau in enumerate(systemArray):
			hyperTs.append(tau.hyperPeriod())
		hyperTMedium = time.clock()
		for i, tau in enumerate(systemArray):
			print(("CDF Index", self.cdfIndex, "system", i))
			sys.stdout.flush()
			hyperTResults.append(algorithms.dbfTest(tau))
		hyperTStop = time.clock()

		ditStart = time.clock()
		for i, tau in enumerate(systemArray):
			#print i
			firstDITs.append(algorithms.findFirstDIT(tau))
		ditMedium = time.clock()
		for i, tau in enumerate(systemArray):
			ditResults.append(algorithms.dbfTest(tau, firstDITs[i]))
		ditStop = time.clock()
	
		for i in range(len(systemArray)):
			assert ditResults[i] == hyperTResults[i]
	
# 		self.outLock.acquire()
# 		print "Thread", self.cdfIndex, "== Test Results (on " + str(numberOfSystems) + " tasks system)"
# 		if (verbose and len(systemArray) <= 10):
# 			for i in range(len(systemArray)):
# 				print "=== System", i
# 				print "\tbusy period:", busyPeriods[i]
# 				print "\tfirst DIT:", firstDITs[i]
# 				print "\tPPCM:", hyperTs[i]
# 		print "\tAlgorithms performance (upper limit computation + dbf test)"
# 		print "\t\tTime with busy period:", bpMedium - bpStart, "+", bpStop - bpMedium, " = ", bpStop - bpStart, "s"
# 		print "\t\tTime with DIT:", ditMedium - ditStart, "+", ditStop - ditMedium, " = ", ditStop - ditStart, "s"
# 		print "\t\tTime with hyperT:", hyperTMedium - hyperTStart, "+", hyperTStop - hyperTMedium, " = ", hyperTStop - hyperTStart, "s"
# 		feasibleSystemCnt = reduce(lambda x, y: x + (y is True), bpResults)
# 		print "\tFeasible?", feasibleSystemCnt, ", or about", int(round((feasibleSystemCnt * 100.0)/len(systemArray))), "%"
# 		self.outLock.release()
	
		return bpStop - bpMedium, bpMedium - bpStart, ditStop - ditMedium, ditMedium - ditStart, hyperTStop - hyperTMedium, hyperTMedium - hyperTStart

def processRun(cdfIndex, numSystems, numCdfValues, resQueue, globalCdfIndex, cdfArray, resLock, outLock):
	work = Worker(cdfIndex, numSystems, numCdfValues)
	work.run(resQueue, globalCdfIndex, cdfArray, resLock, outLock)
	
# def zombieKiller(masterQueue, workerPidList):
# 	master = masterQueue.get()
# 	master.join()
# 	for worker in workerPidList:
# 		os.kill(worker, signal.SIGKILL)
# 	sys.exit()
		
class ProcessManager(object):
	def __init__(self,cdf,threadCountLimit,numSystems):
		self.resultsQueue = multiprocessing.Queue()
		self.stdoutLock = multiprocessing.Lock()
		self.numSystems = numSystems
		self.cdf = multiprocessing.Array('d', cdf)
		self.numCdfValues = len(self.cdf)
		self.processCountLimit = min(threadCountLimit,self.numCdfValues)
		self.workerList = []
		self.bpValue = array.array('f',[0.0])*self.numCdfValues
		self.bpTest = array.array('f',[0.0])*self.numCdfValues
		self.bpAll = array.array('f',[0.0])*self.numCdfValues
		self.ditValue = array.array('f',[0.0])*self.numCdfValues
		self.ditTest = array.array('f',[0.0])*self.numCdfValues
		self.ditAll = array.array('f',[0.0])*self.numCdfValues
		self.hyperTValue = array.array('f',[0.0])*self.numCdfValues
		self.hyperTTest = array.array('f',[0.0])*self.numCdfValues
		self.hyperTAll = array.array('f',[0.0])*self.numCdfValues
		
	def runAllThreads(self):
		self.curCdfIndex = multiprocessing.Value('i',0)
		resLock = multiprocessing.Lock()
		outLock = multiprocessing.Lock()
		resLock.acquire()
		for i in range(self.processCountLimit):
			t = multiprocessing.Process(target=processRun, 
										args=(	self.curCdfIndex.value,self.numSystems,	self.numCdfValues, 
												self.resultsQueue,self.curCdfIndex,self.cdf,resLock,outLock))
			self.workerList.append(t)
			t.start()
			self.curCdfIndex.value += 1
# 		masterQueue = multiprocessing.Queue()
# 		masterQueue.put(multiprocessing.current_process())
#  		k = multiprocessing.Process(target=zombieKiller, args=(masterQueue,[worker.pid for worker in self.workerList]))
#  		k.start()
		resLock.release()
			
		for i in range(self.numCdfValues):
			cdfIndex,res = self.resultsQueue.get()
			print(("Got results for cdf", self.cdf[cdfIndex], [round(r,3) for r in res]))
			self.bpValue[cdfIndex] = res[1]
			self.bpTest[cdfIndex] = res[0]
			self.bpAll[cdfIndex] = res[0] + res[1]
			self.ditValue[cdfIndex] = res[3]
			self.ditTest[cdfIndex] = res[2]
			self.ditAll[cdfIndex] = res[2] + res[3]
			self.hyperTValue[cdfIndex] = res[5]
			self.hyperTTest[cdfIndex] = res[4]
			self.hyperTAll[cdfIndex] = res[4] + res[5]
			
		for t in self.workerList:
			t.join()
			
if __name__ == '__main__':	
	NUMBER_OF_SYSTEMS = 10000
	cdfRange = [1]
# 	cdfRange = [f/2.0 for f in range(2, 11)]
	manager = ProcessManager(cdfRange,4,NUMBER_OF_SYSTEMS)
	manager.runAllThreads()

 	pylab.figure()
#  	pylab.plot(cdfRange, manager.bpAll, "k-", label="BP ALL")
#  	pylab.plot(cdfRange, manager.bpValue, "k--", label="BP VALUE")
 	pylab.plot(cdfRange, manager.ditAll, "b-", label="DIT ALL")
 	pylab.plot(cdfRange, manager.ditValue, "b--", label="DIT VALUE")
 	pylab.plot(cdfRange, manager.hyperTAll, "r-", label="HYPERT ALL")
 	pylab.plot(cdfRange, manager.hyperTValue, "r--", label="HYPERT VALUE")
 	pylab.ylabel("time (s)")
 	pylab.xlabel("e")
 	pylab.title("Computation time for some values of e (" + str(NUMBER_OF_SYSTEMS) + " systems)")
 	pylab.legend(loc=0)
 # 	pylab.axis([cdfRange[0], cdfRange[-1], -0.5, 6])
 	pylab.savefig("./plots/001_" + str(time.time()).replace(".", "") + ".png")
 	pylab.show()

		
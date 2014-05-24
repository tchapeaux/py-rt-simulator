PyRTSS
=======

Python Real-Time System Simulator, developed during my final year of Master to help me with my [Master Thesis](http://www.thomaschapeaux.be/assets/Master_Thesis.pdf) on the integration of preemption costs.

Dependencies
------------

* GLPK v4.45+, see http://www.gnu.org/software/glpk/ or use the provided installer in /GLPK/
* pycairo module for displaying the simulator result
* matplotlib module in some scripts

Usage
-----

Systems can be described in a text file. An example is provided in `/systems/task_example.system`

* To launch the simulator on a given system: `python3 mainSimu.py -sys path/of/input_file -sched NAME_OF_SCHEDULER`

* To compare two schedulers on a given number of systems: `python3 mainSimuComp.py`. Parameters:
    + `sched1` : Name of the supposed 'best' schedulers
    + `sched2` : Name of the supposed 'worst' schedulers
    + `writeVict` : Log systems scheduled by 1 but not by 2 (1/0, def: 0)
    + `writeFail` : Log systems scheduled by 2 but not by 1 (1/0, def: 0)
    + `o` : log file (default: " + outFilePath + "
    + `p` : pickle file (default: " + pickFilePath + "
    + `n` : number of systems per data point (def: 1000)
    + `synchr` : generate synchronous system only (1/0 def: 0)
    + `cdf` : float value of the CDF (0: implicit, 1: fully constrained)

* To calculate the C-space of a given system: `python3 mainCspace.py path/of/input_file`

* To launch tests `python3 runtests.py`

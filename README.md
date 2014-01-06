Python Real-Time Systems Simulator
==================================
by Thomas Chapeaux

Some initial help by Paul Rodriguez

Dependencies
------------

* GLPK v4.45+, see http://www.gnu.org/software/glpk/ or use the provided installer in /GLPK/
* pycairo module for displaying the simulator result
* matplotlib module in some scripts

Usage
-----

Systems can be described in a text file. An example is provided in /systems/task_example.system

To launch the simulator on a given system:
python3 mainSimu.py path/of/input_file

To calculate the C-space of a given system:
python3 mainCspace.py path/of/input_file

To launch tests
python3 runtests.py

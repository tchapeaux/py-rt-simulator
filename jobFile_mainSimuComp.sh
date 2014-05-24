#!/bin/bash -l
#PBS -l nodes=3:ppn=12
#PBS -l walltime=24:00:00
#PBS -l mem=32gb
#PBS -o stdout.txt
#PBS -e stderr.txt
#PBS -N mainSimuComp

cd $WORKDIR/py-rt-simulator
rm -f stderr.txt
rm -f stdout.txt
rm -f mainSimuComp_log.txt
rm -f mainSimuComp_results.pickle
module load python/3.4.0a1
python3 mainSimuComp.py -p mainSimuComp_results.pickle -n 10000 -sched1 PMImp -sched2 EDF -writeFail 1

#!/bin/bash -l
#PBS -l nodes=8:ppn=2
#PBS -l walltime=12:00:00
#PBS -l mem=16gb
#PBS -o stdout.txt
#PBS -e stderr.txt
#PBS -N mainSimuComp

cd $WORKDIR/py-rt-simulator
rm stderr.txt
rm stdout.txt
rm mainSimuComp_log.txt
rm mainSimuComp_results.pickle
module load python/3.4.0a1
python3 mainSimuComp.py -p mainSimuComp_results.pickle -n 100000 -sched1 PMImp -sched2 EDF

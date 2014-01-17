#!/bin/bash -l
#PBS -l nodes=8:ppn=2
#PBS -l walltime=6:00:00
#PBS -l mem=1gb
#PBS -o mainFindLongTransitive_stdout.txt
#PBS -e mainFindLongTransitive_stderr.txt
#PBS -N mainFindLongTransitive

cd $WORKDIR/py-rt-simulator
rm -f mainFindLongTransitive_stdout.txt
rm -f mainFindLongTransitive_stderr.txt
module load python/3.4.0a1
python3 mainFindLongTransitive.py

#!/bin/bash -l

#PBS -l nodes=8:ppn=2
#PBS -l walltime=20:00:00
#PBS -l mem=4Gb
#PBS -o stdout.txt
#PBS -e stderr.txt
#PBS -N part

echo "Running job on $HOST - " `date` 

cd $HOME/partitioning
module load python/3.4.0a1
PATH=$PATH:$HOME/glpk/bin
echo `pwd`
python3 $HOME/python-simulation/hydraSizeHist.py

echo "Done"
#!/bin/bash -l

#PBS -l nodes=8:ppn=2
#PBS -l walltime=20:00:00
#PBS -l mem=1gb
#PBS -o stdout.txt
#PBS -e stderr.txt
#PBS -N mainSimuComp

echo "Running job on $HOST - " `date`

cd $HOME/Repositories/py-rt-simulator
module load python/3.4.0a1
#PATH=$PATH:$HOME/glpk/bin
echo `pwd`
python3 $HOME/Repositories/py-rt-simulator/mainSimuComp.py

echo "Done"

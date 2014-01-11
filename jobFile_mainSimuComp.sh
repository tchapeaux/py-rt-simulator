#!/bin/bash -l

#PBS -l nodes=8:ppn=2
#PBS -l walltime=3:00:00
#PBS -l mem=1gb
#PBS -o stdout.txt
#PBS -e stderr.txt
#PBS -N mainSimuComp

cd $HOME/py-rt-simulator
module load python/3.4.0a1
python3 mainSimuComp.py

#!/bin/bash
#SBATCH -p debug 
#SBATCH -N 2
#SBATCH -t 00:20:00
#SBATCH -J fits-hdf
#SBATCH -e %j.err
#SBATCH -o %j.out
#SBATCH -V

cd $SLURM_SUBMIT_DIR
python  h5fits-parallel.py  64 

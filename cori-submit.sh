#!/bin/bash
#SBATCH -p debug 
#SBATCH -N 1
#SBATCH -t 00:20:00
#SBATCH -J h5py-col
#SBATCH -e %j.err
#SBATCH -o %j.out
#SBATCH -V

cd $SLURM_SUBMIT_DIR

#fits2hdf $fitsinput $hdfoutput
fits2hdf $fitsinput -x gz $hdfoutput

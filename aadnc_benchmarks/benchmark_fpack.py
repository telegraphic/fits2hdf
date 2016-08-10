"""
benchmark compression
---------------------

Generate benchmarks for AANDC paper.

"""
from os.path import  getsize
import os
import time
import glob
import subprocess

fits_dir = 'fits_generated'

for fits_filename in glob.glob(os.path.join(fits_dir, '*.fits')):

    fits_comp_filename = fits_filename + '.fz'
    if os.path.exists(fits_comp_filename):
        os.remove(fits_comp_filename)

    t0 = time.time()
    subprocess.check_call(['fpack','-table',fits_filename])
    t1 = time.time()


    dd = {
        'img_name': fits_filename,
        'fits_size': getsize(fits_filename),
        'fits_comp_size': getsize(fits_filename + '.fz'),
        'comp_fact_fits': float(getsize(fits_filename)) / getsize(fits_comp_filename),
        'fits_comp_time': (t1 - t0)
        }

    print(fits_filename)
    print("FITS file size:        %sB" % dd['fits_size'])
    print("FITS comp size:        %sB" % dd['fits_comp_size'])
    print("FITS comp time:        %2.2fs" % dd['fits_comp_time'])
    print("FITS/FITS compression: %2.2fx\n" % dd['comp_fact_fits'])

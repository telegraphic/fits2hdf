"""
benchmark compression
---------------------

Generate benchmarks for AANDC paper.

"""

import numpy as np
from os.path import join, getsize,exists
import os, sys
from fits2hdf import idi
from fits2hdf.io import hdfio, fitsio
import time
import glob

from astropy.table import Table, Column

fits_dir = sys.argv[1]

for fits_filename in glob.glob(os.path.join(fits_dir, '*.fits')):

    fits_comp_filename = fits_filename + '.fz'
    if os.path.exists(fits_comp_filename):
        os.remove(fits_comp_filename)

    t0 = time.time()
    os.system("./fpack -table %s" % fits_filename)
    t1 = time.time()
    


    
    dd = {
        'img_name': fits_filename,
        'fits_size': getsize(fits_filename),
        'fits_comp_size': getsize(fits_filename + '.fz'),
        'comp_fact_fits': float(getsize(fits_filename)) / getsize(fits_comp_filename),
        'fits_comp_time': (t1 - t0)
        }
        
    print fits_filename
    print "FITS file size:        %sB" % dd['fits_size']
    print "FITS comp size:        %sB" % dd['fits_comp_size']
    print "FITS comp time:        %2.2fs" % dd['fits_comp_time']
    print "FITS/FITS compression: %2.2fx\n" % dd['comp_fact_fits']

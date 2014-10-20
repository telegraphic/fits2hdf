import os, sys
sys.path.append('..')

from hdulib import hdu
from ms2hdf import *
import pylab as plt
import numpy as np
import pyfits as pf
import h5py


if __name__ == '__main__':

    create_hdf = True
    create_ms = False
    ext = 'ms'

    if create_hdf:
        os.system('python ../ms2hdf.py ms hdfms -c lzf -x %s' % ext)

    if create_ms:
        pass
    #ms_dir  = 'ms/'
    #hdf_dir = 'hdfms/'
    #
    #if create_hdf:
    #    hd = ms2hdu(ms_dir + 'leda.ms', verbosity=5)
    #    ms  = pt.table(ms_dir + 'leda.ms')
    #
    #    hd.export_hdf(hdf_dir + "leda.h5")
    #
    #if create_ms:
    #    hdf2ms("testms.h5", "test.ms", verbosity=5)
    #
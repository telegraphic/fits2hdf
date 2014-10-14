import os, sys
sys.path.append('..')

from hdulib import hdu
import pylab as plt
import numpy as np
import pyfits as pf

if __name__ == '__main__':
    
    #os.system('python download_test_fits.py')
    os.system('python ../fits2hdf.py fits hdf -c gzip')
    

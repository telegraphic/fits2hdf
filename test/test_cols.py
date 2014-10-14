import os, sys
sys.path.append('..')

from hdulib import hdu
import pylab as plt
import numpy as np
import pyfits as pf

if __name__ == '__main__':

    idi = hdu.IdiList()
    idi.read_fits('test_ovro.fitsidi')
    print idi["ANTENNA"].data
    idi.export_hdf("test_ovro.hdf", compression="bitshuffle")
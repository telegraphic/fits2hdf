import os
import sys
sys.path.append('..')

from fits2hdf.io.fitsio import *
from fits2hdf.io.hdfio import *
from fits2hdf import idi
import numpy as np
from astropy.io import fits as pf
import h5py


def test_multihdf():

    filenames = ["eagle.fits", "FGSf64y0106m_a1f.fits", "EUVEngc4151imgx.fits"]
    try:
        for fname in filenames:
            a = read_fits('fits/' + fname)

            export_hdf(a, "output.hdf", root_group=fname)
            h = h5py.File("output.hdf")
            print h.keys()
            h.close()

    except:
        raise
    finally:
        #os.remove("output.hdf")
        pass



if __name__ == '__main__':
    test_multihdf()
# -*- coding: utf-8 -*-
"""
pyhdfits.py
===========

Open either a FITS file, or a HDFITS file, and return a FITS object.
Idea here is to do

>> from fits2hdf import pyhdfits as pf

instead of

>> from astropy.io import fits as pf

So that both HDF5 and FITS files can be read transparently.
"""

import os
from astropy.io import fits as pfo

from io.hdfio import *
from io.fitsio import *
from astropy.io.fits import *
from astropy.io.fits import PrimaryHDU, ImageHDU, CompImageHDU

def check_file_type(file_name):
    """ Check what kind of file a file is based on its filename """

    file_root, file_ext = os.path.splitext(file_name)

    fits_exts = {'.fits', '.sdfits', '.fitsidi', '.sdf', '.psrfits'}
    hdf_exts  = {'.h5', '.hdf', '.hdf5', '.hdfits'}

    file_ext = file_ext.lower()
    if file_ext in fits_exts:
        return 'fits'
    elif file_ext in hdf_exts:
        return 'hdf'
    else:
        return 'unknown'


def open(*args, **kwargs):
    """ Open a file, and return a FITS HDUList object.

    This overrides the default pyfits open, and first checks to see if the file
    is a HDF5 file. If so, then the file is opened using fits2hdf.io.hdfio
    and then exported to a FITS file (in memory, not on disk).
    """
    file_name = args[0]
    file_type = check_file_type(file_name)
    if file_type == 'fits':
        return pfo.open(*args, **kwargs)
    elif file_type == 'hdf':
        hdul = read_hdf(file_name)
        return create_fits(hdul)
    else:
        raise RuntimeError("File type could not be found from file extension.")


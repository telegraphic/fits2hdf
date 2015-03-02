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

from astropy.io import fits as pfo
from astropy.io.fits import *

from io.hdfio import *
from io.fitsio import *

from check_file_type import check_file_type

def open(*args, **kwargs):
    """ Open a file, and return a FITS HDUList object.

    This overrides the default pyfits open, and first checks to see if the file
    is a HDF5 file. If so, then the file is opened using fits2hdf.io.hdfio
    and then exported to a FITS file (in memory, not on disk).

    Notes
    -----
    If you're not careful, this will override the standard open() class. So,
    never do "from pyhdfits import open", as this would be bad.
    #TODO: Do this slightly different, to avoid the open() issue
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


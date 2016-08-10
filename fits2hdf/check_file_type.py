# -*- coding: utf-8 -*-
"""
check_file_type.py
==================

Utilities for checking what kind of file (HDF5 or FITS) a filepath is.
"""

import os

# FITS file signature as per RFC 4047
FITS_SIGNATURE = (b"\x53\x49\x4d\x50\x4c\x45\x20\x20\x3d\x20\x20\x20\x20\x20"
                  b"\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20\x20"
                  b"\x20\x54")

HDF5_SIGNATURE = b'\x89HDF\r\n\x1a\n'

def is_hdf(filepath):
    return is_hdf5(filepath)

def is_hdf5(filepath):
    """
    Check if a file is a HDF5 file

    Returns True of False

    Parameters
    ----------
    filepath: str
        Path to file
    """
    with open(str(filepath),'r') as f:
        try:
            return f.read(8) == HDF5_SIGNATURE
        except (OSError,IOError):
            return False


def is_fits(filepath):
    """
    Check if file is a FITS file

    Returns True of False

    Parameters
    ----------
    filepath: str
        Path to file
    """
    with open(str(filepath),'r') as f:
        return fileobj.read(30) == FITS_SIGNATURE
    except (OSError,IOError):
        return False

def check_file_type(file_name):
    """
    Check what kind of file a file is based on its filename

    Parameters
    ----------
    file_name: str
        file name to check type of


    Returns
    -------
    filetype: string
        string of either 'fits', 'hdf', or 'unknown'
    """

    file_root, file_ext = os.path.splitext(file_name)

    fits_exts = {'.fits', '.sdfits', '.fitsidi', '.sdf', '.psrfits'}
    hdf_exts  = {'.h5', '.hdf', '.hdf5', '.hdfits'}

    file_ext = file_ext.lower()
    if file_ext in fits_exts:
        return 'fits'
    elif file_ext in hdf_exts:
        return 'hdf'
    elif is_fits(file_name):
        return 'fits'
    elif is_hdf(file_name):
        return 'hdf'
    else:
        return 'unknown'

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
hdf2fits.py
===========

FITS to HDF5 conversion utility. This script takes a HDFITS-formatted
HDF5 files, processes it into an in-memory data structure, then converts
this to a FITS files.
"""

from fits2hdf.file_conversion import convert_hdf_to_fits

if __name__ == '__main__':
    convert_hdf_to_fits(args=None)

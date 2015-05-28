#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
fits2hdf.py
===========

FITS to HDF5 conversion utility. This script takes a FITS file, processes it into
an in-memory data structure, then converts this to a HDF5 file.
"""

from fits2hdf.file_conversion import convert_fits_to_hdf

if __name__ == '__main__':
    convert_fits_to_hdf(args=None)
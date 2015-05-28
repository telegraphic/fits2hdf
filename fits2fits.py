#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
fits2hdf.py
===========

FITS to FITS conversion utility. This script takes a FITS file, loads it into
an in-memory data structure, then outputs a FITS file. This utility is provided
for testing, and so that you can see how your data may be affected by hdf2fits.

Notes
------

The FITS writing routines in ``fits2hdf`` only output binary tables and images. So,
if your original data was an ASCII table, or a random group, then it won't come
out quite the same. However, the contents of data should be the same.
Similarly, you can expect to lose a few header keywords on mandatory things like
BITPIX and SIMPLE. Units are parsed and converted into units that astropy 
agrees with.
"""

from fits2hdf.file_conversion import convert_fits_to_fits

if __name__ == '__main__':
    convert_fits_to_fits(args=None)
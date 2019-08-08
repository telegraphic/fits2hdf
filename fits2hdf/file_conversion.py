#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
fits2hdf.py
===========

FITS to HDF5 conversion utility. This script takes a FITS file, processes it into
an in-memory data structure, then converts this to a HDF5 file.
"""

import os
import time
import warnings

from fits2hdf.idi import IdiHdulist
from fits2hdf.io.fitsio import *
from fits2hdf.io.hdfio import *

from fits2hdf.printlog import PrintLog

import argparse

def convert_fits_to_hdf(args=None):
    """ Convert a FITS file to HDF5 in HDFITS format

    An input and output directory must be specified, and all files with a matching
    extension will be converted. Command line options set the compression algorithm
    and other run-time settings.
    """
    # Parse options and arguments
    parser = argparse.ArgumentParser(description='Convert FITS files to HDF5 files in HDFITS format.')
    parser.add_argument('-c', '--compression', dest='comp', type=str,
                        help='Data compression. Defaults to None, also lzf, bitshuffle, gzip')
    parser.add_argument('-x', '--extension', dest='ext', type=str, default='fits',
                        help='File extension of FITS files. Defaults to .fits')
    parser.add_argument('-v', '--verbosity', dest='verbosity', type=int, default=4,
                        help='verbosity level (default 0, up to 5)')
    parser.add_argument('-s', '--scaleoffset', dest='scale_offset', default=None,
                        help='Add scale offset')
    parser.add_argument('-S', '--shuffle', dest='shuffle', action='store_true', default=None,
                        help='Apply byte shuffle filter')
    parser.add_argument('-t', '--pytables', dest='table_type', action='store_true', default=None,
                        help='Set output tables to be PyTables TABLE class, instead of HDFITES DATA_GROUP')
    parser.add_argument('-C', '--checksum', dest='checksum', action='store_true', default=None,
                        help='Compute fletcher32 checksum on datasets.')
    parser.add_argument('dir_in', help='input directory')
    parser.add_argument('dir_out', help='output_directory')

    args = parser.parse_args()

    dir_in  = args.dir_in
    dir_out = args.dir_out

    if not os.path.exists(dir_out):
        print("Creating directory %s" % dir_out)
        os.mkdir(dir_out)

    # Form a list of keyword arguments to pass to HDF5 export
    kwargs = {}
    if args.comp is not None:
        kwargs['compression'] = args.comp
    if args.scale_offset is not None:
       kwargs['scaleoffset'] = int(args.scale_offset)
    if args.shuffle is not None:
       kwargs['shuffle'] = args.shuffle
    if args.checksum is not None:
       kwargs['fletcher32'] = args.checksum
    if args.table_type is not None:
       kwargs['table_type'] = 'TABLE'
    else:
        kwargs['table_type'] = 'DATA_GROUP'

    pp = PrintLog(verbosity=args.verbosity)
    if args.verbosity == 0:
        warnings.simplefilter("ignore")

    pp.h1("FITS2HDF")
    pp.pa("Input directory:  %s" % dir_in)
    pp.pa("Output directory: %s" % dir_out)
    pp.pa("Dataset creation arguments:")
    for key, val in kwargs.items():
        pp.pa("%16s: %s" % (key, val))

    # Create list of files to process
    filelist = os.listdir(dir_in)
    filelist = [fn for fn in filelist if fn.endswith(args.ext)]

    t_start = time.time()
    file_count = 0
    for filename in filelist:
        file_in = os.path.join(dir_in, filename)
        file_out = os.path.join(dir_out, filename.split('.' + args.ext)[0] + '.h5')

        a = IdiHdulist()
        try:
            pp.pp("\nReading  %s" % file_in)
            a = read_fits(file_in)
            pp.pp("Creating %s" % file_out)
            t1 = time.time()
            export_hdf(a, file_out, **kwargs)
            t2 = time.time()
            pp.pp("Input  filesize: %sB" % os.path.getsize(file_in))
            pp.pp("Output filesize: %sB" % os.path.getsize(file_out))
            compfact = float(os.path.getsize(file_in)) / float(os.path.getsize(file_out))
            pp.pp("Compression:     %2.2fx" % compfact)
            pp.pp("Comp/write time: %2.2fs" % (t2 - t1))

            file_count += 1

        except IOError:
            pp.err("ERROR: Cannot load %s" % file_in)

    pp.h1("\nSUMMARY")
    pp.pa("Files created: %i" % file_count)
    pp.pa("Time taken:    %2.2fs" % (time.time() - t_start))


def convert_hdf_to_fits(args=None):
    """ Convert a HDF5 (in HDFITS format) to a FITS file

    An input and output directory must be specified, and all files with a matching
    extension will be converted. Command line options set the run-time settings.
    """

    # Parse options and arguments
    parser = argparse.ArgumentParser(description='Convert HDF5 in HDFITS format FITS files.')
    parser.add_argument('-x', '--extension', dest='ext', type=str, default='h5',
                        help='File extension of HDFITS files. Defaults to .h5')
    parser.add_argument('-v', '--verbosity', dest='verbosity', type=int, default=4,
                        help='verbosity level (default 0, up to 5)')
    parser.add_argument('dir_in', help='input directory')
    parser.add_argument('dir_out', help='output_directory')
    args = parser.parse_args()

    dir_in  = args.dir_in
    dir_out = args.dir_out

    if not os.path.exists(dir_out):
        print("Creating directory %s" % dir_out)
        os.mkdir(dir_out)

    # Form a list of keyword arguments to pass to HDF5 export
    kwargs = {}

    pp = PrintLog(verbosity=args.verbosity)
    if args.verbosity == 0:
        warnings.simplefilter("ignore")

    pp.h1("HDF2FITS")
    pp.pa("Input directory:  %s" % dir_in)
    pp.pa("Output directory: %s" % dir_out)
    pp.pa("Dataset creation arguments:")
    for key, val in kwargs.items():
        pp.pa("%16s: %s" % (key, val))

    # Create list of files to process
    filelist = os.listdir(dir_in)
    filelist = [fn for fn in filelist if fn.endswith(args.ext)]

    t_start = time.time()
    file_count = 0
    for filename in filelist:
        file_in = os.path.join(dir_in, filename)
        file_out = os.path.join(dir_out, filename.split('.' + args.ext)[0] + '.fits')

        a = IdiHdulist()
        try:
            pp.pp("\nReading  %s" % file_in)
            a = read_hdf(file_in)
            pp.pp("Creating %s" % file_out)
            t1 = time.time()
            export_fits(a, file_out, **kwargs)
            t2 = time.time()
            pp.pp("Input  filesize: %sB" % os.path.getsize(file_in))
            pp.pp("Output filesize: %sB" % os.path.getsize(file_out))
            compfact = float(os.path.getsize(file_in)) / float(os.path.getsize(file_out))
            pp.pp("Compression:     %2.2fx" % compfact)
            pp.pp("Comp/write time: %2.2fs" % (t2 - t1))

            file_count += 1

        except IOError:
            pp.err("ERROR: Cannot load %s" % file_in)

    pp.h1("\nSUMMARY")
    pp.pa("Files created: %i" % file_count)
    pp.pa("Time taken:    %2.2fs" % (time.time() - t_start))


def convert_fits_to_fits(args=None):
    """ Read a FITS file into the in-memory IDI format then back out into a FITS file

    An input and output directory must be specified, and all files with a matching
    extension will be converted. Command line options set the compression algorithm
    and other run-time settings.
    """
    # Parse options and arguments
    parser = argparse.ArgumentParser(description='Convert FITS files to HDF5 files in HDFITS format.')
    parser.add_argument('-x', '--extension', dest='ext', type=str, default='fits',
                      help='File extension of FITS files. Defaults to .fits')
    parser.add_argument('-v', '--verbosity', dest='vb', type=int, default=0,
                      help='verbosity level (default 0, up to 5)')
    parser.add_argument('-w', '--nowarn', dest='warn', action='store_false', default=True,
                      help='Turn off warnings created by FITS parsing')
    parser.add_argument('-o', '--overwrite', dest='overwrite', action='store_true', default=False,
                      help='Automatically overwrite output files if already exist')
    parser.add_argument('dir_in', help='input directory')
    parser.add_argument('dir_out', help='output_directory')

    args = parser.parse_args()

    dir_in  = args.dir_in
    dir_out = args.dir_out

    if not os.path.exists(dir_out):
        print("Creating directory %s" % dir_out)
        os.mkdir(dir_out)


    if not args.warn:
        warnings.simplefilter("ignore")

    if dir_in == dir_out:
        raise ValueError("Input directory cannot be same as output directory.")

    # Create list of files to process
    filelist = os.listdir(dir_in)
    filelist = [fn for fn in filelist if fn.endswith(args.ext)]

    t1 = time.time()
    file_count = 0
    for filename in filelist:


        file_in = os.path.join(dir_in, filename)
        file_out = os.path.join(dir_out, filename)

        a = IdiHdulist()
        try:
            a = read_fits(file_in)
            if os.path.exists(file_out):
                if args.overwrite:
                    os.remove(file_out)
                else:
                    qn = raw_input("%s exists. Overwrite (y/n)?" % file_out)
                    if qn in ["y", "Y", "yes"]:
                        os.remove(file_out)

            print("\nCreating %s" % file_out)
            export_fits(a, file_out)
            print("Input  filesize: %sB" % os.path.getsize(file_in))
            print("Output filesize: %sB" % os.path.getsize(file_out))
            compfact = float(os.path.getsize(file_in)) / float(os.path.getsize(file_out))
            print("Compression:     %2.2fx" % compfact)

            file_count += 1

        except IOError:
            print("ERROR: Cannot read/write %s" % file_in)

    print("\nSUMMARY")
    print("-------")
    print("Files created: %i" % file_count)
    print("Time taken:    %2.2fs" % (time.time() - t1))

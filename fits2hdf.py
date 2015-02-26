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
import optparse
import warnings

from fits2hdf.idi import IdiHdulist
from fits2hdf.io.fitsio import *
from fits2hdf.io.hdfio import *

from fits2hdf.printlog import PrintLog

if __name__ == '__main__':
    
    # Parse options and arguments
    parser = optparse.OptionParser(
        usage = 'Usage: %prog input_dir output_dir <options>. -h for optional args.',
        description  = 'Convert FITS files to HDF5 files in HDFITS format.')
    parser.add_option('-c', '--compression', dest='comp', type='string',
                      help='Data compression. Defaults to None, also lzf, bitshuffle, gzip')
    parser.add_option('-x', '--extension', dest='ext', type='string', default='fits',
                      help='File extension of FITS files. Defaults to .fits')
    parser.add_option('-v', '--verbosity', dest='verbosity', type='int', default=4,
                      help='verbosity level (default 0, up to 5)')
    parser.add_option('-s', '--scaleoffset', dest='scale_offset', default=None,
                      help='Add scale offset')
    parser.add_option('-S', '--shuffle', dest='shuffle', action='store_true', default=None,
                      help='Apply byte shuffle filter')
    parser.add_option('-C', '--checksum', dest='checksum', action='store_true', default=None,
                      help='Compute fletcher32 checksum on datasets.')
    (opts, args) = parser.parse_args()

    if len(args) == 2:
        dir_in  = args[0]
        dir_out = args[1]

        if not os.path.exists(dir_out):
            print "Creating directory %s" % dir_out
            os.mkdir(dir_out)
    else:
        parser.print_usage()
        exit()

    # Form a list of keyword arguments to pass to HDF5 export
    kwargs = {}
    if opts.comp is not None:
        kwargs['compression'] = opts.comp
    if opts.scale_offset is not None:
       kwargs['scaleoffset'] = int(opts.scale_offset)
    if opts.shuffle is not None:
       kwargs['shuffle'] = opts.shuffle
    if opts.checksum is not None:
       kwargs['checksum'] = opts.checksum

    pp = PrintLog(verbosity=opts.verbosity)
    if opts.verbosity == 0:
        warnings.simplefilter("ignore")

    pp.h1("FITS2HDF")
    pp.pa("Input directory:  %s" % dir_in)
    pp.pa("Output directory: %s" % dir_out)
    pp.pa("Dataset creation arguments:")
    for key, val in kwargs.items():
        pp.pa("%16s: %s" % (key, val))

    # Create list of files to process
    filelist = os.listdir(dir_in)
    filelist = [fn for fn in filelist if fn.endswith(opts.ext)]

    t1 = time.time()
    file_count = 0
    for filename in filelist:
        file_in = os.path.join(dir_in, filename)
        file_out = os.path.join(dir_out, filename.split('.' + opts.ext)[0] + '.h5')

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
    pp.pa("Time taken:    %2.2fs" % (time.time() - t1))
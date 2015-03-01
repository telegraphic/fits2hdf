#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ms2hdf.py
==========

Python class which reads a Measurement Set and converts it to HDF.
This is experimental, and as such expect it not to work very well.

"""

import os, sys, time, re
import numpy as np
import h5py
import optparse

from fits2hdf.io.msio import *
from fits2hdf.io.hdfio import *

if __name__ == '__main__':

    # Parse options and arguments
    parser = optparse.OptionParser(
        usage = 'Usage: %prog input_dir output_dir <options>',
        description  = 'Convert MS files to HDF5 files in HDFITS format.')
    parser.add_option('-c', '--compression', dest='comp', type='string',
                      help='Data compression. Defaults to none, also lzf, bitshuffle, gzip')
    parser.add_option('-x', '--extension', dest='ext', type='string', default='ms',
                      help='File extension of MS directories. Defaults to .ms')
    (opts, args) = parser.parse_args()
    if len(args) == 2:
        dir_in  = args[0]
        dir_out = args[1]
        comp = opts.comp
        if not os.path.exists(dir_out):
            print "Creating directory %s" % dir_out
            os.mkdir(dir_out)
    else:
        parser.print_usage()
        exit()

    # Create list of files to process
    filelist = os.listdir(dir_in)
    filelist = [fn for fn in filelist if fn.endswith(opts.ext)]

    t1 = time.time()
    file_count = 0
    for filename in filelist:
        file_in = os.path.join(dir_in, filename)
        file_out = os.path.join(dir_out, filename.split('.' + opts.ext)[0] + '.h5')

        a = IdiList(verbosity=0)
        try:
            a = read_ms(file_in)
            export_hdf(a, file_out, compression=comp)
            print "\nCreating %s" % file_out
            print "Input  filesize: %sB" % get_size_ms(file_in)
            print "Output filesize: %sB" % os.path.getsize(file_out)
            compfact = float(get_size_ms(file_in)) / float(os.path.getsize(file_out))
            print "Compression:     %2.2fx" % compfact

            file_count += 1

        except IOError:
            print "ERROR: Cannot load %s" % file_in

    print "\nSUMMARY"
    print "-------"
    print "Files created: %i" % file_count
    print "Time taken:    %2.2fs" % (time.time() - t1)






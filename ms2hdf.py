#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ms2hdf.py
==========

Python class which reads a Measurement Set and converts it to HDF

"""

import os, sys, time, re
import numpy as np
import h5py
import optparse
try:
    import pyrap.tables as pt
except ImportError:
    print "ERROR: could not load pyrap"
    print "This script requires pyrap to read and write MS files."
    print "Please install casacore and pyrap, and re-run this script."
    exit()
from hdulib.printlog import PrintLog
from hdulib.hdu import IdiTable, IdiList, VerificationError

def get_size_ms(start_path = '.'):
    """ Return size of MS directory
    http://stackoverflow.com/questions/1392413/
    calculating-a-directory-size-using-python
    """
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


def table2hdu(table, hd, verbosity=1, close_after=True):
    """ Convert MS table to a Header-Data unit
    :param table: name of table (MS path)
    :param hdu: header data unit, either a string or a HDU
    :return:  HDU version of MS table
    """
    pp = PrintLog(verbosity=verbosity)

    if isinstance(hd, str):
        pp.h3("Creating %s HDU" % hd)
        hd = IdiTable(name=hd)

    colnames = table.colnames()
    keywords = table.getkeywords()

    for colname in colnames:
        try:
            pp.debug("Reading col %s" % colname)
            hd.add_column(table.getcol(colname), name=colname)
        except RuntimeError:
            # This can be raised when no data is in the column
            pp.warn("Could not add %s" % colname)


    for key, val in keywords.items():
        hd.header.vals[key] = val

    if close_after:
        table.close()
    return hd


def ms2hdu(infile, verbosity=1):
    """ Convert MS to a HDF file
    :param infile:  Measurement Set path
    :return: HDU version of Measurement Set
    """
    pp = PrintLog(verbosity=verbosity)
    ms = pt.table(infile)

    # Create a HDU List for storing HDUs
    hdul = IdiList(verbosity=verbosity)

    # Add each column to the main HDU
    hdu_main = table2hdu(ms, "MAIN", verbosity=verbosity, close_after=False)
    hdul["MAIN"] = hdu_main

    # Now look for other keyword tables
    for key, val in ms.getkeywords().items():
        pp.debug(val)
        if type(val) in (unicode, str):
            if val.startswith("Table: "):
                tblpath = val.strip().split("Table: ")[1]
                pp.h2("Opening %s" % key)
                t = pt.table(tblpath)
                t_hdu = table2hdu(t, key, verbosity=verbosity)
                hdul[key] = t_hdu
        else:
            hdul["MAIN"].header.vals[key] = val

    ms.close()
    return hdul

def hdf2ms(hdf_file, ms_file, verbosity=1):
    """ Convert an HDF file to MS
    :param hdf_file: Input HDF-MS filename
    :param ms_file: Output MS filename

    TODO: Get this working properly.
    """
    pp = PrintLog(verbosity=verbosity)
    hdul = IdiList(verbosity=1)
    hdul.read_hdf("testms.h5")

    main_hdu = hdul["MAIN"]

    vdict = {'float32' : 'float',
               'float64' : 'double',
               'complex64' : 'complex',
               'complex128' : 'dcomplex',
               'int32'  : 'int',
               'uint32' : 'uint',
               'str'    : 'string',
               'bool'   : 'bool'
                }

    col_descs = []
    for col, cdata in main_hdu.data.items():
        col = str(col)
        pp.pp("%16s %s %s" % (col, cdata.shape, cdata.dtype))

        if cdata.ndim == 1:
            vt = vdict[str(cdata.dtype)]
            cdesc = pt.makescacoldesc(col, cdata[0], valuetype=vt)
        else:
            cdesc = pt.makearrcoldesc(col, cdata[0], valuetype=vt)
        col_descs.append(cdesc)

    tdesc = pt.maketabdesc(col_descs)

    t = pt.table("table.ms", tdesc, nrow=main_hdu.n_rows)


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
            a = ms2hdu(file_in)
            a.export_hdf(file_out, compression=comp)
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






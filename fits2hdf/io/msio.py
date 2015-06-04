# -*- coding: utf-8 -*-
"""
msio.py
=========

MS I/O for reading and writing to MS files.
"""

import os

try:
    import pyrap.tables as pt
except ImportError:
    print("ERROR: could not load pyrap")
    print("This script requires pyrap to read and write MS files.")
    print("Please install casacore and pyrap, and re-run this script.")
    exit()

from fits2hdf.printlog import PrintLog
from fits2hdf.idi import IdiTableHdu, IdiHdulist, VerificationError

def get_size_ms(start_path='.'):
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
        hd = IdiTableHdu(name=hd)

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


def read_ms(infile, verbosity=1):
    """ Convert MS to a HDF file
    :param infile:  Measurement Set path
    :return: HDU version of Measurement Set
    """
    pp = PrintLog(verbosity=verbosity)
    ms = pt.table(infile)

    # Create a HDU List for storing HDUs
    hdul = IdiHdulist(verbosity=verbosity)

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

def export_ms(hdf_file, ms_file, verbosity=1):
    """ Convert an HDF file to MS
    :param hdf_file: Input HDF-MS filename
    :param ms_file: Output MS filename

    TODO: Get this working properly.
    """
    pp = PrintLog(verbosity=verbosity)
    hdul = IdiHdulist(verbosity=1)
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
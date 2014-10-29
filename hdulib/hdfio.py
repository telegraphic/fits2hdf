# -*- coding: utf-8 -*-
"""
fitsio.py
=========

FITS I/O for reading and writing to FITS files.
"""

import pyfits as pf
import numpy as np

try:
    from hdulib import idi
    from hdulib.idi import *
    from hdulib.printlog import PrintLog
except ImportError:
    import idi
    from idi import *
    from printlog import PrintLog

def read_hdf(infile, mode='r+', verbosity=0):
    """ Read and load contents of an HDF file """

    self = idi.IdiList(verbosity=verbosity)

    h = h5py.File(infile, mode=mode)
    self.pp.debug(h.items())

    # See if this is a HDFITS file. Raise warnings if not, but still try to read
    cls = "None"
    try:
        cls = h.attrs["CLASS"]
    except KeyError:
        self.pp.warn("No CLASS defined in HDF5 file.")
    if "HDFITS" not in cls:
        self.pp.warn("CLASS %s: Not an HDFITS file." % cls[0])

    for gname, group in h.items():
        self.pp.h2("Reading %s" % gname)

        if "HISTORY" in group["HEADER"].keys():
            history = group["HEADER"]["HISTORY"]
        else:
            history = None

        if "COMMENT" in group["HEADER"].keys():
            comment = group["HEADER"]["COMMENT"]
        else:
            comment = None

        header = group["HEADER"].attrs

        self.pp.pp(group.keys())
        if "DATA" not in group:
            hdu_type = "PRIMARY"
            self.pp.h3("Adding Primary %s" % gname)
            self.add_primary(gname)

        elif group["DATA"].attrs["CLASS"] == "TABLE":
            self.pp.h3("Adding Table %s" % gname)
            #self.add_table(gname)
            data = []

            for dname, dset in group["DATA"].items():
                self.pp.debug("Reading col %s > %s" %(gname, dname))

                #self[gname].data[dname] = dset[:]
                #self[gname].n_rows = dset.shape[0]
                try:
                    col_units = dset.attrs["UNITS"]
                except:
                    col_units = None
                col_num   = dset.attrs["COLUMN_ID"]

                idi_col = idi.IdiColumn(dname, dset[:], col_num, units=col_units)
                data.append(idi_col)

            self.add_table(gname,
                           header=header, data=data, history=history, comment=comment)

        elif group["DATA"].attrs["CLASS"] == "IMAGE":
            self.pp.h3("Adding Image %s" % gname)
            self.add_image(gname, data=group["DATA"][:])

        else:
            self.pp.warn("Cannot understand data class of %s" % gname)
        self.pp.debug(gname)
        self.pp.debug(self[gname].header)
        for hkey, hval in group["HEADER"].attrs.items():
            self[gname].header.vals[hkey] = hval

    h.close()

    return self


def export_hdf(self, outfile, compression=None, shuffle=False, chunks=None):
    """ Export to HDF file """

    h = h5py.File(outfile, mode='w')

    print outfile
    self.hdf = h

    self.hdf.attrs["CLASS"] = np.array(["HDFITS"])

    for gkey in self.keys():
        self.pp.h2("Creating %s" % gkey)
        gg = h.create_group(gkey)

        gg.attrs["CLASS"] = np.array(["HDU"])
        hg = gg.create_group("HEADER")

        if isinstance(self[gkey], IdiTable):

            #self.pp.verbosity = 5
            dg = gg.create_group("DATA")
            dg.attrs["CLASS"] = np.array(["TABLE"])
            for dkey, dval in self[gkey].data.items():

                data = dval.data
                if data.ndim != 2:
                    chunks = None
                self.pp.debug("Adding col %s > %s" % (gkey, dkey))

                try:
                    if compression == 'bitshuffle':
                        dset = bs.create_dataset(dg, dkey, data, chunks=chunks)

                    else:
                        dset = dg.create_dataset(dkey, data=data, compression=compression,
                                          shuffle=shuffle, chunks=chunks)

                    dset.attrs["CLASS"] = np.array(["COLUMN"])
                    dset.attrs["COLUMN_ID"] = np.array([dval.col_num])

                    if dval.units:
                        dset.attrs["UNITS"] = np.array([dval.units])


                except:
                    self.pp.err("%s > %s" % (gkey, dkey))
                    raise

        elif isinstance(self[gkey], IdiImage):
            self.pp.debug("Adding %s > DATA" % gkey)
            if compression == 'bitshuffle':
                dset = bs.create_dataset(gg, "DATA", self[gkey].data)
            else:
                dset = gg.create_dataset("DATA", data=self[gkey].data, compression=compression,
                                  shuffle=shuffle, chunks=chunks)

                # Add image-specific attributes
                dset.attrs["CLASS"] = np.array(["IMAGE"])
                dset.attrs["IMAGE_VERSION"] = np.array(["1.2"])
                if self[gkey].data.ndim == 2:
                    dset.attrs["IMAGE_SUBCLASS"] = np.array(["IMAGE_GRAYSCALE"])
                    dset.attrs["IMAGE_MINMAXRANGE"] = np.array([np.min(self[gkey].data), np.max(self[gkey].data)])

        elif isinstance(self[gkey], IdiPrimary):
            pass


        # Add header values
        for hkey, hval in self[gkey].header.vals.items():
            self.pp.debug("Adding header %s > %s" % (hkey, hval))
            hg.attrs[hkey] = np.array([hval])

        if self[gkey].header.comment:
            hg.create_dataset("COMMENT", data=self[gkey].header.comment)
        if self[gkey].header.history:
            hg.create_dataset("HISTORY", data=self[gkey].header.history)

    h.close()
# -*- coding: utf-8 -*-
"""
hdfio.py
=========

HDF I/O for reading and writing to HDF5 files.
"""

import pyfits as pf
import numpy as np
import h5py


from ..idi import *
from .. import idi

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

        # Form header dict from
        hk = group["HEADER"].attrs.keys()
        hv = group["HEADER"].attrs.values()
        h_vals = dict(zip(hk, hv))

        try:
            h_comment = group["HEADER"]["COMMENT"]
        except KeyError:
            h_comment = None
        try:
            h_history = group["HEADER"]["HISTORY"]
        except KeyError:
            h_history = None
        #header = IdiHeader(values=h_vals, comment=h_comment, history=h_history)
        #print header.vals.keys()

        self.pp.pp(group.keys())
        if "DATA" not in group:
            hdu_type = "PRIMARY"
            self.pp.h3("Adding Primary %s" % gname)
            self.add_primary(gname, header=h_vals, history=h_history, comment=h_comment)

        elif group["DATA"].attrs["CLASS"] == "TABLE":
            self.pp.h3("Adding Table %s" % gname)
            #self.add_table(gname)
            data = []

            col_num = 0
            for dname in group["DATA"].dtype.fields:
                self.pp.debug("Reading col %s > %s" %(gname, dname))

                dset = group["DATA"][dname][:]
                col_units = group["DATA"].attrs["FIELD_%i_UNITS" % col_num][0]
                #self[gname].data[dname] = dset[:]
                #self[gname].n_rows = dset.shape[0]

                idi_col = idi.IdiColumn(dname, dset[:], col_num, units=col_units)
                data.append(idi_col)
                col_num += 1

            self.add_table(gname,
                           header=h_vals, data=data, history=h_history, comment=h_comment)

        elif group["DATA"].attrs["CLASS"] == "DATA_GROUP":
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
                           header=h_vals, data=data, history=h_history, comment=h_comment)

        elif group["DATA"].attrs["CLASS"] == "IMAGE":
            self.pp.h3("Adding Image %s" % gname)
            self.add_image(gname,
                           header=h_vals, data=group["DATA"][:], history=h_history, comment=h_comment)

        else:
            self.pp.warn("Cannot understand data class of %s" % gname)
        self.pp.debug(gname)
        self.pp.debug(self[gname].header)
        #for hkey, hval in group["HEADER"].attrs.items():
        #    self[gname].header.vals[hkey] = hval

    h.close()

    return self


def export_hdf(self, outfile, compression=None, shuffle=False, chunks=None):
    """ Export to HDF file """

    h = h5py.File(outfile, mode='w')

    #print outfile
    self.hdf = h

    self.hdf.attrs["CLASS"] = np.array(["HDFITS"])

    for gkey in self.keys():
        self.pp.h2("Creating %s" % gkey)
        gg = h.create_group(gkey)

        gg.attrs["CLASS"] = np.array(["HDU"])
        hg = gg.create_group("HEADER")

        if isinstance(self[gkey], IdiTable):

            try:
                            #self.pp.verbosity = 5
                #dg = gg.create_group("DATA")

                dd = self[gkey].as_ndarray()

                if dd is not None:
                    if compression == 'bitshuffle':
                        dset = bs.create_dataset(gg, "DATA", dd, chunks=chunks)

                    else:
                        dset = gg.create_dataset("DATA", data=dd, compression=compression,
                                          shuffle=shuffle, chunks=chunks)
                    dset.attrs["CLASS"] = np.array(["TABLE"])

                    col_num = 0
                    for col_name in dd.dtype.names:

                        col_dtype = str(self[gkey].data[col_name].data.dtype)
                        col_units = self[gkey].data[col_name].units

                        if "|S" in col_dtype or "str" in col_dtype:
                            dset.attrs["FIELD_%i_FILL" % col_num] = np.array([''])
                        else:
                            dset.attrs["FIELD_%i_FILL" % col_num] = np.array([0])
                        dset.attrs["FIELD_%i_NAME" % col_num] = np.array([col_name])

                        dset.attrs["FIELD_%i_UNITS" % col_num] = np.array([str(col_units)])
                        col_num += 1

                    dset.attrs["NROWS"]   = np.array([dd.shape[0]])
                    dset.attrs["VERSION"] = np.array([2.6])     #TODO: Move this version no
                    dset.attrs["TITLE"]   = np.array([gkey])





            except:
                self.pp.err("%s" % gkey)
                raise

            #for dkey, dval in self[gkey].data.items():
            #
            #    data = dval.data
            #    if data.ndim != 2:
            #        chunks = None
            #    self.pp.debug("Adding col %s > %s" % (gkey, dkey))
            #
            #    try:
            #        if compression == 'bitshuffle':
            #            dset = bs.create_dataset(dg, dkey, data, chunks=chunks)
            #
            #        else:
            #            dset = dg.create_dataset(dkey, data=data, compression=compression,
            #                              shuffle=shuffle, chunks=chunks)
            #
            #        dset.attrs["CLASS"] = np.array(["COLUMN"])
            #        dset.attrs["COLUMN_ID"] = np.array([dval.col_num])
            #
            #        if dval.units:
            #            dset.attrs["UNITS"] = np.array([dval.units])
            #
            #
            #    except:
            #        self.pp.err("%s > %s" % (gkey, dkey))
            #        raise

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
        #print self[gkey].header
        for hkey, hval in self[gkey].header.vals.items():

            self.pp.debug("Adding header %s > %s" % (hkey, hval))
            hg.attrs[hkey] = np.array(hval)

        if self[gkey].header.comment:
            hg.create_dataset("COMMENT", data=self[gkey].header.comment)
        if self[gkey].header.history:
            hg.create_dataset("HISTORY", data=self[gkey].header.history)

    h.close()
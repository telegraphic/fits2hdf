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

    hdulist = idi.IdiHdulist()

    h = h5py.File(infile, mode=mode)

    pp = PrintLog(verbosity=verbosity)
    pp.debug(h.items())

    # See if this is a HDFITS file. Raise warnings if not, but still try to read
    cls = "None"
    try:
        cls = h.attrs["CLASS"]
    except KeyError:
        pp.warn("No CLASS defined in HDF5 file.")

    if "HDFITS" not in cls:
        pp.warn("CLASS %s: Not an HDFITS file." % cls[0])

    for gname, group in h.items():
        pp.h2("Reading %s" % gname)

        # Form header dict from
        hk = group.attrs.keys()
        hv = group.attrs.values()
        h_vals = dict(zip(hk, hv))

        try:
            h_comment = group["COMMENT"]
        except KeyError:
            h_comment = None
        try:
            h_history = group["HISTORY"]
        except KeyError:
            h_history = None
        #header = IdiHeader(values=h_vals, comment=h_comment, history=h_history)
        #print header.vals.keys()

        pp.pp(group.keys())
        if "DATA" not in group:
            hdu_type = "PRIMARY"
            pp.h3("Adding Primary %s" % gname)
            hdulist.add_primary_hdu(gname, header=h_vals, history=h_history, comment=h_comment)

        elif group["DATA"].attrs["CLASS"] == "TABLE":
            pp.h3("Adding Table %s" % gname)
            #self.add_table(gname)
            data = IdiTableHdu(gname)

            col_num = 0
            for dname in group["DATA"].dtype.fields:
                pp.debug("Reading col %s > %s" %(gname, dname))

                dset = group["DATA"][dname][:]
                col_units = group["DATA"].attrs["FIELD_%i_UNITS" % col_num][0]
                #self[gname].data[dname] = dset[:]
                #self[gname].n_rows = dset.shape[0]

                idi_col = idi.IdiColumn(dname, dset[:], unit=col_units)
                data.add_column(idi_col)
                col_num += 1

            hdulist.add_table_hdu(gname,
                           header=h_vals, data=data, history=h_history, comment=h_comment)

        elif group["DATA"].attrs["CLASS"] == "DATA_GROUP":
            pp.h3("Adding Table %s" % gname)
            #self.add_table(gname)
            data = []

            for dname, dset in group["DATA"].items():
                pp.debug("Reading col %s > %s" %(gname, dname))

                #self[gname].data[dname] = dset[:]
                #self[gname].n_rows = dset.shape[0]
                try:
                    col_units = dset.attrs["UNITS"]
                except:
                    col_units = None
                col_num   = dset.attrs["COLUMN_ID"]

                idi_col = idi.IdiColumn(dname, dset[:], col_num, units=col_units)
                data.append(idi_col)

            hdulist.add_table_hdu(gname,
                           header=h_vals, data=data, history=h_history, comment=h_comment)

        elif group["DATA"].attrs["CLASS"] == "IMAGE":
            pp.h3("Adding Image %s" % gname)
            hdulist.add_image_hdu(gname,
                           header=h_vals, data=group["DATA"][:], history=h_history, comment=h_comment)

        else:
            pp.warn("Cannot understand data class of %s" % gname)
        pp.debug(gname)
        pp.debug(hdulist[gname].header)
        #for hkey, hval in group["HEADER"].attrs.items():
        #    self[gname].header.vals[hkey] = hval

    h.close()

    return hdulist


def export_hdf(idi_hdu, outfile, compression=None, shuffle=False, chunks=None):
    """ Export to HDF file """

    h = h5py.File(outfile, mode='w')
    pp = PrintLog(verbosity=verbosity)

    #print outfile
    idi_hdu.hdf = h

    idi_hdu.hdf.attrs["CLASS"] = np.array(["HDFITS"])

    for gkey in idi_hdu.keys():
        pp.h2("Creating %s" % gkey)
        gg = h.create_group(gkey)

        gg.attrs["CLASS"] = np.array(["HDU"])
        #hg = gg.create_group("HEADER")

        if isinstance(idi_hdu[gkey], IdiTableHdu):

            try:
                            #self.pp.verbosity = 5
                #dg = gg.create_group("DATA")

                dd = idi_hdu[gkey].as_ndarray()

                if dd is not None:
                    if compression == 'bitshuffle':
                        dset = bs.create_dataset(gg, "DATA", dd, chunks=chunks)

                    else:
                        dset = gg.create_dataset("DATA", data=dd, compression=compression,
                                          shuffle=shuffle, chunks=chunks)
                    dset.attrs["CLASS"] = np.array(["TABLE"])

                    col_num = 0
                    for col_name in dd.dtype.names:

                        col_dtype = str(idi_hdu[gkey].data[col_name].data.dtype)
                        col_units = idi_hdu[gkey].data[col_name].units

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
                idi_hdu.pp.err("%s" % gkey)
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

        elif isinstance(idi_hdu[gkey], IdiImageHdu):
            idi_hdu.pp.debug("Adding %s > DATA" % gkey)
            if compression == 'bitshuffle':
                dset = bs.create_dataset(gg, "DATA", idi_hdu[gkey].data)
            else:
                dset = gg.create_dataset("DATA", data=idi_hdu[gkey].data, compression=compression,
                                  shuffle=shuffle, chunks=chunks)

                # Add image-specific attributes
                dset.attrs["CLASS"] = np.array(["IMAGE"])
                dset.attrs["IMAGE_VERSION"] = np.array(["1.2"])
                if idi_hdu[gkey].data.ndim == 2:
                    dset.attrs["IMAGE_SUBCLASS"] = np.array(["IMAGE_GRAYSCALE"])
                    dset.attrs["IMAGE_MINMAXRANGE"] = np.array([np.min(idi_hdu[gkey].data), np.max(idi_hdu[gkey].data)])

        elif isinstance(idi_hdu[gkey], IdiPrimaryHdu):
            pass

        # Add header values
        #print self[gkey].header
        for hkey, hval in idi_hdu[gkey].header.items():

            idi_hdu.pp.debug("Adding header %s > %s" % (hkey, hval))
            gg.attrs[hkey] = np.array(hval)

        if idi_hdu[gkey].header.comment:
            gg.create_dataset("COMMENT", data=idi_hdu[gkey].header.comment)
        if idi_hdu[gkey].header.history:
            gg.create_dataset("HISTORY", data=idi_hdu[gkey].header.history)

    h.close()
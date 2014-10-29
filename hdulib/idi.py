# -*- coding: utf-8 -*-
"""
idi.py
======

Abstract class for python Header-Data unit object. This is similar
to the HDU in FITS. Each HDU has a header dictionary and a data
dictionary. The data dictionary can be converted into a pandas
DataFrame object, and there are a few view / verify items also.
"""

import numpy as np
import pandas as pd
import h5py
import pyfits as pf
from datetime import datetime


from hdulib.printlog import PrintLog
import hdulib.hdfcompress as bs
from hdulib import fitsio

class VerificationError(Exception):
    """ Custom data verification exception """
    pass


class IdiHeader(object):
    """ Header unit for storing header information

    stores header dictionary and data dictionary

    name (str):    name of HDU
    header (dict): python dictionary of key:value pairs
    data   (dict): dictionary of key:value pairs, where data are stored
                   as numpy arrays

    """
    def __init__(self, header=None, comment=None, history=None, verbosity=0):
        self.vals   = {}
        self.history  = []
        self.comment  = []

        if header is not None:
            self.vals   = header
        if history is not None:
            self.history  = history
        if history is not None:
            self.comment = comment

        self.pp = PrintLog(verbosity=verbosity)

    def __repr__(self):
        return "IdiHeader: %s" % self.vals


class IdiPrimary(object):
    """ Header-data unit for storing table data

    stores header dictionary and data dictionary

    name (str):    name of HDU
    header (dict): python dictionary of key:value pairs
    data   (dict): dictionary of key:value pairs, where data are stored
                   as numpy arrays

    """
    def __init__(self, name, header=None, history=None, comment=None, verbosity=0):
        self.name   = name
        self.header = IdiHeader(header, comment, history)
        self.pp = PrintLog(verbosity=verbosity)

    def __repr__(self):
        return "IdiPrimary: %s" % self.name


class IdiImage(object):
    """ Header-data unit for storing table data

    stores header dictionary and data dictionary

    name (str):    name of HDU
    header (dict): python dictionary of key:value pairs
    data   (dict): dictionary of key:value pairs, where data are stored
                   as numpy arrays

    """
    def __init__(self, name, header=None, data=None, comment=None, history=None, verbosity=0):
        self.name   = name
        self.header = IdiHeader(header, comment, history)
        self.data   = np.array([0])
        self.n_rows = 0

        if data is not None:
            self.data = data


        self.pp = PrintLog(verbosity=verbosity)

    def __repr__(self):
        return "IdiImage: %s" % self.name


class IdiTable(object):
    """ Header-data unit for storing table data

    stores header dictionary and data dictionary

    name (str):    name of HDU
    header (dict): python dictionary of key:value pairs
    data   (dict): dictionary of key:value pairs, where data are stored
                   as numpy arrays

    """
    def __init__(self, name, header=None, data=None, comment=None, history=None, verbosity=0):
        self.name   = name
        self.header = IdiHeader(header, comment, history)
        self.data   = {}
        self.n_rows = 0
        self.n_cols = 0

        if data is not None:
            for col in data:
                self.n_cols += 1
                self.add_column(col)
            #self.data = data
            #self.n_rows = data[0][1].shape[0]

        self.pp = PrintLog(verbosity=verbosity)

    def __repr__(self):
        return "IdiTable: %s" % self.name

    def add_column(self, data, name='', dtype=None):
        """ Add a new column to the data unit

        name (str): name of column
        data (np.array or float): data for column. Defaults to
            a column of zeros. If a constant is given, then a
            column of said constant is produced. Alternatively
            pass a numpy array.
        dtype (str): Data type to use (ignored if an array is passed)
        """

        col_id = self.n_cols
        if isinstance(data, IdiColumn):
            name = data.name
            self.data[name] = data

        elif isinstance(data, np.ndarray):
            if name == '':
                raise RuntimeError("No column name supplied.")
            try:
                if len(self.data) == 0:
                    self.n_rows = data.shape[0]
                assert data.shape[0] == self.n_rows
            except AssertionError:
                msg = "Data len %i does not match n_rows %i" % (data.shape[0], self.n_rows)
                raise RuntimeError(msg)

            self.data[name] = IdiColumn(name, data, col_num=col_id)

        elif type(data) is list:
            self.data[name] = IdiColumn(name, np.array(data), col_num=col_id)

        elif type(data) is dict:
            pass

        elif data is None:
            pass

        else:
            if self.n_rows == 0:
                self.n_rows = 1
            if dtype is None:
                dtype = type(data)
            self.data[name] = IdiColumn(name, np.array([data] * self.n_rows, dtype=dtype), col_num=col_id)

    def verify(self):
        for key in self.data.keys():
            try:
                assert self.data[key].shape[0] == self.n_rows
            except:
                msg = "Column %s len %i does not match n_rows %i" % (key, self.data[key].shape[0], self.n_rows)
                raise AssertionError(msg)

    def as_dataframe(self):
        """ Read data as a pandas DataFrame, instead of dictionary of numpy arrays
        :return: pandas DataFrame of data
        """

        vals   = self.data.values()
        keys   = self.data.keys()
        dtypes = [str(x.dtype) for x in vals]
        shapes = [x.shape for x in vals]
        ndims  = [x.ndim  for x in vals]

        # Convert 2-dimensional to 1-dimensional struct
        ii = 0
        for ii in range(len(vals)):
            if ndims[ii] == 2:
                vals[ii] = vals[ii].view(dtype=[(keys[ii], dtypes[ii], shapes[ii][1])]).ravel()
            if ndims[ii] > 2:
                raise RuntimeError("NDIM of %s is too large") % keys[ii]

        dataframe = pd.DataFrame(dict(zip(keys, vals)))
        return dataframe


class IdiColumn(object):
    """ Column unit for storing columnular dataset

    stores header dictionary and data dictionary

    name (str):    name of HDU
    data:
    units:

    """
    def __init__(self, name, data, col_num, units=None, dtype=None):
        self.name   = name
        self.data   = data
        self.units  = units
        self.col_num = col_num

        if dtype:
            self.dtype = dtype
        else:
            self.dtype   = data.dtype

    def __repr__(self):
        uu = " " if self.units is None else self.units
        return "IdiColumn: %02i %16s %08s %s \n" % (self.col_num, self.name, self.dtype, uu)

class IdiList(dict):
    """ Header-Data Unit list (actually a dictionary) """

    def __init__(self, verbosity=0):
        super(IdiList, self).__init__()
        self.pp = PrintLog(verbosity=verbosity)

    def add_table(self, name, header=None, data=None, history=None, comment=None):
        """ Add HDu to HDU list"""
        self[name] = IdiTable(name, header=header, data=data,
                              history=history, comment=comment)

    def add_image(self, name, header=None, data=None, history=None, comment=None):
        self[name] = IdiImage(name, header=header, data=data,
                              history=history, comment=comment)

    def add_primary(self, name, header=None, history=None, comment=None):
        self[name] = IdiPrimary(name, header=header,
                                history=history, comment=comment)


    def print_headers(self):
        """ Print header info to screen """
        vtemp = self.pp.vlevel
        self.pp.vlevel = 5

        for key, hdu in self.items():
            self.pp.h2(key)
            for k, v in hdu.header.items():
                self.pp.pp("%16s    %s" %(k, v))
        self.pp.vlevel = vtemp

    def read_hdf(self, infile, mode='r+'):
        """ Read and load contents of an HDF file """

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

                    idi_col = IdiColumn(dname, dset[:], col_num, units=col_units)
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

    def read_fits(self, infile, mode='r+', verbosity=None):
        """ Read and load contents of a FITS file """
        if verbosity is None:
            verbosity = self.pp.vlevel
        else:
            self.pp.vlevel = verbosity

        self = fitsio.read_fits(infile, mode, verbosity)

    def export_fits(self, outfile):
        """ Export to FITS file """
        fitsio.export_fits(self, outfile)

def write_headers(hduobj, idiobj):
    """ copy headers over from idiobj to hduobj

    TODO: FITS header cards have to be written in correct order.
    TODO: Need to do this a little more carefully
    """

    for key, value in idiobj.header.vals.items():
        hduobj.header.update(key, value)

    for histline in idiobj.header.history:
        hduobj.header.add_history(histline)

    for commline in idiobj.header.comment:
        hduobj.header.add_comment(commline)

    hduobj.verify('fix')
    return hduobj

def parse_fits_header(hdu):
    """ Parse a FITS header into something less stupid """

    history  = []
    comment = []
    header   = {}

    hdu.verify('fix')

    for card in hdu.header.cards:

        card_id, card_val, card_comment = card
        card_id = card_id.strip()

        if card_id in (None, '', ' '):
            pass
        elif card_id == "HISTORY":
            history.append(card_val)
        elif card_id == "COMMENT":
            comment.append(card_val)
        else:
            header[card_id] = np.array([card_val, card_comment])

    return header, comment, history


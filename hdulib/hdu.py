# -*- coding: utf-8 -*-
"""
hdu.py
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

from hdulib.printlog import PrintLog
import hdulib.hdfcompress as bs

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

        if data is not None:
            self.data = data
            self.n_rows = data[data.keys()[0]].shape[0]

        self.pp = PrintLog(verbosity=verbosity)

    def __repr__(self):
        return "IdiTable: %s" % self.name

    def add_column(self, name, data=0, dtype=None):
        """ Add a new column to the data unit

        name (str): name of column
        data (np.array or float): data for column. Defaults to
            a column of zeros. If a constant is given, then a
            column of said constant is produced. Alternatively
            pass a numpy array.
        dtype (str): Data type to use (ignored if an array is passed)
        """

        if type(data) is type(np.array([0])):
            try:
                if len(self.data.keys()) == 0:
                    self.n_rows = data.shape[0]
                assert data.shape[0] == self.n_rows
            except AssertionError:
                msg = "Data len %i does not match n_rows %i" % (data.shape[0], self.n_rows)
                raise RuntimeError(msg)

            self.data[name] = data

        elif type(data) is list:
            self.data[name] = np.array(data)

        elif type(data) is dict:
            pass

        elif data is None:
            pass

        else:
            if self.n_rows == 0:
                self.n_rows = 1
            if dtype is None:
                dtype = type(data)
            self.data[name] = np.array([data] * self.n_rows, dtype=dtype)

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

        for gname, group in h.items():
            self.pp.h2("Reading %s" % gname)

            self.pp.pp(group.keys())
            if "DATA" not in group:
                hdu_type = "PRIMARY"
                self.pp.h3("Adding Primary %s" % gname)
                self.add_primary(gname)

            elif "XTENSION" in group["HEADER"].attrs.keys():
                hdu_type = group["HEADER"].attrs["XTENSION"]

                if hdu_type in ("BINTABLE", "TABLE"):
                    self.pp.h3("Adding Table %s" % gname)
                    self.add_table(gname)

                for dname, dset in group["DATA"].items():
                    self.pp.debug("Reading col %s > %s" %(gname, dname))
                    if dname == 'FLUX':
                        self[gname].data[dname] = dset[:,]
                    else:
                        self[gname].data[dname] = dset[:]
                    self[gname].n_rows = dset.shape[0]

            else:
                self.pp.h3("Adding Image %s" % gname)
                self.add_image(gname, data=group["DATA"][:])

            self.pp.debug(gname)
            self.pp.debug(self[gname].header)
            for hkey, hval in group["HEADER"].attrs.items():
                self[gname].header.vals[hkey] = hval

            if "HISTORY" in group["HEADER"].keys():
                self[gname].header.history = group["HEADER"]["HISTORY"]

            if "COMMENT" in group["HEADER"].keys():
                self[gname].header.comment = group["HEADER"]["COMMENT"]


        h.close()


    def export_hdf(self, outfile, compression=None, shuffle=False, chunks=None):
        """ Export to HDF file """

        h = h5py.File(outfile, mode='w')

        self.hdf = h

        for gkey in self.keys():
            self.pp.h2("Creating %s" % gkey)
            gg = h.create_group(gkey)
            hg = gg.create_group("HEADER")

            if isinstance(self[gkey], IdiTable):
                
                self.pp.verbosity = 5
                dg = gg.create_group("DATA")
                for dkey, dval in self[gkey].data.items():
                    if dval.ndim != 2:
                        chunks=None
                    self.pp.debug("Adding col %s > %s" % (gkey, dkey))
                    
                    try:
                        if compression == 'bitshuffle':
                            bs.create_dataset(dg, dkey, dval, chunks=chunks)
                            
                        else:
                            dg.create_dataset(dkey, data=dval, compression=compression,
                                              shuffle=shuffle, chunks=chunks)
                    except:
                        self.pp.err("%s > %s" % (gkey, dkey))
                        raise

            elif isinstance(self[gkey], IdiImage):
                self.pp.debug("Adding %s > DATA" % gkey)
                if compression == 'bitshuffle':
                    bs.create_dataset(gg, "DATA", self[gkey].data)
                else:
                    gg.create_dataset("DATA", data=self[gkey].data, compression=compression,
                                      shuffle=shuffle, chunks=chunks)

            elif isinstance(self[gkey], IdiPrimary):
                pass

            for hkey, hval in self[gkey].header.vals.items():
                self.pp.debug("Adding header %s > %s" % (hkey, hval))
                hg.attrs[hkey] = hval

            if self[gkey].header.comment:
                hg.create_dataset("COMMENT", data=self[gkey].header.comment)
            if self[gkey].header.history:
                hg.create_dataset("HISTORY", data=self[gkey].header.comment)

        h.close()

    def read_fits(self, infile, mode='r+'):
        """ Read and load contents of a FITS file """

        ff = pf.open(infile)
        self.fits = ff

        ii = 0
        for hdu in ff:
            if hdu.name in ('', None, ' '):
                hdu.name = "HDU%i" % ii
                ii += 1

            header, history, comment = self.parse_fits_header(hdu)
            
            ImageHDU   = pf.hdu.ImageHDU
            PrimaryHDU = pf.hdu.PrimaryHDU
            GroupsHDU  = pf.hdu.GroupsHDU
                                                 
            if isinstance(hdu, ImageHDU) or isinstance(hdu, PrimaryHDU):
                try:
                    if hdu.data is None:
                        self.add_primary(hdu.name,
                                         header=header, history=history, comment=comment)
                    else:
                        self.add_image(hdu.name, data=hdu.data[:],
                                       header=header, history=history, comment=comment)
                except TypeError:
                    # Primary groups HDUs can raise this error with no data
                    self.add_primary(hdu.name,
                                     header=header, history=history, comment=comment)                    

            elif isinstance(hdu, GroupsHDU):
                try:
                    data = hdu.data
                    self.add_table(hdu.name, data=hdu.data[:],
                                   header=header, history=history, comment=comment)
                except TypeError:
                    # Primary groups HDUs can raise this error with no data
                    self.add_primary(hdu.name,
                                     header=header, history=history, comment=comment)
            else:
                # Data is tabular
                data = {}
                for key in hdu.data.names:
                    data[key] = hdu.data[key][:]
                self.add_table(hdu.name,
                               header=header, data=data, history=history, comment=comment)

    def parse_fits_header(self, hdu):
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
                header[card_id] = card_val

        return header, comment, history

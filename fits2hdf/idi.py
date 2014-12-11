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

from fits2hdf.printlog import PrintLog


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
    """ Header-data unit for storing image data

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




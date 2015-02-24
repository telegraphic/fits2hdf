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
import six
from astropy.table import Table, Column, MaskedColumn
from astropy.nddata import NDData
from astropy.utils.metadata import MetaData
from ordereddict import OrderedDict
import pprint

from fits2hdf.printlog import PrintLog


class VerificationError(Exception):
    """ Custom data verification exception """
    pass


class IdiHeader(OrderedDict):
    """ Header unit for storing header information

    stores header dictionary and data dictionary

    name (str):    name of HDU
    header (dict): python dictionary of key:value pairs
    data   (dict): dictionary of key:value pairs, where data are stored
                   as numpy arrays

    """
    def __init__(self, values=None, verbosity=0):

        super(IdiHeader, self).__init__(values)

    def __repr__(self):
        to_print = ''
        for key, val in self.items():
            if not key.endswith('_COMMENT'):
                if len(key) < 8:
                    key = "%8s" % key

                if type(val) in [bool, float, int]:
                    val = "%32s" % val
                elif type(val) in [str, unicode]:
                    if len(val) < 32:
                        val = "%32s" % val
                comment_key = key + '_COMMENT'
                comment_val = self.get(comment_key)

                if comment_val is None:
                    comment_val = ''
                to_print += "%s %s   / %s\n" % (key, val, comment_val)
        return to_print

class IdiComment(list):
    """ Class for storing comments within a HDU
    """
    def __init__(self, comment=None):
        new_comment = comment
        if isinstance(comment, type(None)):
            new_comment = []
        elif type(comment) in (str, unicode):
            new_comment = [comment]

        super(IdiComment, self).__init__(new_comment)



    def __repr__(self):
        to_print = 'COMMENTS\n--------\n'
        for item in self:
            to_print += item + '\n'
        return to_print

class IdiHistory(IdiComment):
    """ Class for storing history within a HDU
    """
    def __init__(self, history):
        super(IdiHistory, self).__init__(history)

    def __repr__(self):
        to_print = 'HISTORY\n--------\n'
        for item in self:
            to_print += item + '\n'
        return to_print


class IdiPrimaryHdu(OrderedDict):
    """ Header-data unit for storing primary info

    name (str):    name of HDU
    header (dict): python dictionary of key:value pairs
    data   (dict): dictionary of key:value pairs, where data are stored
                   as numpy arrays

    """
    def __init__(self, name, header=None, history=None, comment=None):
        self.name   = name
        self.header  = IdiHeader(header)
        self.comment = IdiComment(comment)
        self.history = IdiHistory(history)

    def __repr__(self):
        return "IdiPrimary: %s" % self.name


class IdiImageHdu(NDData):
    """ Header-data unit for storing table data

    stores header dictionary and data dictionary

    name (str):    name of HDU
    header (dict): python dictionary of key:value pairs
    data   (dict): dictionary of key:value pairs, where data are stored
                   as numpy arrays

    """

    def __init__(self, *args, **kwargs):
        self.name = args[0]
        try:
            self.comment = IdiComment(kwargs.pop("comment"))
        except KeyError:
            self.comment = None
        try:
            self.history = IdiHistory(kwargs.pop("history"))
        except KeyError:
            self.history = None
        try:
            self.header = IdiHeader(kwargs.pop("header"))
        except KeyError:
            self.header = None
        super(IdiImageHdu, self).__init__(*args[1:], **kwargs)


class IdiTableHdu(Table):
    """ Header-data unit for storing table data


    Parameters
    ----------
    name : string
        Name of table. Required.
    data : numpy ndarray, dict, list, or Table, optional
        Data to initialize table.
    mask : numpy ndarray, dict, list, optional
        The mask to initialize the table
    names : list, optional
        Specify column names
    dtypes : list, optional
        Specify column data types
    meta : dict, optional
        Metadata associated with the table
    copy : boolean, optional
        Copy the input data (default=True).

    """
    def __init__(self, *args, **kwargs):
        self.name = args[0]

        try:
            self.comment = IdiComment(kwargs.pop("comment"))
        except KeyError:
            self.comment = None
        try:
            self.history = IdiHistory(kwargs.pop("history"))
        except KeyError:
            self.history = None
        try:
            self.header = IdiHeader(kwargs.pop("header"))
        except KeyError:
            self.header = IdiHeader()
        super(IdiTableHdu, self).__init__(*args[1:], **kwargs)

        # Add self.data item, which is missing in Table()
        self.data = self._data


class IdiColumn(Column):
    """ IDI version of astropy column"""
    def __init__(self, *args, **kwargs):
        self.name = args[0]
        #print self.name
        args = args[1:]
        super(IdiColumn, self).__init__(*args, **kwargs)

    def __new__(cls, name, data=None,
                dtype=None, shape=(), length=0,
                description=None, unit=None, format=None, meta=None, copy=False):

        if isinstance(data, MaskedColumn) and np.any(data.mask):
            raise TypeError("Cannot convert a MaskedColumn with masked value to a Column")

        self = super(IdiColumn, cls).__new__(cls, data=data, name=name, dtype=dtype,
                                          shape=shape, length=length, description=description,
                                          unit=unit, format=format, meta=meta)
        return self


class IdiHdulist(OrderedDict):
    """OrderedDict subclass for a dictionary of Header-data units (HDU).

    This is used as a container equivalent to the FITS HDUList.

    Credit
    ------
    Parts of this class are derived / copied from astropy.table
    http://www.astropy.org

    """

    def __getitem__(self, item):
        """Get items from a TableColumns object."""
        if isinstance(item, six.string_types):
            return OrderedDict.__getitem__(self, item)
        elif isinstance(item, int):
            return self.values()[item]
        elif isinstance(item, tuple):
            return self.__class__([self[x] for x in item])
        elif isinstance(item, slice):
            return self.__class__([self[x] for x in list(self)[item]])
        else:
            raise IndexError('Illegal key or index value for {} object'
                             .format(self.__class__.__name__))

    def __repr__(self):
        names = ("'{0}'".format(x) for x in six.iterkeys(self))
        return "<{1} names=({0})>".format(",".join(names), self.__class__.__name__)

    # Define keys and values for Python 2 and 3 source compatibility
    def keys(self):
        return list(OrderedDict.keys(self))

    def values(self):
        return list(OrderedDict.values(self))

    def add_table_hdu(self, name, header=None, data=None, history=None, comment=None):
        """ Add HDu to HDU list"""
        self[name] = IdiTableHdu(name, header=header, data=data,
                              history=history, comment=comment)

    def add_image_hdu(self, name, header=None, data=None, history=None, comment=None):
        self[name] = IdiImageHdu(name, header=header, data=data,
                              history=history, comment=comment)

    def add_primary_hdu(self, name, header=None, history=None, comment=None):
        self[name] = IdiPrimaryHdu(name, header=header,
                                history=history, comment=comment)



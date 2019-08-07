# -*- coding: utf-8 -*-
"""
idi.py
======

Abstract classes for python Header-Data unit object. This is similar
to the HDU in FITS. Each HDU has a header dictionary and a data
dictionary. The data dictionary can be converted into a pandas
DataFrame object, and there are a few view / verify items also.

"""

import numpy as np
import six
from astropy.table import Table, Column, MaskedColumn
from astropy.nddata import NDData
from collections import OrderedDict


class VerificationError(Exception):
    """ Custom data verification exception """
    pass


class IdiHeader(OrderedDict):
    """
    Header unit for storing header information

    This object stores a header dictionary. For FITS files, order
    is important (particularly for HISTORY cards); but HDF5 does
    not assign any ordering to attributes. As such, order may be lost
    in translation between the two formats.

    Comments should be passed to this object as dictionary entries with
    keys key_COMMENT, e.g. CARD1: 1.20, CARD1_COMMENT: 'Example entry'

    Parameters
    ----------
    values: dict
        Dictionary of header keyword : value pairs.
    """
    def __init__(self, values=None):

        if values is not None:
            super(IdiHeader, self).__init__(values)
        else:
            super(IdiHeader, self).__init__()

    def __repr__(self):
        to_print = ''
        for key, val in self.items():
            if not key.endswith('_COMMENT'):
                if len(key) < 8:
                    key = "%8s" % key

                if type(val) in [bool, float, int]:
                    val = "%32s" % val
                elif isinstance(val, six.text_type):
                    if len(val) < 32:
                        val = "%32s" % val
                comment_key = key + '_COMMENT'
                comment_val = self.get(comment_key)

                if comment_val is None:
                    comment_val = ''
                to_print += "%s %s   / %s\n" % (key, val, comment_val)
        return to_print

class IdiComment(list):
    """
    Class for storing comments within a HDU

    This stores comments as a list of strings. The FITS 'COMMENT'
    keyword should be stripped, and only the actual comment should
    be passed.

    Parameters
    ----------
    comment: list, string, or None
        Comment values to be used in initialization (more can be added
        later by using the append method / other list methods).
    """
    def __init__(self, comment=None):
        new_comment = comment
        if isinstance(comment, type(None)):
            new_comment = []
        elif isinstance(comment, six.text_type):
            new_comment = [comment]

        super(IdiComment, self).__init__(new_comment)

    def __repr__(self):
        to_print = 'COMMENTS\n--------\n'
        for item in self:
            to_print += item + '\n'
        return to_print

class IdiHistory(IdiComment):
    """
    Class for storing history within a HDU

    This stores history log notes as a list of strings. The FITS 'HISTORY'
    keyword should be stripped and only actual history log should be passed.

    Parameters
    ----------
    history: list, string, or None
        Comment values to be used in initialization (more can be added
        later by using the append method / other list methods).
    """
    def __init__(self, history):
        super(IdiHistory, self).__init__(history)

    def __repr__(self):
        to_print = 'HISTORY\n--------\n'
        for item in self:
            to_print += item + '\n'
        return to_print


class IdiPrimaryHdu(OrderedDict):
    """
    Header-data unit for storing PRIMARY metadata

    This is used for storing the FITS / HDFITS PRIMARY HDU, where
    there is NO data payload. Otherwise, the IdiImageHdu should be
    used.

    Parameters
    ----------
    name : string
        Name of HDU. Required.
    comment : list
        List of comments. Optional
    history : list
        List of history entries. Optional
    header: dict
        Header dictionary of keyword:value pairs. Optional
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

    Parameters
    ----------
    name : string
        Name of HDU. Required.
    comment : list
        List of comments. Optional
    history : list
        List of history entries. Optional
    header: dict
        Header dictionary of keyword:value pairs. Optional
    data: dict
        dictionary of key:value pairs, where data are stored
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

    This subclasses the astropy.table Table() class.
    It attaches comments, history and a header to make
    it a "HDU", instead of just a Table

    Parameters
    ----------
     name : string
        Name of HDU. Required.
    comment : list
        List of comments. Optional
    history : list
        List of history entries. Optional
    header: dict
        Header dictionary of keyword:value pairs. Optional
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

        # # Add self.data item, which is missing in Table()
        # self.data = None


class IdiColumn(Column):
    """ IDI version of astropy.table Column()

    This subclasses the astropy.table Column() class, to provide an equivalent
    comment object for IDI data conversion. This subclass adds the ability to
    name the column

    Parameters
    ----------
    name: string
        name of column. This is a required argument for IdiColumn, and must be
        the first argument.
        Column name and key for reference within Table
    data : list, ndarray or None
        Column data values
    dtype : numpy.dtype compatible value
        Data type for column
    shape : tuple or ()
        Dimensions of a single row element in the column data
    length : int or 0
        Number of row elements in column data
    description : str or None
        Full description of column
    unit : str or None
        Physical unit
    format : str or None or function or callable
        Format string for outputting column values. This can be an “old-style”
        (format % value) or “new-style” (str.format) format specification
        string or a function or any callable object that accepts a single value
        and returns a string.
    meta : dict-like or None
        Meta-data associated with the column
    """
    # def __init__(self, *args, **kwargs):
    #     self.name = args[0]
    #     args = args[1:]
    #     super(IdiColumn, self).__init__(*args, **kwargs)

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

    This is used as a container equivalent to the FITS HDUList. This can
    be initialized with no arguments, then HDUs may be appended to it
    using regular ordered dict methods

    Parameters
    ----------
    dict_data: dict
        This class can be initialized with zero arguments, or you can pass
        a python-style dictionary.
    """

    def __getitem__(self, item):
        """Get items from a TableColumns object."""
        if isinstance(item, six.string_types):
            try:
                return OrderedDict.__getitem__(self, item)
            except KeyError:
                try:
                    return OrderedDict.__getitem__(self, item.lower())
                except KeyError:
                    return OrderedDict.__getitem__(self, item.upper())

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
        """
        Add a Table HDU to HDU list

        Parameters
        ----------
        name: str
            Name for table HDU
        header=None: dict
            Header keyword:value pairs dictionary. optional
        data=None: IdiTableHdu
            IdiTableHdu that contains the data
        history=None: list
            list of history data
        comment=None: list
            list of comments
        """
        self[name] = IdiTableHdu(name, header=header, data=data,
                              history=history, comment=comment)

    def add_image_hdu(self, name, header=None, data=None, history=None, comment=None):
        """
        Add a Image HDU to HDU list

        Parameters
        ----------
        name: str
            Name for table HDU
        header=None: dict
            Header keyword:value pairs dictionary. optional
        data=None: np.ndarray or equivalent
            Array that contains the image data
        history=None: list
            list of history data
        comment=None: list
            list of comments
        """
        self[name] = IdiImageHdu(name, header=header, data=data,
                              history=history, comment=comment)

    def add_primary_hdu(self, name, header=None, history=None, comment=None):
        """
        Add a Primary HDU to HDU list. This should not have a data payload.

        Parameters
        ----------
        name: str
            Name for table HDU
        header=None: dict
            Header keyword:value pairs dictionary. optional
        history=None: list
            list of history data
        comment=None: list
            list of comments
        """
        self[name] = IdiPrimaryHdu(name, header=header,
                                history=history, comment=comment)

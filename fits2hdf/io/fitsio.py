# -*- coding: utf-8 -*-
"""
fitsio.py
=========

FITS I/O for reading and writing to FITS files.
"""

from astropy.io import fits as pf
from astropy.io.fits.verify import VerifyWarning
from astropy.units import Unit, UnrecognizedUnit
import numpy as np
from datetime import datetime
import warnings

from ..idi import *
from .. import idi
from .. import unit_conversion
from ..printlog import PrintLog

# A list of keywords that are mandatory to FITS, but should always be calculated
# By the writing program from the data model, and should not be written to HDF5
restricted_header_keywords = {"XTENSION", "BITPIX", "SIMPLE", "PCOUNT", "GCOUNT",
                              "GROUPS", "EXTEND", "TFIELDS", "EXTNAME"}
restricted_table_keywords = {"TDISP", "TUNIT", "TTYPE", "TFORM", "TBCOL",
                             "TNULL", "TSCAL", "TZERO", "NAXIS"}


class DeprecatedGroupsHDUWarning(VerifyWarning):
    """
    Warning message when a deprecated 'group HDU' is found
    """

def fits_format_code_lookup(numpy_dtype, numpy_shape):
    """ Return a FITS format code from a given numpy dtype

    Parameters
    ----------
    numpy_dtype: a numpy dtype object
        Numpy dtype to lookup
    numpy_shape: tuple
        shape of data array to be converted into a FITS format

    Returns
    -------
    fmt_code: string
        FITS format code, e.g. 8A for character string of length 8
    fits_dim: string or None
        Returns fits dimension for TDIM keyword

    Notes
    -----

    FITS format code         Description                     8-bit bytes
    --------------------------------------------------------------------
    L                        logical (Boolean)               1
    X                        bit                             *
    B                        Unsigned byte                   1
    I                        16-bit integer                  2
    J                        32-bit integer                  4
    K                        64-bit integer                  4
    A                        character                       1
    E                        single precision floating point 4
    D                        double precision floating point 8
    C                        single precision complex        8
    M                        double precision complex        16
    P                        array descriptor                8
    Q                        array descriptor                16
    """

    np_type = numpy_dtype.type


    # Get length of array last axis
    fmt_len = 1
    if len(numpy_shape) > 1:
        for ii in numpy_shape[1:]:
            fmt_len *=  ii
        #fmt_len = numpy_shape[-1]
    else:
        fmt_len = 1

    if np_type is np.string_ or "string" in str(np_type):
        fits_dim = None
        if numpy_dtype.itemsize == 1:
            fits_fmt = "A"
        else:
            fits_fmt = '%iA' % numpy_dtype.itemsize
        return fits_fmt, fits_dim

    else:
        #TODO: handle special case of uint16,32,64, requires BZERO / scale
        dtype_dict = {
            np.uint8:   'B',
            np.uint16:  'J',    # No native FITS equivalent
            np.uint32:  'K',
            np.uint64:  'K',
            np.int8:    'I',    # No native FITS equivalent
            np.int16:   'I',
            np.int32:   'J',
            np.int64:   'K',
            np.float16: 'E',    # No native FITS equivalent
            np.float32: 'E',
            np.float64: 'D',
            np.complex64: 'C',
            np.complex128: 'M',
            np.bool_:      'L'
        }

        fmt_code = dtype_dict.get(np_type)

        if fmt_len > 1:
            fmt_code = "%i%s" % (fmt_len, fmt_code)

        if len(numpy_shape) == 1:
            fits_dim = None
        else:
            #NOTE: Needs to be flipped to be FORTRAN order
            # From FITS spec: The value field of this indexed keyword shall contain a
            # character string describing how to interpret the contents of field n as
            # a multi-dimensional array with a format of “(l, m, n ...)” where l, m, n, ...
            # are the dimensions of the array. The data are ordered such that the array index
            # of the first dimension given (l) is the most rapidly varying and that of the last
            # dimension given is the least rapidly varying.
            fits_dim = str(numpy_shape[1:][::-1])

        return fmt_code, fits_dim

def numpy_dtype_lookup(numpy_dtype):
    """
    Return the local OS datatype for a given dtype

    Notes
    -----
    This is added to workaround a bug in binary table writing,
    whereby an additional byteswap is done that is unnecessary.

    Parameters
    ----------
    numpy_dtype: numpy.dtype
        Numpy datatype

    Returns
    -------
    numpy_local_dtype: numpy.dtype
        Local numpy datatype
    """

    np_type = numpy_dtype.type

    dtype_dict = {
            np.uint8:   'uint8',
            np.uint16:  'uint16',    # No native FITS equivalent
            np.uint32:  'uint32',
            np.uint64:  'uint64',
            np.int8:    'int8',    # No native FITS equivalent
            np.int16:   'int16',
            np.int32:   'int32',
            np.int64:   'int64',
            np.float16: 'float16',    # No native FITS equivalent
            np.float32: 'float32',
            np.float64: 'float64',
            np.complex64: 'complex64',
            np.complex128: 'complex128',
            np.bool_:      'bool',
            np.string_:    'str'
        }

    new_dtype = np.dtype(dtype_dict.get(np_type))
    return new_dtype

def write_headers(hduobj, idiobj):
    """ copy headers over from idiobj to hduobj.

    Need to skip values that refer to columns (TUNIT, TDISP), as
    these are necessarily generated by the table creation

    Parameters
    ----------
    hduobj: astropy FITS HDU (ImageHDU, BintableHDU)
        FITS HDU to which to write header values
    idiobj: IdiImageHdu, IdiTableHdu, IdiPrimaryHdu
        HDU object from which to copy headers from
    verbosity: int
        Level of verbosity, none (0) to all (5)
    """

    header_obj = hduobj
    if not isinstance(hduobj, pf.Header):
        header_obj = hduobj.header

    for key, value in idiobj.header.items():

        try:
            comment = idiobj.header[key+"_COMMENT"]
        except:
            comment = ''

        is_comment = key.endswith("_COMMENT")
        is_table   = key[:5] in restricted_table_keywords
        is_table = is_table or key[:4] == "TDIM" or key == "TFIELDS"

        is_basic = key in restricted_header_keywords
        if is_comment or is_table or is_basic:
            pass
        else:
            header_obj[key] = (value, comment)

    for histline in idiobj.history:
        header_obj.add_history(histline)

    for commline in idiobj.comment:
        header_obj.add_comment(commline)

    if not isinstance(hduobj, pf.Header):
        hduobj.verify('fix')
    return hduobj

def parse_fits_header(hdul):
    """ Parse a FITS header into something less stupid.

    Parameters
    ----------
    hdul: HDUList
        FITS HDUlist from which to parse the header

    Notes
    -----
    This function takes a fits HDU object and returns:
    header (dict): Dictionary of header values. Header comments
                   are written to [CARDNAME]_COMMENT
    comment (list): Comment cards are parsed and then put into list
                    (order is important)
    history (list): History cards also parsed into a list
    """

    history  = []
    comment = []
    header   = {}

    hdul.verify('fix')

    for card in hdul.header.cards:

        card_id, card_val, card_comment = card
        card_id = card_id.strip()
        comment_id = card_id + "_COMMENT"

        if card_id in (None, '', ' '):
            pass
        elif card_id in restricted_header_keywords:
            pass
        elif card_id[:5] in restricted_table_keywords:
            pass
        elif card_id == "HISTORY":
            history.append(card_val)
        elif card_id == "COMMENT":
            comment.append(card_val)
        else:
            header[card_id] = card_val
            header[comment_id] = card_comment

    return header, comment, history


def create_column(col):
    """
    Create a astropy.io.fits column object from IdiColumn

    This is a helper function that automatically computes a few things
    that should be obvious from the numpy data type and shape, but that
    the fits.column object needs to have set explicitly.

    This fills in format, dim, and array keywords.
    Unit and null are left as keyword arguments.
    Bscale, bzero, disp, start, and ascii are NOT supported.

    Parameters
    ----------
    col: IdiColumn
        IdiColumn object that contains the data array

    Returns
    -------
    fits_col: pf.Column
        astropy.io.fits column
    """
    name = col.name
    fits_fmt, fits_dim = fits_format_code_lookup(col.dtype, col.shape)
    fits_unit = unit_conversion.units_to_fits(col.unit)
    local_type = numpy_dtype_lookup(col.data.dtype)
    data = col.data.astype(local_type)

    fits_col = pf.Column(name=name, format=fits_fmt, unit=fits_unit,
                         array=data, dim=fits_dim)

    return fits_col



def read_fits(infile, verbosity=0):
    """
    Read and load contents of a FITS file

    Parameters
    ----------
    infile: str
        File path of input file
    verbosity: int
        Verbosity level of output, 0 (none) to 5 (all)
    """

    pp = PrintLog(verbosity=verbosity)
    ff = pf.open(infile)


    hdul_idi = idi.IdiHdulist()

    hdul_idi.fits = ff

    ii = 0
    for hdul_fits in ff:
        if hdul_fits.name in ('', None, ' '):
            hdul_fits.name = "HDU%i" % ii
            ii += 1

        header, history, comment = parse_fits_header(hdul_fits)

        ImageHDU   = pf.hdu.ImageHDU
        PrimaryHDU = pf.hdu.PrimaryHDU
        compHDU    = pf.hdu.CompImageHDU
        groupsHDU  = pf.hdu.groups.GroupsHDU

        if isinstance(hdul_fits, ImageHDU) or isinstance(hdul_fits, PrimaryHDU):
            pp.debug("Adding Image HDU %s" % hdul_fits)
            try:
                if isinstance(hdul_fits, groupsHDU):
                    # We have a random group table, yuck
                    hdul_idi.add_table_hdu(hdul_fits.name, data=hdul_fits.data[:],
                                           header=header, history=history, comment=comment)
                elif hdul_fits.size == 0:
                    hdul_idi.add_primary_hdu(hdul_fits.name,
                                              header=header, history=history, comment=comment)
                elif hdul_fits.is_image:
                    hdul_idi.add_image_hdu(hdul_fits.name, data=hdul_fits.data[:],
                                           header=header, history=history, comment=comment)
                else:
                    # We have a random group table, yuck
                    hdul_idi.add_table_hdu(hdul_fits.name, data=hdul_fits.data[:],
                                           header=header, history=history, comment=comment)
            except TypeError:
                # Primary groups HDUs can raise this error with no data
                hdul_idi.add_primary_hdu(hdul_fits.name,
                                         header=header, history=history, comment=comment)

        elif isinstance(hdul_fits, compHDU):
            pp.debug("Adding Compressed Image HDU %s" % hdul_fits)
            hdul_idi.add_image_hdu(hdul_fits.name, data=hdul_fits.data[:],
                                   header=header, history=history, comment=comment)
        else:
            pp.debug("Adding Tablular HDU %s" % hdul_fits)
            # Data is tabular
            tbl_data = Table.read(infile, hdu=hdul_fits.name)
            idi_tbl = IdiTableHdu(hdul_fits.name, tbl_data)
            hdul_idi.add_table_hdu(hdul_fits.name,
                                   header=header, data=idi_tbl, history=history, comment=comment)

    return hdul_idi

def create_fits(hdul, verbosity=0):
    """
    Export HDU to FITS file in memory.

    Returns an in-memory HDUlist, does not write to file.

    Parameters
    ----------
    hdul: IdiHduList
        An IDI HDU list object to convert into a pyfits /
        astropy HDUlist() object in memory
    verbosity: int
        verbosity level, 0 (none) to 5 (all)
    """
    pp = PrintLog(verbosity=verbosity)
    # Create a new hdulist
    hdulist = pf.HDUList()


    for name, idiobj in hdul.items():
        pp.debug("%s %s" % (name, idiobj))

        if isinstance(idiobj, IdiPrimaryHdu):
            pp.pp("Creating Primary HDU %s" % idiobj)
            new_hdu = pf.PrimaryHDU()
            new_hdu = write_headers(new_hdu, idiobj)
            hdulist.insert(0, new_hdu)

        elif isinstance(idiobj, IdiImageHdu):
            pp.pp("Creating Image HDU %s" % idiobj)
            if name == "PRIMARY":
                new_hdu = pf.PrimaryHDU()
                new_hdu = write_headers(new_hdu, idiobj)
                try:
                    new_hdu.data = idiobj.data
                    hdulist.insert(0, new_hdu)
                except KeyError:
                    print(idiobj)
                    #print new_hdu
                    raise
            else:
                new_hdu = pf.ImageHDU()
                new_hdu = write_headers(new_hdu, idiobj)
                new_hdu.data = idiobj.data
                new_hdu.name = name
                hdulist.append(new_hdu)

        elif isinstance(idiobj, IdiTableHdu):
            if idiobj.name == "PRIMARY":
                pp.warn("Groups HDU has been converted to a binary table")
                warnings.warn("PRIMARY GroupsHDU has been converted to a binary table", DeprecatedGroupsHDUWarning)
                idiobj.name = "PRIDATA"
                name = idiobj.name
                #hdulist.append(pf.PrimaryHDU())

            pp.pp("Creating Table HDU %s" % idiobj)
            fits_cols = []
            for cn in idiobj.colnames:
                col = idiobj[cn]
                fits_col = create_column(col)
                pp.debug(col.data.shape)

                fits_cols.append(fits_col)

            table_def = pf.ColDefs(fits_cols)
            pp.pp(table_def)
            print(table_def)

            new_hdu = pf.BinTableHDU.from_columns(table_def, name=idiobj.name)
            new_hdu = write_headers(new_hdu, idiobj)
            new_hdu.name = name
            new_hdu.verify()
            #print new_hdu.name, idiobj.name
            hdulist.append(new_hdu)
            hdulist.verify()

    now = datetime.now()
    now_str = now.strftime("%Y-%M-%dT%H:%M")
    hdulist[0].header.add_history("%s File written by fits2hdf" %now_str)
    return hdulist



def export_fits(hdul, outfile, verbosity=0):
    """
    Export HDU list to file

    Parameters
    ----------
    hdul: IdiHduList
        HDU list to write to file
    outfile: str
        Filename of ourput file
    verbosity: int
        verbosity of output, 0 (none) to 5 (all)
    """
    fits_hdulist = create_fits(hdul, verbosity=verbosity)
    # Write to file
    fits_hdulist.writeto(outfile, checksum=True, output_verify='fix')

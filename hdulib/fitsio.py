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
except ImportError:
    import idi
    from idi import *

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

def parse_fits_header(hdul):
    """ Parse a FITS header into something less stupid """

    history  = []
    comment = []
    header   = {}

    hdul.verify('fix')

    for card in hdul.header.cards:

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


def read_fits(infile, mode='r+', verbosity=0):
    """ Read and load contents of a FITS file """

    ff = pf.open(infile)

    self = idi.IdiList(verbosity=verbosity)

    self.fits = ff

    ii = 0
    for hdul in ff:
        if hdul.name in ('', None, ' '):
            hdul.name = "HDU%i" % ii
            ii += 1

        header, history, comment = parse_fits_header(hdul)

        ImageHDU   = pf.hdu.ImageHDU
        PrimaryHDU = pf.hdu.PrimaryHDU
        compHDU    = pf.hdu.CompImageHDU

        if isinstance(hdul, ImageHDU) or isinstance(hdul, PrimaryHDU):
            try:
                if hdul.size == 0:
                    self.add_primary(hdul.name,
                                     header=header, history=history, comment=comment)
                elif hdul.is_image:
                    self.add_image(hdul.name, data=hdul.data[:],
                                   header=header, history=history, comment=comment)
                else:
                    # We have a random group table, yuck
                    self.add_table(hdul.name, data=hdul.data[:],
                                   header=header, history=history, comment=comment)
            except TypeError:
                # Primary groups HDUs can raise this error with no data
                self.add_primary(hdul.name,
                                 header=header, history=history, comment=comment)
        elif isinstance(hdul, compHDU):
            self.add_image(hdul.name, data=hdul.data[:],
                           header=header, history=history, comment=comment)
        else:
            # Data is tabular
            data = []
            col_num = 1
            for key in hdul.data.names:
                col_units = None
                try:
                    col_units = hdul.header["TUNIT%i" % col_num]
                    #print col_units
                except KeyError:
                    pass
                idi_col = idi.IdiColumn(key, hdul.data[key][:], col_num, units=col_units)
                data.append(idi_col)
                col_num += 1
            self.add_table(hdul.name,
                           header=header, data=data, history=history, comment=comment)


    return self

def export_fits(self, outfile):
    """ Export to FITS file """

    # Create a new hdulist
    hdulist = pf.HDUList()

    # Create a new hdu for every item in IdiList
    for name, idiobj in self.items():
        print name, idiobj

        if isinstance(idiobj, IdiPrimary):
                hdu = pf.PrimaryHDU()
                hdu = write_headers(hdu, idiobj)
                hdulist.insert(0, hdu)

        elif isinstance(idiobj, IdiImage):
            if name == "PRIMARY":
                hdu = pf.PrimaryHDU()
                hdu = write_headers(hdu, idiobj)
                hdu.data = idiobj.data
                hdulist.insert(0, hdu)
            else:
                hdu = pf.ImageHDU()
                hdu.name = name

        elif isinstance(idiobj, IdiTable):
            # Need special care in case it is a random group
            pass

    # Add creation info to history
    now = datetime.now()
    now_str = now.strftime("%Y-%M-%dT%H:%M")
    hdulist[0].header.add_history("File written by fits2hdf %s" %now_str)

    # Write to file
    hdulist.writeto(outfile)

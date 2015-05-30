# -*- coding: utf-8 -*-
"""
unit_conversion.py
==================

Functions for checking and sanitizing units that do not follow the FITS specification.
This uses functions from ``astropy.unit`` to parse and handle units.
"""

import warnings
from astropy.units import Unit, UnrecognizedUnit
from astropy.io.fits.verify import VerifyWarning


class UnitWarning(VerifyWarning):
    """
    Unit warning class

    Used when units do not parse or parse oddly
    """


def fits_to_units(unit_str):
    """ Do a lookup from a astropy unit and return a fits unit string

    unit_str (str): a FITS unit string
    returns an astropy.units.Unit(), or UnrecognizedUnit()

    Notes
    -----
    This will attempt to correct some common mistakes in the FITS format.
    """
    unit_lookup = {
        'meters':  'm',
        'meter':   'm',
        'degrees': 'deg',
        'degree':  'deg',
        'hz': 'Hz',
        'hertz': 'Hz',
        'second': 's',
        'sec': 's',
        'secs': 's',
        'days': 'd',
        'day': 'd',
        'steradians': 'sr',
        'steradian': 'sr',
        'radians': 'rad',
        'radian': 'rad',
        'jy': 'Jy',
        'au': 'AU',
    }

    try:
        new_units = ""

        if unit_str is None:
            unit_str = ''
        unit_str = unit_str.lower()
        unit_list = unit_str.split("/")

        for uu in unit_list:
            if uu.endswith("s") and len(uu) > 1:
                uu = uu[:-1]
            corrected_unit = unit_lookup.get(uu, uu)
            new_units += corrected_unit
            new_units += " / "
        new_units = new_units[:-3]
        unit = Unit(new_units)
        return unit

    except ValueError:
        warnings.warn("Unknown unit: %s" % new_units, UnitWarning)
        return UnrecognizedUnit(unit_str)


def units_to_fits(unit):
    """ Convert an astropy unit to a FITS format string.

    uses the to_string() method built-in to astropy Unit()

    Notes
    -----
    The output will be the format defined in the FITS standard:
    http://fits.gsfc.nasa.gov/fits_standard.html

    A roundtrip from fits_to_units -> units_to_fits may not return
    the original string, as people often don't follow the standard.
    """
    if unit is None:
        unit = Unit('')
    return unit.to_string("fits").upper()

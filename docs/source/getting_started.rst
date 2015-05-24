.. fits2hdf documentation master file, created by
   sphinx-quickstart on Fri May 22 16:29:56 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Getting started
===============

Installation
------------

To install, you first need to clone the directory from github::

    git clone https://github.com/telegraphic/fits2hdf

and then run::

    python setup.py install
    
from the command line. You'll need 
`astropy <http://www.astropy.org/>`_ and `h5py <http://www.h5py.org/>`_ to be installed. If you want to
use `bitshuffle <https://github.com/kiyo-masui/bitshuffle>`_ compression (good for radio astronomy data), you'll need to install that too.

Installation through ``pip`` will likely be added in the future.

Command line usage
------------------

To use ``fits2hdf`` to convert FITS files to HDF5, use the `fits2hdf.py` script::

    python fits2hdf.py input_dir output_dir <options>

Optional arguments are:
  -h, --help            show this help message and exit
  -c COMP, --compression=COMP
                        Data compression algorithm: None, lzf,
                        gzip and bitshuffle (if installed). 
  -x EXT, --extension=EXT
                        File extension of FITS files. Defaults to .fits
  -v VERBOSITY, --verbosity=VERBOSITY
                        verbosity level (default 0, up to 5)
  -s SCALE_OFFSET, --scaleoffset=SCALE_OFFSET
                        Add scale offset (HDF5 compression option). NB: this can be
                        lossy!
  -S, --shuffle         Apply byte shuffle filter (HDF5 compression option)
  -C, --checksum        Compute fletcher32 checksum on datasets.


To convert back into FITS, run ``hdf2fits.py``, which uses similar options::

    python fits2hdf.py input_dir output_dir <options>

As many HDF5 features don't have equivalents in FITS, this will (probably) only work for HDFITS files.

Quickly adding HDF5 support in Python
-------------------------------------

If you have an existing program and want to quickly be able to read HDFITS files, just change your::

    from astropy.io import fits
    
line to::

    from fits2hdf import pyhdfits as fits

Or, if you're using pyfits, change your ``import pyfits as pf`` line to  
``from fits2hdf import pyhdfits as pf``.

By doing this, any data in HDFITS will be converted to the PyFITS/ Astropy HDUList object on the fly.

Loading HDFITS files in python
------------------------------

Functions to read / write HDFITS files into an in-memory data object in python are located in 
``fits2hdf.io.hdfio``. There are equivalent functions to read FITS files into an interchange 
format in ``fits2hdf.io.fitsio``.

For example, to read a FITS file in, then export it to HDFITS you would do::

    from fits2hdf.io.fitsio import read_fits
    from fits2hdf.io.hdfio import export_hdf
    a = read_fits('my_file.fits')
    export_hdf(a, 'my_file.hdf')

and to convert the other way::

    from fits2hdf.io.fitsio import export_fits
    from fits2hdf.io.hdfio import read_hdf
    a = read_hdf('my_file.hdf')
    export_hdf(a, 'my_file.fits')

For more exciting API musings you can `read the API <api.html>`_.

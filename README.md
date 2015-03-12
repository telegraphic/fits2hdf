fits2hdf
========

`fits2hdf` is a conversion to utility to port FITS files to Hierarchical Data Format (HDF5) 
files in the HDFITS format. In addition, there is a utility to port MeasurementSets (MS)
to HDF5 files. This work was first presented at the [ADASS XXIV](http://arxiv.org/abs/1411.0507)
conference in Calgary, 2014.

The `fits2hdf` utility works by first mapping data from FITS/MS/HDF into an in-memory interchange
format (IDI). `fits2hdf` is written in python and uses h5py, pyFits, and pyrap for file I/O.

`fits2hdf` is still under development, so should be considered an 'alpha' release that is likely
to change. Community feedback is encouraged, and if you are interested in development please
get in touch. This work is intended as a "pathfinder" toward getting astronomical data into 
a standardized HDF5 format, so that the advantages of HDF5 can be leveraged in the future.

HDF5 specifications
-------------------

The HDF5 format has an abstract data model, capable of storing myriad data structures. 
While there are many possible mappings from FITS into HDF5, we have selected a straightforward
one that maps FITS images to the [HDF5 IMAGE specification](http://www.hdfgroup.org/HDF5/doc/HL/H5TB_Spec.html), 
and FITS ASCII tables, binary tables and random group tables to the 
[HDF5 TABLE specification](http://www.hdfgroup.org/HDF5/doc/ADGuide/ImageSpec.html). 
Alternatively, table-like data can be stored in column-by-column hierarchical datasets 
(we are exploring the advantages of both approaches). On top of these specifications sits the 
"HDFITS" specification, that provides an equivalent to the FITS HDU (Header Data Unit). The HDFITS
specification is kept as close to FITS as possible to promote backwards compatibility in the future.

The two main advantages to reusing the HDF5 TABLE and IMAGE specifications are that 1) existing
utilities can already understand them (e.g. PyTables, HDFView), and 2) there are fewer competing
standards. Exploration of whether or not these are sufficient and well-suited to astronomy datasets
is ongoing.

Installation and usage
----------------------

To install, clone the directory and then run `python setup.py install`. You'll need 
[astropy](http://www.astropy.org/) and [h5py](http://www.h5py.org/) to be installed. If you want to
use [bitshuffle](https://github.com/kiyo-masui/bitshuffle) compression, you'll need to install that
too.

To use `fits2hdf` to convert FITS files to HDF5, use the `fits2hdf.py` script:


```
python fits2hdf.py input_dir output_dir <options>
```

Optional arguments are:

```

Convert FITS files to HDF5 files in HDFITS format.

Options:
  -h, --help            show this help message and exit
  -c COMP, --compression=COMP
                        Data compression. Defaults to None, also lzf,
                        bitshuffle, gzip
  -x EXT, --extension=EXT
                        File extension of FITS files. Defaults to .fits
  -v VERBOSITY, --verbosity=VERBOSITY
                        verbosity level (default 0, up to 5)
  -s SCALE_OFFSET, --scaleoffset=SCALE_OFFSET
                        Add scale offset
  -S, --shuffle         Apply byte shuffle filter
  -C, --checksum        Compute fletcher32 checksum on datasets.
```

To convert back into FITS, run `hdf2fits.py`, which uses similar options:

```
python fits2hdf.py input_dir output_dir <options>
```

Loading HDFITS files in python
------------------------------

Functions to read / write HDFITS files into an in-memory data object in python are located in 
`fits2hdf.io.hdfio`. There are equivalent functions to read FITS files into an interchange 
format in `fits2hdf.io.fitsio`. If you have an existing program and want to quickly be able
to read hdf5 files, just change your

``` python
from astropy.io import fits
```
line to 

```
from fits2hdf import pyhdfits as fits
```

and any data in HDFITS will be converted to the PyFITS/ Astropy HDUList object on the fly.

[![astropy](http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat)](http://www.astropy.org/)





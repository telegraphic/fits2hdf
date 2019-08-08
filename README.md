fits2hdf [![Build Status](https://travis-ci.org/telegraphic/fits2hdf.svg?branch=master)](https://travis-ci.org/telegraphic/fits2hdf)
[![astropy](http://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat)](http://www.astropy.org/)
[![Documentation Status](https://readthedocs.org/projects/fits2hdf/badge/?version=latest)](https://readthedocs.org/projects/fits2hdf/?badge=latest)
========

`fits2hdf` is a conversion to utility to port FITS files to Hierarchical Data Format (HDF5)
files in the HDFITS format. In addition, there is a utility to port MeasurementSets (MS)
to HDF5 files. A more complete overview is given in the [fits2hdf Astronomy & Computing paper](http://www.sciencedirect.com/science/article/pii/S2213133715000554).

Documentation
-------------

For documentation and a getting started guide for `fits2hdf`, please head over to our
readthedocs page:

http://fits2hdf.readthedocs.org/en/latest/index.html

Licensing and referencing
-------------------------

This software is licensed under the MIT license. If you use this in published research, it sure
would be swell if you could cite the 
[fits2hdf Astronomy & Computing paper](http://www.sciencedirect.com/science/article/pii/S2213133715000554):

    D.C. Price, B.R. Barsdell, L.J. Greenhill, HDFITS: Porting the FITS data model to HDF5,
    Astronomy and Computing, Available online 22 May 2015, ISSN 2213-1337,
    http://dx.doi.org/10.1016/j.ascom.2015.05.001.


``fits2hdf`` makes use of a few excellent packages:

* [Astropy](https://www.astropy.org), a community-developed core Python package for Astronomy].
* [h5py](http://www.h5py.org/), a Pythonic interface to the HDF5 binary data format.

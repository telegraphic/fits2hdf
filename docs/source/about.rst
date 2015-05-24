About fits2hdf
==============
   
``fits2hdf`` is a conversion to utility to port FITS files to Hierarchical Data Format (HDF5) 
files in the HDFITS format. In addition, there is a utility to port MeasurementSets (MS)
to HDF5 files. This work was first presented at the `ADASS XXIV <http://arxiv.org/abs/1411.0507>`_
conference in Calgary, 2014. A more complete overview is given in `Astronomy & Computing <TODO>`_.

The ``fits2hdf`` utility works by first mapping data from FITS/MS/HDF into an in-memory interchange
format (IDI). ``fits2hdf`` is written in python and uses h5py, pyFits, and pyrap for file I/O.

``fits2hdf`` is still under development, so should be considered an 'alpha' release that is likely
to change. Community feedback is encouraged, and if you are interested in development please
get in touch. This work is intended as a pathfinder toward getting astronomical data into 
a standardized HDF5 format, so that the advantages of HDF5 can be leveraged in the future.


Motivation: why HDF5, and why not FITS?
---------------------------------------

The Flexible Image Transport System (FITS) file format
has enjoyed **several decades** of widespread usage within astronomy.
Its ubiquity has been attributed
to the guiding maxim “once FITS, always FITS”: that
changes to the FITS standard must be incremental so as to
never break backward compatibility. This maxim limits 
what modifications can be made, and FITS is
showing its age; the guiding principle that made FITS so 
successful can now be seen as its Achilles heel.

The limitations of FITS are succinctly summarized in
`Thomas et al. (2014) <TODO>`_ and `Thomas et al. (2015) <TODO>`_. Some of the limitations 
are quite frankly archaic: 8-character maximum keywords in the 
FITS header, lack of Unicode support, and incomplete support of basic
unsigned integer types. Other limitations become apparent when 
compared against newer formats: FITS has no support for chunking, parallel I/O,
or hierarchical data models.


Motivated by data volumes, the Hierarchical Data Format (HDF5) is becoming increasingly 
common in astronomy and science in general. HDF5 has several advantages over FITS, 
with I/O access speed being a compelling reason to make the switch. For example, HDF5 allows
efficient reading of portions of 
a dataset, such as reading along slowly-varying axes of a dataset, which incurs
significant overhead when reading from FITS files. A switch to HDF5 may save you lots of processing time.

For a more complete discussion, see `HDFITS: porting the FITS data model to HDF5 <TODO>`_.

The HDFITS specification
------------------------

The HDF5 format has an abstract data model, capable of storing myriad data structures. 
While there are many possible mappings from FITS into HDF5, we've implemented one that 
we are calling **HDFITS v1.0**. We encourage feedback, and invisage that comments from
the broader community will lead to a HDFITS v2.0.

The goal of HDFITS/fits2hdf is to provide a HDF5-based equivalent of the FITS file format, 
and to provide utilities for converting between the two formats.
The motivation of this approach, as opposed to creating an HDF5-based format from scratch, 
is that decades of widespread FITS usage has left a legacy that would otherwise be discarded. 
By preserving the familiar underlying data model of FITS, software packages designed to read
and interpret FITS can be readily updated to read HDF5
data. Maintaining backwards-compatibility with FITS, so
that data stored in HDF5 files can be converted into FITS
for use in legacy software packages is another persuasive
reason to pursue a FITS-like data model within HDF5.

Of course, a port of the FITS data model to HDF5 does not
address issues with the FITS data model itself. Nevertheless, 
as the HDF5 data model is abstracted from its
file format, an HDF5-based version of the FITS data model
can be extended without requiring changes to the storage model. 
HDFITS can be used as a starting point and as a testbed for
enhancing the FITS data model.

Alternatives
------------

There are a bunch of alternative data formats, and if you're a free spirit 
you can always roll your own higher-level data model inside the HDF5 abstract data model. Otherwise,
look into:

    * `NDF <TODO>`_ is the file format used by Starlink. Recently, Starlink added HDF5 support, meaning
      that you can use the Starlink utilities to convert from FITS into the NDF-HDF5 format.
    * `hickle <https://github.com/telegraphic/hickle>`_ provides a HDF5-based drop-in replacement 
      to the Python `pickle` package, allowing nice & lazy dumping of common python objects to file.
    * `ASDF <TODO>`_ is a file format being developed for interchange, particularly for JWST.
    * `MeasurementSets <TODO>`_ are how the CASA software package stores its data.  
    * `VOTables <TODO>`_ is an XML-based format designed for the Virtual Observatory.   


Copyright and referencing
-------------------------

This software is licensed under the MIT license. If you use this in published research, it sure
would be swell if you could cite the  `fits2hdf Astronomy & Computing paper <TODO>`_::

    REFERENCE TO GO HERE

``fits2hdf`` makes use of a few excellent packages:
    
    * `Astropy <https://www.astropy.org>`_, a community-developed core Python package for Astronomy.
    * `h5py <TODO>`_, a Pythonic interface to the HDF5 binary data format.


.. fits2hdf documentation master file, created by
   sphinx-quickstart on Fri May 22 16:29:56 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

fits2hdf: a FITS to HDF5 conversion utility
===========================================

.. toctree::
   :maxdepth: 2
   
   about
   getting_started
   api
   ...
   
About fits2hdf
--------------

``fits2hdf`` is a conversion to utility to port FITS files to and from Hierarchical Data Format (HDF5) 
files in the HDFITS format. In addition, there is a utility to port MeasurementSets (MS)
to HDF5 files. This work was first presented at the `ADASS XXIV <http://arxiv.org/abs/1411.0507>`_
conference in Calgary, 2014. A more complete overview is given in `Astronomy & Computing <TODO>`_.

The ``fits2hdf`` utility works by first mapping data from FITS/MS/HDF into an in-memory interchange
format (IDI). ``fits2hdf`` is written in python and uses h5py, pyFits, and pyrap for file I/O.

``fits2hdf`` is still under development, so should be considered an 'alpha' release that is likely
to change. Community feedback is encouraged, and if you are interested in development please
get in touch. This work is intended as a pathfinder toward getting astronomical data into 
a standardized HDF5 format, so that the advantages of HDF5 can be leveraged in the future.
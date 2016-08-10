#!/usr/bin/env python
"""
setup.py -- setup script for fits2hdf package
"""
from setuptools import setup, find_packages

# create entry points
# see http://astropy.readthedocs.org/en/latest/development/scripts.html
entry_points = {
    'console_scripts' :
        ['fits2hdf = fits2hdf.file_conversion:convert_fits_to_hdf',
         'hdf2fits = fits2hdf.file_conversion:convert_hdf_to_fits',
         'fits2fits = fits2hdf.file_conversion:convert_fits_to_fits']
    }

setup(name='fits2hdf',
      version='1.0',
      description='FITS to HDF5 conversion utility',
      install_requires=['h5py', 'astropy', 'colorama'],
      url='http://github.com/telegraphic/fits2hdf',
      author='Danny Price',
      author_email='dprice@cfa.harvard.edu',
      license='MIT',
      packages=find_packages(),
      zip_safe=False,
      entry_points=entry_points,
      )

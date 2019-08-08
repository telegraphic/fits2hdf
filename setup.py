# To increment version
# Check you have ~/.pypirc filled in
# git tag x.y.z
# git push && git push --tags
# rm -rf dist; python setup.py sdist bdist_wheel
# TEST: twine upload --repository-url https://test.pypi.org/legacy/ dist/*
# twine upload dist/*

#!/usr/bin/env python
"""
setup.py -- setup script for fits2hdf package
"""
from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

version = '1.1.1'

# create entry points
# see http://astropy.readthedocs.org/en/latest/development/scripts.html
entry_points = {
    'console_scripts' :
        ['fits2hdf = fits2hdf.file_conversion:convert_fits_to_hdf',
         'hdf2fits = fits2hdf.file_conversion:convert_hdf_to_fits',
         'fits2fits = fits2hdf.file_conversion:convert_fits_to_fits']
    }

setup(name='fits2hdf',
      version=version,
      description='FITS to HDF5 conversion utility',
      long_description=long_description,
      long_description_content_type='text/markdown',
      install_requires=['h5py', 'astropy', 'colorama'],
      url='http://github.com/telegraphic/fits2hdf',
      author='Danny Price',
      author_email='dancpr@berkeley.edu',
      license='MIT',
      packages=find_packages(),
      zip_safe=False,
      entry_points=entry_points,
      python_requires='>=3.5',
      download_url='https://github.com/telegraphic/hickle/archive/%s.tar.gz' % version,
      )

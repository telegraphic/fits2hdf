from setuptools import setup, Extension, Distribution, find_packages


setup(name='fits2hdf',
      version='0.2',
      description='FITS to HDF5 conversion utility',
      url='http://github.com/telegraphic/fits2hdf',
      author='Danny Price',
      author_email='dprice@cfa.harvard.edu',
      license='MIT',
      packages=find_packages(),
      zip_safe=False)
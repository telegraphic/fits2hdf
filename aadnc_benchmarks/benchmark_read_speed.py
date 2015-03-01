"""
benchmark compression
---------------------

Generate benchmarks for AANDC paper.

"""

import numpy as np
from os.path import join, getsize,exists
import os, sys
from fits2hdf import idi
from fits2hdf.io import hdfio, fitsio
import time
import glob
import h5py

from astropy.table import Table, Column
import pyfits
from astropy.io import fits as pf


def create_image(img_name, data, hdf_opts={}):
    """ Create HDF and FITS versions of a given image """

    output_dir_fits = 'fits_generated'
    output_dir_hdf  = 'hdf_generated'
    idi_img = idi.IdiHdulist()
    idi_img.add_image_hdu(img_name, data=data)

    # Create all the filenames
    fits_filename = join(output_dir_fits, img_name+'.fits')
    hdf_filename = join(output_dir_hdf, img_name+'.h5')
    hdf_comp_filename = join(output_dir_hdf, img_name+'_comp.h5')
    gzip_comp_filename = join(output_dir_fits, img_name+'.fits.gz')
    fits_comp_filename = join(output_dir_fits, img_name+'.fits.fz')

    # Delete files that already exists
    file_list = [fits_filename, hdf_filename, fits_comp_filename,
                 hdf_comp_filename, gzip_comp_filename]
    for fname in file_list:
        if exists(fname):
            os.remove(fname)

    print "\nWriting %s to disk" % img_name
    t1 = time.time()
    fitsio.export_fits(idi_img, fits_filename)
    t2 = time.time()
    hdfio.export_hdf(idi_img, hdf_filename)
    t3 = time.time()
    hdfio.export_hdf(idi_img, hdf_comp_filename, **hdf_opts)
    t4 = time.time()


def read_speed(img_name):

    output_dir_fits = 'fits_generated'
    output_dir_hdf  = 'hdf_generated'

    fits_filename = join(output_dir_fits, img_name+'.fits')
    hdf_filename = join(output_dir_hdf, img_name+'.h5')
    hdf_comp_filename = join(output_dir_hdf, img_name+'_comp.h5')

    a = pf.open(fits_filename)
    print "DATA SHAPE: %s" % str(a[0].data.shape)
    t1 = time.time()
    for ii in range(a[0].data.shape[0]):
        d = a[0].data[ii::4, ii::4, ii::4]
    t2 = time.time()
    print "Time for FITS access: %2.2es" % (t2 - t1)

    b = h5py.File(hdf_filename)
    #print b.keys()
    d = b["random_integers_23"]["DATA"]
    t1 = time.time()
    for ii in range(d.shape[0]):
        d = a[0].data[ii::4, ii::4, ii::4]
    t2 = time.time()
    print "Time for HDF access: %2.2es" % (t2 - t1)

if __name__== "__main__":
    # IMAGE DATA


    hdf_opts = {
        'compression': 'bitshuffle'
        }

    print "HDF5 compression options:"
    for option, optval in hdf_opts.items():
        print "    ", option, optval

    #file_info = create_image(img_name, img_data, hdf_opts=hdf_opts)


    # Generate data with differing levels of entropy
    print "Generating random integers"
    max_int = 2**23

    #img_data = np.random.random_integers(-1*max_int, max_int, size=(1000, 1000, 1000)).astype('int32')
    #create_image(img_name, img_data, hdf_opts=hdf_opts)

    # Open example datasets
    print "Reading..."


    for copy_num in range(1, 5):
        fname = "random_integers_%i.fits" % np.log2(max_int)
        fname2 = "random_integers_%i%i.fits" % (np.log2(max_int), copy_num)
        print "cp fits_generated/%s fits_generated/%s" % (fname, fname2)
        os.system("cp fits_generated/%s fits_generated/%s" % (fname, fname2))

        fname = "random_integers_%i.fits" % np.log2(max_int)
        fname2 = "random_integers_%i%i.fits" % (np.log2(max_int), copy_num)
        print "cp hdf_generated/%s hdf_generated/%s" % (fname, fname2)
        os.system("cp fits_generated/%s fits_generated/%s" % (fname, fname2))

    for copy_num in range(1, 5):
        img_name = "random_integers_%i%i" % (np.log2(max_int), copy_num)
        read_speed(img_name)
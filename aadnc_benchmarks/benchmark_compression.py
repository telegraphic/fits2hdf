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

from astropy.table import Table, Column



def load_fits(file_name):
    """ Load FITS file, create various things """

    output_dir_fits = 'fits_generated'
    output_dir_hdf  = 'hdf_generated'
    idi_img = fitsio.read_fits(file_name)

    for hdu_name in idi_img:
        hdu = idi_img[hdu_name]
        if isinstance(hdu, idi.IdiTableHdu):
            for col in hdu.colnames:
                if hdu[col].dtype.type is np.float32:
                    #print "CONVERTING %s TO INT" % col
                    hdu[col] = hdu[col].astype('int32')
                    if col == 'FLUX':
                        print "FRUX"
                        hdu[col] = hdu[col].data / 16
                    hdu[col].dtype = 'int32'
                    #print hdu[col].dtype

    img_name = os.path.split(file_name)[1]
    img_name = os.path.splitext(img_name)[0]
    name = img_name
    #idi_img.add_image_hdu(img_name, data=data)

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
    os.system("./fpack -table %s" % fits_filename)
    t5 = time.time()
    os.system("gzip -c %s > %s.gz" % (fits_filename, fits_filename))
    t6 = time.time()

    dd = {
        'img_name': name,
        'fits_size': getsize(fits_filename),
        'hdf_size':  getsize(hdf_filename),
        'hdf_comp_size':  getsize(hdf_comp_filename),
        'fits_comp_size': getsize(fits_filename + '.fz'),
        'gzip_comp_size': getsize(fits_filename + '.gz'),
        'fits_time': (t2 - t1),
        'hdf_time': (t3 - t2),
        'hdf_comp_time': (t4 - t3),
        'fits_comp_time': (t5 - t4),
        'gzip_comp_time': (t6 - t5),
        'comp_fact_hdf': float(getsize(fits_filename)) / getsize(hdf_comp_filename),
        'comp_fact_fits': float(getsize(fits_filename)) / getsize(fits_comp_filename),
        'comp_fact_gzip': float(getsize(fits_filename)) / getsize(gzip_comp_filename)
    }

    rh = dd['comp_fact_gzip']
    th = dd['gzip_comp_time']

    dd["weissman_hdf"] = weissman_score(dd["comp_fact_hdf"], dd["hdf_comp_time"], rh, th)
    dd["weissman_fits"] = weissman_score(dd["comp_fact_fits"], dd["fits_comp_time"], rh, th)

    print "FITS file size:        %sB" % dd['fits_size']
    print "HDF file size:         %sB" % dd['hdf_size']
    print "FITS comp size:        %sB" % dd['fits_comp_size']
    print "HDF comp size:         %sB" % dd['hdf_comp_size']
    print "GZIP comp size:        %sB" % dd['gzip_comp_size']
    print "FITS creation time:    %2.2fs" % dd['fits_time']
    print "HDF  creation time:    %2.2fs" % dd['hdf_time']
    print "FITS comp time:        %2.2fs" % dd['fits_comp_time']
    print "HDF  comp time:        %2.2fs" % dd['hdf_comp_time']
    print "GZIP comp time:        %2.2fs" % dd['gzip_comp_time']
    print "FITS/FITS compression: %2.2fx" % dd['comp_fact_fits']
    print "HDF/FITS compression:  %2.2fx" % dd['comp_fact_hdf']
    print "GZIP/FITS compression: %2.2fx" % dd['comp_fact_gzip']
    print "FITS weissman score:   %2.2f" % dd['weissman_fits']
    print "HDF  weissman score:   %2.2f" % dd['weissman_hdf']


    return dd

def create_image(name, data, hdf_opts={}):
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
    os.system("./fpack -table %s" % fits_filename)
    t5 = time.time()
    os.system("gzip -c %s > %s.gz" % (fits_filename, fits_filename))
    t6 = time.time()

    dd = {
        'img_name': name,
        'fits_size': getsize(fits_filename),
        'hdf_size':  getsize(hdf_filename),
        'hdf_comp_size':  getsize(hdf_comp_filename),
        'fits_comp_size': getsize(fits_filename + '.fz'),
        'gzip_comp_size': getsize(fits_filename + '.gz'),
        'fits_time': (t2 - t1),
        'hdf_time': (t3 - t2),
        'hdf_comp_time': (t4 - t3),
        'fits_comp_time': (t5 - t4),
        'gzip_comp_time': (t6 - t5),
        'comp_fact_hdf': float(getsize(fits_filename)) / getsize(hdf_comp_filename),
        'comp_fact_fits': float(getsize(fits_filename)) / getsize(fits_comp_filename),
        'comp_fact_gzip': float(getsize(fits_filename)) / getsize(gzip_comp_filename)
    }

    rh = dd['comp_fact_gzip']
    th = dd['gzip_comp_time']

    dd["weissman_hdf"] = weissman_score(dd["comp_fact_hdf"], dd["hdf_comp_time"], rh, th)
    dd["weissman_fits"] = weissman_score(dd["comp_fact_fits"], dd["fits_comp_time"], rh, th)

    print "FITS file size:        %sB" % dd['fits_size']
    print "HDF file size:         %sB" % dd['hdf_size']
    print "FITS comp size:        %sB" % dd['fits_comp_size']
    print "HDF comp size:         %sB" % dd['hdf_comp_size']
    print "GZIP comp size:        %sB" % dd['gzip_comp_size']
    print "FITS creation time:    %2.2fs" % dd['fits_time']
    print "HDF  creation time:    %2.2fs" % dd['hdf_time']
    print "FITS comp time:        %2.2fs" % dd['fits_comp_time']
    print "HDF  comp time:        %2.2fs" % dd['hdf_comp_time']
    print "GZIP comp time:        %2.2fs" % dd['gzip_comp_time']
    print "FITS/FITS compression: %2.2fx" % dd['comp_fact_fits']
    print "HDF/FITS compression:  %2.2fx" % dd['comp_fact_hdf']
    print "GZIP/FITS compression: %2.2fx" % dd['comp_fact_gzip']
    print "FITS weissman score:   %2.2f" % dd['weissman_fits']
    print "HDF  weissman score:   %2.2f" % dd['weissman_hdf']


    return dd

def weissman_score(r, t, rh, th):
    """ Compute the Weissman score for a compression algorithm

    :param r: compression ratio
    :param t: time to compress (in ms).
    :param rh: compression ratio of standard (gzip)
    :param th: time to compress of standard (gzip)
    :return: weissman score (int)
    """

    W = 1.0* r * np.log(th * 1e3) / rh / np.log(t * 1e3)

    return W

if __name__== "__main__":
    # IMAGE DATA

    print "Generating data.."
    img_name = "sin_outer"
    d = np.linspace(1e5, 1e6, 1024)
    img_data = np.sin(np.outer(d, d))

    hdf_opts = {
        'compression': 'bitshuffle'
        }

    print "HDF5 compression options:"
    for option, optval in hdf_opts.items():
        print "    ", option, optval

    #file_info = create_image(img_name, img_data, hdf_opts=hdf_opts)

    tbl = Table(
        names=['img_name', 'fits_size', 'hdf_size', 'fits_comp_size', 'hdf_comp_size',
               'gzip_comp_size', 'fits_time', 'hdf_time', 'fits_comp_time', 'hdf_comp_time',
               'gzip_comp_time', 'comp_fact_hdf', 'comp_fact_fits', 'comp_fact_gzip',
               'weissman_fits', 'weissman_hdf'],
        dtype=['S32', 'i4', 'i4', 'i4', 'i4', 'i4', 'f4', 'f4', 'f4', 'f4', 'f4',
               'f4', 'f4', 'f4', 'f4', 'f4']
        )


    # Generate data with differing levels of entropy
    for max_int in (2**7, 2**15, 2**23, 2**31):
        img_name = "random_integers_%i" % np.log2(max_int)
        img_data = np.random.random_integers(-1*max_int, max_int, size=(8192, 8192)).astype('int32')
        file_info = create_image(img_name, img_data, hdf_opts=hdf_opts)

        tbl.add_row(file_info)

    tbl.add_columns

    # Open example datasets

    #for file_name in glob.glob("fits/*.fitsidi"):
    #    file_info = load_fits(file_name)
    #    tbl.add_row(file_info)

    tbl.write("generated_data_report.html", format="html")
    tbl.write("generated_data_report.tex", format="latex")

    print tbl
    #tbl.show_in_browser()
from fits2hdf.io import fitsio
import pylab as plt
import os
import glob

for fits_file in glob.glob('test/fits/*.fits'):

    print "Reading %s" % fits_file
    fits_a = fitsio.read_fits(fits_file)
    print fits_a

    if os.path.exists("test.fits"):
        os.remove("test.fits")

    print "Writing %s copy" % fits_file

    fitsio.export_fits(fits_a, "test.fits")

    try:
        fits_b = fitsio.read_fits("test.fits")
        print fits_b
    except:
        print "ERROR: can't read %s" % fits_file
        raise
    ##print fits_a
    #print fits_b


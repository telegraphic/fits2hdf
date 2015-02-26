from fits2hdf.io import fitsio, hdfio
import pylab as plt
import os
import glob

fits_file = 'test/fits/LWA1-2014-02-23T11H06M51.fitsidi'

print "Reading %s" % fits_file
fits_a = fitsio.read_fits(fits_file)
print fits_a

if os.path.exists("test.hdf"):
    os.remove("test.hdf")

print "Writing %s copy" % fits_file

hdfio.export_hdf(fits_a, "test.hdf")

try:
    fits_b = hdfio.read_hdf("test.hdf")
    print fits_b
except:
    print "ERROR: can't read %s" % fits_file
    raise
    ##print fits_a
    #print fits_b


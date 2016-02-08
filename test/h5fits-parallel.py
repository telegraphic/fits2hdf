import os
import sys
sys.path.append('..')

from fits2hdf.io.fitsio import *
from fits2hdf.io.hdfio import *
from fits2hdf import idi
import numpy as np
from astropy.io import fits as pf
import h5py
from multiprocessing import Pool
import time
rootdir= "/global/projecta/projectdirs/sdss/data/sdss/dr12/boss/spectro/redux/v5_7_0/"
outputd ="/global/cscratch1/sd/jialin/hdf-data/v5_7_0-sample/sample/"

#function for listing all fits files and fits.gz files inside given path and all sub-folders
def listfiles(x):
     fitsfiles = [os.path.join(root, name)
       for root, dirs, files in os.walk(x)
       for name in files
       if name.endswith((".fits", ".fits.gz"))]
     return fitsfiles
#function for combining one fits folder into a single HDF5 file
def test_multihdf(x):
     thedir = rootdir+str(x)+"/"
     try:
         count=0
         fitlist=listfiles(thedir)
         print "number of files %d" % len(fitlist), "in ", thedir
         for fname in fitlist:
             a = read_fits(fname) 
             gname=fname.split('/')[-1]
             outputf=outputd+str(x)+".h5"
             export_hdf(a, outputf, root_group=gname)
             count=count+1
     except TypeError:
         print x
     finally:
         pass
def parallel_test_multihdf():
     if (len(sys.argv)!=2):
       print "usage: python -W ignore h5fits-parallel.py number_of_processes"
       print "example: python h5fits-parallel.py 32"
       print "*****************End********************"
       sys.exit(1)
     n=int(sys.argv[1])
     ldir=os.listdir(rootdir)    
     lldir=[fn for fn in ldir if fn.isdigit()]
     print "*****************Start******************"
     print "Totally, ", len(lldir), "fits files in folder: ", rootdir
     print "Totally, ",len(ldir), "fits folders, e.g., 4440"
     if (len(lldir)==0):
        print "No fits folder exists, Exit program"
        print "*****************End********************"
        sys.exit(1)
     print "****************In Progress*************"
     start = time.time()
     p=Pool(n)
     p.map(test_multihdf,lldir)
     end = time.time()
     print "Combined",len(lldir),"fits folder to hdf5 files, costs ", end-start, " seconds"
     print "Check output at ", outputd
     print "*****************End********************"
if __name__ == '__main__':
    parallel_test_multihdf()

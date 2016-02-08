import os
import sys
sys.path.append('..')
import time
from fits2hdf.io.fitsio import *
from fits2hdf.io.hdfio import *
from fits2hdf import idi
import numpy as np
from astropy.io import fits as pf
import h5py
rootdir= "/global/projecta/projectdirs/sdss/data/sdss/dr12/boss/spectro/redux/v5_7_0/"
outputd ="/global/cscratch1/sd/jialin/hdf-data/v5_7_0-sample/sample/"
#import progressbar as pb

def listfiles(x):
     fitsfiles = [os.path.join(root, name)
       for root, dirs, files in os.walk(x)
       for name in files
       if name.endswith((".fits", ".fits.gz"))]
     return fitsfiles

def test_multihdf(x):
     thedir = rootdir+str(x)+"/"
     try:
         count=0
         fitlist=listfiles(thedir)
         print "number of files %d" % len(fitlist)
         for fname in fitlist:
             #if "fits" in fname or "gz" in fname:
             a = read_fits(fname) 
             gname=fname.split('/')[-1]  
             outputf=outputd+str(x)+".h5"
             export_hdf(a, outputf, root_group=gname)
             count=count+1
     except TypeError:
         print x
     finally:
         pass
def h5fit_test1():
     if (len(sys.argv)!=2):
       print "usage: python -W ignore h5fits-serial.py input_folder_name"
       print "example: python h5fits-serial.py 4440"
       print "*****************End********************"
       sys.exit(1)
     input=sys.argv[1]
     thedir = rootdir+str(input)+"/"
     numfits = listfiles(thedir)
     print "*****************Start******************"
     print "Totally,",len(numfits),"fits files in folder:", thedir
     if (len(numfits)==0):
        print "No fits exists, Exit program"
        print "*****************End********************"
        sys.exit(1)
     print "****************In Progress*************"
     #progress = pb.ProgressBar(widgets=_widgets, maxval = 500000).start()
     #progvar = 0
     #for i in range(500000):
     start = time.time()
     test_multihdf(input)
     end = time.time()
      #progress.update(progvar + 1)
      #progvar += 1
     print "Combined",len(numfits),"fits to hdf5, costs ", end-start, " seconds"
     print "Check output at ", outputd
     print "*****************End********************"
if __name__ == '__main__':
    h5fit_test1()

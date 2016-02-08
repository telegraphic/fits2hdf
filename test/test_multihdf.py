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
rootdir= "/global/projecta/projectdirs/sdss/data/sdss/dr12/boss/spectro/redux/v5_7_0/"
outputd ="/global/cscratch1/sd/jialin/hdf-data/v5_7_0/"
def test_multihdf(x):
     thedir = rootdir+str(x)+"/"
     try:
         count=0
         for fname in os.listdir(thedir):
             if "fits" in fname or "gz" in fname:
	        #print fname
                a = read_fits(thedir + fname)   
                #outputf=outputd+thedir.split('/')[-1]+".h5"
                outputf=outputd+str(x)+".h5" 
                export_hdf(a, outputf, root_group=fname)
                count=count+1
         #print "combining "+count+"in "+str(x)
     except TypeError:
         print x
     finally:
         pass
def parallel_test_multihdf():
     #n=int(sys.argv[1])
     n=1
     p=Pool(n)
     ldir=os.listdir(rootdir)
     #print len(ldir)
     lldir=[fn for fn in ldir if fn.isdigit()]
     #print len(lldir)
     p.map(test_multihdf,lldir)
if __name__ == '__main__':
    parallel_test_multihdf()

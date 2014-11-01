import os
import sys

sys.path.append('..')

from fits2hdf.io.fitsio import *
from fits2hdf.io.hdfio import *
from fits2hdf import idi
import numpy as np
import pyfits as pf
import h5py

if __name__ == '__main__':

    download_fits = False
    run_converter = False
    run_tests     = True
    ext = 'fits'

    if download_fits:
        os.system('python download_test_fits.py')
    if run_converter:
        os.system('python ../fits2hdf.py fits hdf -c gzip -x %s' % ext)
        #os.system('python ../fits2hdf.py fits hdf -c gzip -x fz')

    if run_tests:
        for fits_file in os.listdir('fits'):
            if fits_file.endswith(ext):
                hdf_file = fits_file.split('.'+ext)[0] + '.h5'
                print "\nFITS: %s" % fits_file
                print "HDF:  %s" % hdf_file
                # Assert that file has been created
                try:
                    assert os.path.exists('hdf/' + hdf_file)
                    print "Test 01: OK - HDF5 file created"
                except AssertionError:
                    print "Test 01: FAIL - HDF5 file not created"
                    raise

                # open the files
                a = pf.open('fits/' + fits_file)
                b = h5py.File('hdf/' + hdf_file)

                # Check all HDUS have been ported over
                try:
                    for hdu_item in a:
                        assert hdu_item.name in b.keys()
                    print "Test 02: OK - All HDUs in FITS in HDF5 file"
                except AssertionError:
                    print "Test 02: ERROR - cannot match all FITS files"
                    print a.info()
                    print b.keys()
                    raise

                a.close()
                b.close()

                # IDILIST based tests
                c = idi.IdiList()
                d = idi.IdiList()

                c = read_fits('fits/' + fits_file)
                d = read_hdf('hdf/' + hdf_file, verbosity=0)

                for name, group in c.items():
                    assert name in d
                    group2 = d[name]
                    try:
                        assert isinstance(d[name], type(group))
                        print "Test 03a: OK - Both files as IDI have group  %s" % name
                    except AssertionError:
                        print "Test 03a: ERROR - both files do not have group  %s" % name
                    all_match = True
                    if isinstance(group, idi.IdiTable):
                        for dc, dd in group.data.items():
                            assert dc in group2.data
                            try:
                                assert np.allclose(dd.data, group2.data[dc].data)
                            except TypeError:
                                d1 = dd.data
                                d2 = group2.data[dc].data

                                for ii in range(len(d1)):
                                    try:
                                        assert str(d1[ii]).strip() == str(d2[ii]).strip()
                                    except AssertionError:
                                        print d1[ii]
                                        print d2[ii]
                                        all_match = False

                    if all_match:
                        print "Test 03b: OK - All data match between FITS and HDF5"
                    else:
                        print "Test 03b: ERROR - Not all data match"

                    attr_match = True
                    for hc, hv in group.header.vals.items():
                        #print  group2.header.vals

                        try:
                            assert hc in group2.header.vals.keys()
                            assert group2.header.vals[hc][0] == hv[0]
                            assert group2.header.vals[hc][1] == hv[1]
                        except AssertionError:
                            attr_match = False
                            print hc
                            print "FITS FILE:"
                            print group.header
                            print group

                            print "HDF5 FILE:"
                            print group2.header
                            print group
                            raise

                    if attr_match:
                        print "Test 04: OK - All attributes match between FITS and HDF5"
                    else:
                        print "Test 04: ERROR - Not all attributes match"




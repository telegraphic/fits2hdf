import os, sys
sys.path.append('..')

from fits2hdf import idi
from fits2hdf.io.msio import *
from fits2hdf.io.hdfio import *
import pylab as plt
import numpy as np
import pyfits as pf
import h5py


if __name__ == '__main__':

    create_hdf = True
    create_ms  = False
    run_tests  = True
    ext = 'ms'

    if create_hdf:
        os.system('python ../ms2hdf.py ms hdfms -c lzf -x %s' % ext)

    if create_ms:
        # TODO: Add HDF -> MS porting
        pass

    if run_tests:
        for fits_file in os.listdir('ms'):
            if fits_file.endswith(ext):
                hdf_file = fits_file.split('.'+ext)[0] + '.h5'
                print "\nMS: %s" % fits_file
                print "HDF:  %s" % hdf_file
                # Assert that file has been created
                try:
                    assert os.path.exists('hdfms/' + hdf_file)
                    print "Test 01: OK - HDF5 file created"
                except AssertionError:
                    print "Test 01: FAIL - HDF5 file not created"
                    raise

                c = read_ms('ms/' + fits_file)
                d = read_hdf('hdfms/' + hdf_file)

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
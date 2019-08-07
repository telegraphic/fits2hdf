import os
import sys
import warnings

sys.path.append('..')

from fits2hdf.io.fitsio import *
from fits2hdf.io.hdfio import *
from fits2hdf import idi
import numpy as np
from astropy.io import fits as pf
import h5py
import warnings

def test_fits2hdf():
    download_fits = False
    run_converter = True
    run_tests     = True
    ext = 'fits'

    commands_to_test = [
        'fits2hdf fits hdf -c gzip -x fits -v 0',
        #'fits2hdf fits hdf -c bitshuffle -x fits -v 0 -t',
        'fits2hdf fits hdf -c lzf -x fits -v 0 -t',
        'fits2hdf fits hdf -c lzf -C -S -x fits -v 0',
        'fits2hdf fits hdf -c lzf -C -S -x fits -v 0 -t',
        #'python fits2hdf.py fits hdf -c lzf -S -s 1 -x fits -v 0',
    ]

    #NB : Scale-offset filter will cause comparison to input to fail as it is lossy
    #NB : e.g. 'python ../fits2hdf.py fits hdf -c lzf -S -s 1 -x fits -v 0',
    #NB : will fail

    for cmd2test in commands_to_test:
        if download_fits:
            os.system('python download_test_fits.py')
        if run_converter:
            print("")
            print("--------")
            print("")
            print("Converting FITS files to HDFITS..")
            os.system(cmd2test)
            #os.system('python ../fits2hdf.py fits hdf -c gzip -x fz')

        warnings.simplefilter("ignore")

        if run_tests:
            for fits_file in os.listdir('fits'):
                if fits_file.endswith(ext):
                    hdf_file = fits_file.split('.'+ext)[0] + '.h5'
                    print("\nFITS: %s" % fits_file)
                    print("HDF:  %s" % hdf_file)
                    # Assert that file has been created
                    try:
                        assert os.path.exists('hdf/' + hdf_file)
                        print("Test 01: OK - HDF5 file created")
                    except AssertionError:
                        print("Test 01: FAIL - HDF5 file not created")
                        raise

                    # open the files
                    a = pf.open('fits/' + fits_file)
                    b = h5py.File('hdf/' + hdf_file)

                    # Check all HDUS have been ported over
                    try:
                        for hdu_item in a:
                            assert hdu_item.name in b.keys()
                        print("Test 02: OK - All HDUs in FITS in HDF5 file")
                    except AssertionError:
                        print("Test 02: ERROR - cannot match all FITS files")
                        print(a.info())
                        print(b.keys())
                        raise

                    a.close()
                    b.close()

                    # IDILIST based tests
                    c = idi.IdiHdulist()
                    d = idi.IdiHdulist()

                    c = read_fits('fits/' + fits_file)
                    d = read_hdf('hdf/' + hdf_file, verbosity=0)

                    for name, group in c.items():
                        assert name in d
                        group2 = d[name]
                        try:
                            assert isinstance(d[name], type(group))
                            print("Test 03a: OK - Both files as IDI have group  %s" % name)
                        except AssertionError:
                            print("Test 03a: ERROR - both files do not have group  %s" % name)
                            raise
                        all_match = True
                        if isinstance(group, idi.IdiTableHdu):
                            for dc in group.colnames:
                                assert dc in group2.colnames
                                try:
                                    #print type(group[dc].unit), type(group2[dc].unit)
                                    assert group[dc].unit == group2[dc].unit

                                except AssertionError:
                                    print("WARNING: units do no match:",)
                                    print("Key: %s, fits: %s, hdf: %s" % (dc, group[dc].unit, group2[dc].unit))
                                    all_match = False
                                except TypeError:
                                    print(type(group[dc]))
                                    print(type(group2[dc]))
                                    raise
                                try:
                                    assert np.allclose(group[dc], group2[dc])
                                except TypeError:

                                    for ii in range(len(group[dc])):
                                        try:
                                            assert str(group[dc][ii]).strip() == str(group2[dc][ii]).strip()
                                        except AssertionError:
                                            print(group[dc][ii])
                                            print(group2[dc][ii])
                                            all_match = False

                        if all_match:
                            print("Test 03b: OK - All data match between FITS and HDF5")
                        else:
                            print("Test 03b: ERROR - Not all data match")
                            raise

                        attr_match = True

                        #print group.header
                        for hc, hv in group.header.items():
                            #print  group2.header.vals

                            try:
                                assert hc in group2.header.keys()

                                assert group2.header[hc] == hv
                                #assert group2.header[hc+"_COMMENT"] == hv[1]
                            except AssertionError:
                                attr_match = False
                                print("WARNING: header values do not match", hc, hv, group2.header[hc])
                                #print type(hv), type(group2.header[hc])
                                #print "FITS FILE:"
                                ##print group.header
                                #print group

                                #print "HDF5 FILE:"
                                #print group2.header
                                #print group

                                # print group2.header[hc]
                                #print hv[1]
                                #raise

                        if attr_match:
                            print("Test 04: OK - All attributes match between FITS and HDF5")
                        else:
                            print("Test 04: ERROR - Not all attributes match")
                            raise


if __name__ == '__main__':
    test_fits2hdf()

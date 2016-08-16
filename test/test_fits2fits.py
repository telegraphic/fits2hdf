import os
import subprocess

from fits2hdf.io.fitsio import *
from fits2hdf.io.hdfio import *
from fits2hdf import idi
import numpy as np

import warnings

def test_fits2fits():
    download_fits = False
    run_converter = True
    run_tests     = True
    overwrite_out = True
    ext = 'fits'

    warnings.simplefilter("ignore")

    if download_fits:
        os.system('python download_test_fits.py')
    if run_converter:
        print("Converting FITS files to FITS..")
        if overwrite_out:
            subprocess.check_call('fits2fits fits fits_out -w -x {} -o'.format(ext).split(' '))
        else:
            subprocess.check_call('fits2fits fits fits_out -w -x {}'.format(ext).split(' '))
        #os.system('python ../fits2hdf.py fits hdf -c gzip -x fz')

    if run_tests:
        for fits_file in os.listdir('fits'):
            if fits_file.endswith(ext):
                if fits_file == 'DDTSUVDATA.fits':
                    pass

                fits_file_out = fits_file
                print("\nFITS: %s" % fits_file)
                print("FITS_OUT:  %s" % fits_file_out)
                # Assert that file has been created
                try:
                    assert os.path.exists('fits_out/' + fits_file_out)
                    print("Test 01: OK - FITS_OUT file created")
                except AssertionError:
                    print("Test 01: FAIL - FITS_OUT file not created")
                    raise

                # IDILIST based tests
                c = idi.IdiHdulist()
                d = idi.IdiHdulist()

                c = read_fits('fits/' + fits_file)
                d = read_fits('fits_out/' + fits_file_out)

                for name, group in c.items():
                    try:
                        # pyfits may captalize extension name.
                        in_both = name in d or name.upper() in d or name.lower() in d
                        assert in_both
                    except:
                        print("ERROR: Can't match extension %s in %s" % (name, d))
                    group2 = d[name]
                    try:
                        assert isinstance(d[name], type(group))
                        print("Test 03a: OK - Both files as IDI have group  %s" % name)
                    except AssertionError:
                        if name == "PRIMARY":
                            group2 = d["PRIDATA"]
                            assert isinstance(d["PRIDATA"], type(group))
                            print("Test 03a: OK with GROUPSHDU exception - Both files as IDI have group  %s" % name)
                        else:
                            print("Test 03a: ERROR - both files do not have group  %s" % name)
                    all_match = True
                    if isinstance(group, idi.IdiTableHdu):
                        for dc in group.colnames:
                            assert dc in group2.colnames
                            try:
                                assert group[dc].shape == group2[dc].shape
                            except:
                                print("ERROR: shapes do no match:",)
                                print("GROUP1: %s, GROUP2: %s" % (group[dc].shape, group2[dc].shape))
                                raise
                            try:
                                assert group[dc].unit == group2[dc].unit
                            except AssertionError:
                                print("WARNING: units do no match:",)
                                print("Key: %s, fits: %s, hdf: %s" % (dc, group[dc].unit, group2[dc].unit))
                                all_match = False
                            try:
                                assert np.allclose(group[dc], group2[dc])
                            except AssertionError:
                                print("ERROR!: DATA DO NOT MATCH!")
                                print(group[dc][0])
                                print(group2[dc][0])
                            except TypeError:

                                for ii in range(len(group[dc])):
                                    try:
                                        assert str(group[dc][ii]).strip() == str(group2[dc][ii]).strip()
                                    except AssertionError:
                                        print(group[dc][ii])
                                        print(group2[dc][ii])
                                        all_match = False

                    if all_match:
                        print("Test 03b: OK - All data match between FITS and FITS_OUT")
                    else:
                        print("Test 03b: ERROR - Not all data match")

                    attr_match = True

                    #print group.header
                    for hc, hv in group.header.items():
                        #print  group2.header.vals

                        try:
                            assert hc in group2.header.keys()

                            assert group2.header[hc] == hv or np.allclose(group2.header[hc], hv)
                            #assert group2.header[hc+"_COMMENT"] == hv[1]
                        except AssertionError:
                            attr_match = False
                            print("WARNING: header values do not match", hc, hv, group2.header[hc])
                            print(type(hv), type(group2.header[hc]))
                            #print type(hv), type(group2.header[hc])
                            #print "FITS FILE:"
                            ##print group.header
                            #print group

                            #print "FITS_OUT FILE:"
                            #print group2.header
                            #print group

                            # print group2.header[hc]
                            #print hv[1]
                            #raise

                    if attr_match:
                        print("Test 04: OK - All attributes match between FITS and FITS_OUT")
                    else:
                        print("Test 04: ERROR - Not all attributes match")

if __name__ == '__main__':
    test_fits2fits()





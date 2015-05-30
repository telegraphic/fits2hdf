"""
download_test_fits.py
---------------------

This script downloads sample FITS files from the NASA registry.

Individual Sample FITS files
http://fits.gsfc.nasa.gov/fits_samples.html

Sloane Digital Sky Survey (SDSS) data sample fits files
http://data.sdss3.org/
"""

import os

for dname in ('fits', 'fits_sdss'):
    if not os.path.exists(dname):
        os.mkdir(dname)

################################
## Download example fits from FITS registry
## These are relatively small
################################

filelist = [
    'http://fits.gsfc.nasa.gov/samples/WFPC2u5780205r_c0fx.fits',
    'http://fits.gsfc.nasa.gov/samples/WFPC2ASSNu5780205bx.fits',
    'http://fits.gsfc.nasa.gov/samples/FOCx38i0101t_c0f.fits',
    'http://fits.gsfc.nasa.gov/samples/FOSy19g0309t_c2f.fits',
    'http://fits.gsfc.nasa.gov/samples/HRSz0yd020fm_c2f.fits',
    'http://fits.gsfc.nasa.gov/samples/NICMOSn4hk12010_mos.fits',
    'http://fits.gsfc.nasa.gov/samples/FGSf64y0106m_a1f.fits',
    'http://fits.gsfc.nasa.gov/samples/UITfuv2582gc.fits',
    'http://fits.gsfc.nasa.gov/samples/IUElwp25637mxlo.fits',
    'http://fits.gsfc.nasa.gov/samples/EUVEngc4151imgx.fits',
    'http://fits.gsfc.nasa.gov/samples/DDTSUVDATA.fits',
    'http://fits.gsfc.nasa.gov/samples/testkeys.fits'    
    ]


################################
## Download a few files from SDSS archive
## These files are much larger!
################################


filelist_sdss = [
    'http://data.sdss3.org/sas/dr12/sdss/spectro/redux/photoMatchPlate-dr12.fits',
    'http://data.sdss3.org/sas/dr12/sdss/sspp/ssppOut-dr12.fits',
    'http://data.sdss3.org/sas/dr12/sdss/segue2/target/seguetsObjSetAllDup-0338-3138-0101.fits'
    ]

print("Downloading example files from FITS registry...")

for filename in filelist:
    os.system('wget %s' % filename)
    os.system('mv %s fits/' % filename.split('/')[-1])

print("Downloading example files from FITS registry...")
for filename in filelist_sdss:
    os.system('wget %s' % filename)
    os.system('mv %s fits_sdss/' % filename.split('/')[-1])
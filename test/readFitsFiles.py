## make sure you module load python/2.7-anaconda first, in order to access astropy module

### useful links:
## Descriptions of what's in each fits file: http://data.sdss3.org/datamodel/files/BOSS_SPECTRO_REDUX/RUN2D/PLATE4/
## astropy fits documentsion: http://docs.astropy.org/en/stable/io/fits/
## general fits info: http://fits.gsfc.nasa.gov/fits_primer.html

from astropy.io import fits
import numpy as np
import os


## This is where an example set of SDSS fits files lives. We would like to preserve this structure for now. The directory should become an hdf5 file, and every file should become a group in the hdf5 file. 
## "4444" refers to the "plate number" - this is how all processing is done, so it makes sense to group the data according to the plate number. 
thedir = "/global/projecta/projectdirs/sdss/data/sdss/dr12/boss/spectro/redux/v5_7_0/4444/"

## The plate is actually a piece of metal with holes drilling in it - each hole has an optical fibre places in it, and the location of that fibre corresponds to the location of a star/galaxy on the sky. So the light from each fiber is the light from one object. 

## a single image taken with this plate is called a "frame". There may be multiple frames taken with each plate - these are labeled with a frame number. 
## There are actually four components to each frame - each of the 1000 fibers are sent to one of two spectrographs (i.e. 500 go to one, 500 go to the other). There are two cameras (red and blue) for each spectrograph - so the frames are split into r1, b1, r2, b2. 

## Let's take a look at one of these frames:
for afile in os.listdir(thedir):
    if "spFrame" in afile:
        print afile

## The different segments (or "extensions") of a fits file are called "Header/Data  Units" (or HDU). 
hdulist = fits.open(thedir+"spFrame-r1-00123587.fits.gz")

## what segments do we have?
print hdulist.info()

## There's a lot in there! All you need to know is that each extension has two types of data you will need to store in the hdf5 file: header and data. 


## ******** headers ***********##
print "\n looking at header data"
## To access the header information (which is in a weird astro format of very specific dimensions (80 byte "cards", where each card contains a keyword, a value, and a comment):
headers = []
for i in range(len(hdulist)):
    headers.append(hdulist[i].header)

## because of the weird formatting, it's easiest to print out the entire header using repr
print "example header"
print repr(headers[0])


## this will give you the keyword, value and comments for each header item
for i in range(len(headers[2])):
    print headers[2].keys()[i], headers[2][i], headers[2].comments[i]


 
## ******** data ***********##
print "\n looking at data"
## There are two types of data - image and table. 
## Image data is straightforward - you can read it as a NxM numpy array, where N is the nubmer of bins the spectrum is measured in, and M is 500 (for the 500 fibers going to each spectrograph). Although, some of the fits files here have M=1000, because they are composites of the two sets of 500.  
## Anyway, this is how you read image data:
print "\n looking at image data"
datas = []
for i in range(len(hdulist)):
    if type(hdulist[i].data)==np.ndarray: ## this is an easy way to check if you have image data
        datas.append(hdulist[i].data)
datas = np.array(datas)
print "shape of data:", datas.shape

    
## Table data is a bit more complicated. 
print "\n looking at table data"
tables = []

for i in range(len(hdulist)):
    if type(hdulist[i].data)==fits.fitsrec.FITS_rec:
        tables.append(hdulist[i].data)


## the problem is that each table will be different. To see the columns in a table:
print "columns in table:"
print tables[1].columns.info()

## To look at one row (row number 0 here, cos in this table there happens to be only one row) in the table (not super useful):
print tables[1].shape 
print "rwo 0 from table 1:", tables[1][0]

## If you want to look at the entire column, you have to reference it by column name. 
table_names = []
for i in range(len(tables)):
    table_names.append(tables[i].columns.names)

print "column 0 from table 1:", tables[1][table_names[1][0]]

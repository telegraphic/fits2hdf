# -*- coding: utf-8 -*-

"""
hdfcompress.py
==============

Helper functions for writing bitshuffled compressed datatsets
"""

import numpy as np
from h5py import  h5z

import quinoa

from fits2hdf.printlog import PrintLog

try:
    from bitshuffle import h5
    USE_BITSHUFFLE = True
except ImportError:
    USE_BITSHUFFLE = False

def guess_chunk(shape):
    """ Guess the optimal chunk size for a given shape
    :param shape: shape of dataset
    :return: chunk guess (tuple)

    # TODO: Make this better
    """
    ndim = len(shape)

    if ndim == 1:
        chunks = (min((shape[0], 1024)), )
    elif ndim == 2:
        chunks = (min((shape[0], 256)), min((shape[1], 256)))
    elif ndim == 3:
        chunks = (min((shape[0], 128)), min((shape[1], 128)),
                  min((shape[2], 16)))
    elif ndim == 4:
        chunks = (min((shape[0], 128)), min((shape[1], 128)),
                  min((shape[2], 16)),  min((shape[2], 16)))
    elif ndim == 5:
        chunks = (min((shape[0], 1)),
                  min((shape[1], 10)),
                  min((shape[2], 128)),
                  min((shape[3], 16)),
                  min((shape[4], 16))
                  )
    else:
        raise RuntimeError("Couldn't handle shape %s" % shape)
    return chunks

def create_compressed(hgroup, name, data, **kwargs):
    """
    Add a compressed dataset to a given group.

    Use bitshuffle compression and LZ4 to compress a dataset.

    hgroup: h5py group in which to add dataset
    name:   name of dataset
    data:   data to write
    chunks: chunk size
    """


    # Parse keyword arguments that we need to check
    compression = ''
    if 'compression' in kwargs:
        compression = kwargs['compression']
        if compression is None:
            compression = ''

    if 'chunks' not in kwargs:
        kwargs['chunks'] = guess_chunk(data.shape)
        chunks = kwargs['chunks']

    #print name, shape, dtype, chunks

    if compression.startswith('quinoa') and USE_BITSHUFFLE:
        q = 4
        do_dither = True

        try:
            cparts = compression.split('_')
            q = int(cparts[1])
            do_dither = bool(cparts[2])
            #print cparts
        except:
            pass

        if data.ndim == 2:
            print("QUINOA: scaling %s " % name)
            qdata = quinoa.quinoa_scale(data, q=q, subtractive_dither=do_dither)
            data = qdata["data"]
            #data = quinoa.quinoa_unscale(qdata)
            #dtype = "int32"
            for key in qdata:
                if key != 'data':
                    print("QUINOA: %s: %s" % (key, qdata[key]))

        #print "Creating bitshuffled dataset %s" % hgroup
        print(data.dtype)
        h5.create_dataset(hgroup, name, data.shape, data.dtype, chunks,
                          filter_pipeline=(32008,),
                          filter_flags=(h5z.FLAG_MANDATORY,),
                          filter_opts=((0, h5.H5_COMPRESS_LZ4),),
                          )

    elif compression == 'couscous' and USE_BITSHUFFLE:
        qdata = quinoa.couscous_scale(data)
        data = qdata["data"]
        #for key in qdata:
        #    if key != 'data':
        #        print "COUSCOUS: %s: %s" % (key, qdata[key])

        h5.create_dataset(hgroup, name, data.shape, data.dtype, chunks,
                          filter_pipeline=(32008,),
                          filter_flags=(h5z.FLAG_MANDATORY,),
                          filter_opts=((0, h5.H5_COMPRESS_LZ4),),
                          )

    elif compression == 'bitshuffle' and USE_BITSHUFFLE:
        #print "Creating bitshuffled dataset %s" % hgroup
        h5.create_dataset(hgroup, name, data.shape, data.dtype, chunks,
                          filter_pipeline=(32008,),
                          filter_flags=(h5z.FLAG_MANDATORY,),
                          filter_opts=((0, h5.H5_COMPRESS_LZ4),),
                          )
    else:
        #print "Creating dataset %s" % hgroup
        hgroup.create_dataset(name, data.shape, data.dtype, **kwargs)

    hgroup[name][:] = data

    return hgroup[name]

def create_dataset(hgroup, name, data, **kwargs):
    """ Create dataset from data, will attempt to compress

    :param hgroup: h5py group in which to add dataset
    :param name: name of dataset
    :param data: data to write
    """


    verbosity = 0
    if 'verbosity' in kwargs:
        verbosity = kwargs.pop('verbosity')

    pp = PrintLog(verbosity)

    np_types = [
            np.uint8,
            np.uint16,
            np.uint32,
            np.uint64,
            np.int8,
            np.int16,
            np.int32,
            np.int64,
            np.float16,
            np.float32,
            np.float64,
            np.complex64,
            np.complex128,
            np.void]

    np_types = set(np_types)

    #print name, str(data.dtype)
    #print data.dtype.type, data.dtype.type in np_types
    if data.dtype.type in np_types:
        pp.debug("Creating compressed %s" % name)
        dset = create_compressed(hgroup, name, data, **kwargs)
    else:
        try:
            pp.debug("Creating non-compressed %s" % name)
            dset = hgroup.create_dataset(name, data=data)
        except TypeError:
            #print name, data.dtype
            raise

    return dset


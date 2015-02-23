# -*- coding: utf-8 -*-

"""
hdfcompress.py
==============

Helper functions for writing bitshuffled compressed datatsets
"""

import numpy as np
import h5py
from h5py import h5f, h5d, h5z, h5t, h5s, filters
try:
    from bitshuffle import h5
    USE_BITSHUFFLE = True
except ImportError:
    USE_BITSHUFFLE = False

def guess_chunk(shape):
    """ Guess the optimal chunk size for a given shape
    :param shape: shape of dataset
    :return: chunk guess (tuple)
    """
    ndim = len(shape)

    if ndim == 1:
        chunks = (min((shape[0], 1024)), )
    elif ndim == 2:
        chunks = (min((shape[0], 128)), min((shape[1], 128)))
    elif ndim == 3:
        chunks = (min((shape[0], 128)), min((shape[1], 128)),
                  min((shape[2], 16)))
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

    shape = data.shape
    dtype = data.dtype

    # Parse keyword arguments that we need to check
    compression = None
    if 'compression' in kwargs:
        compression = kwargs['compression']

    if 'chunks' not in kwargs:
        kwargs['chunks'] = guess_chunk(shape)

    #print name, shape, dtype, chunks

    if compression == 'bitshuffle':
        chunks = kwargs['chunks']
        h5.create_dataset(hgroup, name, shape, dtype, chunks,
                          filter_pipeline=(32008,),
                          filter_flags=(h5z.FLAG_MANDATORY,),
                          filter_opts=((0, h5.H5_COMPRESS_LZ4),),
                          )
    else:
        h5.create_dataset(hgroup, name, shape, dtype, **kwargs)

    hgroup[name][:] = data

    return hgroup[name]

def create_dataset(hgroup, name, data, chunks=None):
    """ Create dataset from data, will attempt to compress

    :param hgroup: h5py group in which to add dataset
    :param name: name of dataset
    :param data: data to write
    """

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
            np.complex128]

    np_types = set(np_types)

    #print name, str(data.dtype)
    if data.dtype.type in np_types and USE_BITSHUFFLE:
        #if name == 'FLUX':
        #    data = data.astype('int32')
        dset = create_compressed(hgroup, name, data, chunks)
    else:
        try:
            #print "Creating non-compressed %s" % name
            dset = hgroup.create_dataset(name, data=data)
        except TypeError:
            #print name, data.dtype
            raise

    return dset


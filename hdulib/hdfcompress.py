# -*- coding: utf-8 -*-

"""
hdfcompress.py
==============

Helper functions for writing bitshuffled compressed datatsets
"""

import numpy as np
import h5py

try:
    from h5py import h5f, h5d, h5z, h5t, h5s, filters
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
        raise RuntimeError("Couldn't handle shape %s %s" % (name, shape))

    return chunks

def create_compressed(hgroup, name, data, chunks=None):
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

    if chunks is None:
        chunks = guess_chunk(shape)

    #print name, shape, dtype, chunks

    try:
        h5.create_dataset(hgroup, name, shape, dtype, chunks,
                          filter_pipeline=(32008,),
                          filter_flags=(h5z.FLAG_MANDATORY,),
                          filter_opts=((0, h5.H5_COMPRESS_LZ4),),
                          )
    except:
        raise

    hgroup[name][:] = data

def create_dataset(hgroup, name, data, chunks=None):
    """ Create dataset from data, will attempt to compress

    :param hgroup: h5py group in which to add dataset
    :param name: name of dataset
    :param data: data to write
    """

    num_types = ["float64", "float32", "int32", "int64",
                 "complex64", "complex128", 
                 ">i4", ">i8", ">f4", ">f8"]
    num_types = set(num_types)
    
    
    #print name, str(data.dtype)
    if str(data.dtype) in num_types and USE_BITSHUFFLE:
        #if name == 'FLUX':
        #    data = data.astype('int32')
        create_compressed(hgroup, name, data, chunks)
    else:
        try:
            #print "Creating non-compressed %s" % name
            hgroup.create_dataset(name, data=data)
        except TypeError:
            #print name, data.dtype
            raise
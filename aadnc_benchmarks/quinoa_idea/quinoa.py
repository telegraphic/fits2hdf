# -*- coding: utf-8 -*-
"""
quinoa.py
=========

Create QUINOA compressed dataset.

QUINOA (QUasi Integer Noise Offset Adjustment) compression is a lossy compression
algorithm for floating point data, and is similar to the RICE-based compression
technique that FPACK uses on floating point data.

The FITS compression package FPACK quantizes floating point pixel values into
32bit integers using a linear scaling function:

    integer_value = (floating_point_value - ZERO_POINT ) / SCALE_FACTOR

This array of scaled integers is then compressed using one of the supported compression
algorithms (the default algorithm is RICE).

Basically, QUINOA applies this scaling function then applies bitshuffle compression,
instead of using RICE.

QUINOA is an experimental grain, and should not be used as your staple compression
at this stage.

COUSCOUS: COnversion to Unsigned / Signed ...
"""

import numpy as np
from scipy.signal import convolve2d
from pylab import plt

def estimate_noise(data):
    """ Estimate the RMS noise of an image

    from http://stackoverflow.com/questions/2440504/
                noise-estimation-noise-measurement-in-image

    Reference: J. Immerkaer, “Fast Noise Variance Estimation”,
    Computer Vision and Image Understanding,
    Vol. 64, No. 2, pp. 300-302, Sep. 1996 [PDF]

    """

    H, W = data.shape

    data = np.nan_to_num(data)

    M = [[1, -2, 1],
         [-2, 4, -2],
         [1, -2, 1]]

    sigma = np.sum(np.sum(np.abs(convolve2d(data, M))))
    sigma = sigma * np.sqrt(0.5 * np.pi) / (6 * (W - 2) * (H - 2))

    return sigma

def apply_dither(data, seed):
    """ Apply subtractive dither """
    np.random.seed(seed)
    dither_vals = np.random.random(data.shape)
    data = data + dither_vals
    return data

def unapply_dither(data, seed):
    """ Remove subtractive dither from image """
    np.random.seed(seed)
    dither_vals = np.random.random(data.shape)
    data = data - dither_vals
    return data


def quinoa_scale(data, q=4.0, subtractive_dither=True, seed=12345):
    """ Apply quinoa scaling to a floating-point dataset.

    data: numpy.ndarray of data to be converted.
    q: quantization parameter, default 4.0
    subtractive_dither: apply dither for subtractive dithering
    seed: change seed value
    """

    if subtractive_dither:
        data = apply_dither(data, seed)

    zero_point = np.nanmin(data)
    max_point  = np.nanmax(data)
    dyn_range = max_point - zero_point
    
    data_zeroed = data - zero_point
    
    # Compute scale factor
    noise_rms = estimate_noise(data)
    
    scale_factor = (q / noise_rms) * (2**32 / dyn_range)

    data_int = np.ceil((data_zeroed) * scale_factor).astype('uint32')

    scale_dict = {
        'zero': zero_point,
        'noise_rms': noise_rms,
        'scale_factor': scale_factor,
        'dithered': subtractive_dither,
        'seed': seed,
        'data': data_int,
        'q': q,
        'dtype': str(data_int.dtype)
    }

    return scale_dict

def quinoa_unscale(scale_dict):
    """ Unapply QUINOA scaled data """
    ss = scale_dict
    data = ss["data"].astype('float32')

    data = (data / ss["scale_factor"]) + ss["zero"]

    if ss["dithered"]:
        data = unapply_dither(data, ss["seed"])

    return data

def couscous_scale(data):
    """ Apply couscous scaling to data

    (ceiling rounding and converion to int) """

    d_max = np.nanmax(data)
    d_min = np.nanmin(data)

    if d_max <= 2**8 and d_min >= -2**8:
        scale_factor = 2**16
        data *= scale_factor
        data = np.ceil(data).astype("int32")
    if d_max <= 2**15 and d_min >= -2**15:
        data = np.ceil(data).astype("int16")
        scale_factor = 1
    elif d_max <= 2**31 and d_min >= -2**31:
        data = np.ceil(data).astype("int32")
        scale_factor = 1
    else:
        scale_factor = d_max * 2**32
        data_zeroed = (data - d_min) / scale_factor
        data = np.ceil(data_zeroed).astype("int32")

    scale_dict = {
        'data': data,
        'min': d_min,
        'max': d_max,
        'scale_factor': scale_factor,
        'dtype': str(data.dtype)

    }
    return scale_dict


if __name__ == "__main__":

    d = np.linspace(1e4, 1e5, 100)
    data = np.sin(np.outer(d, d)) * 16384
    noise = np.random.random((100,100)) / 1000
    data = data + noise
    scale_dict = quinoa_scale(data, q=0.001)
    
    data_unscaled = quinoa_unscale(scale_dict)
    
    print(scale_dict)
    print(data_unscaled)
    
    plt.figure()
    plt.subplot(2,2,1)
    plt.imshow(data)
    plt.colorbar()
    plt.subplot(2,2,2)
    plt.imshow(scale_dict["data"])
    plt.colorbar()
    plt.subplot(2,2,3)
    plt.imshow(data_unscaled)
    plt.colorbar()
    plt.subplot(2,2,4)
    plt.imshow(np.abs(data - data_unscaled) / np.max(data) * 100)
    plt.colorbar()
    plt.show()

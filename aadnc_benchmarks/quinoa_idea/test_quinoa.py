# -*- coding: utf-8 -*-
"""
test_quinoa.py
"""

from quinoa import *

def generate_data():
    d = np.linspace(1e4, 1e5, 100)
    d_range = 1e9
    noise_ratio = 1e3
    data = np.sin(np.outer(d, d)) * d_range
    noise = np.random.random((100,100)) * d_range / noise_ratio
    return data + noise

def test_dither():
    data = generate_data()
    
    data_d = apply_dither(data, 12345)
    data_u = unapply_dither(data_d, 12345)
        
    assert np.allclose(data, data_u)

def test_scaling():
    data = generate_data()
    
    scale_dict = quinoa_scale(data, q=4)
    print(scale_dict)
    #print "Noise estimate: %s" % np.max(scale_dict["data"])
    print("Max value in scaled data: %s" % np.max(scale_dict["data"]))
    unscaled = quinoa_unscale(scale_dict)
    
    precision = np.average(np.abs(data - unscaled) / np.nanmax(data)) * 100
    print("Precision: %2.2f%%" % precision)
    assert np.allclose(data, unscaled, rtol=1)
    

if __name__ == "__main__":

    test_dither()
    test_scaling()

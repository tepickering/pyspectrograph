"""CreateImage is a task to produce a 2D image generated by a spectrograph

HISTORY
20100601 SMC  First written by SM Crawford

Limitations:

"""

import numpy as np
from astropy.io import fits

from PySpectrograph.Spectrograph import *
from PySpectrograph.Spectra import *


def writeout(arr, outfile):
    # make and output the image
    hdu = fits.PrimaryHDU(arr)
    hdu.writeto(outfile)


def CreateImage(spectrum, spec, xlen=None, ylen=None):
    """CreateImage is a task  for creating a 2D spectrum of a source.
       It creates a fits image of the source given pertinent information about
       the spectrograph and spectrum

       spectrum--an Spectrum object with information about the spectrum to plot

       spec--a Spectrograph object describing a spectrograph

       xlen--Optional length for the spetrograph detector.  If not, takes the information from spec

       ylen--Optional height for the spectrograph detector.  If not, take the information from spec

    """

    # Set up the detector array--this is the output image
    if xlen is None:
        xlen = int(spec.detector.width / spec.detector.xbin / spec.detector.pix_size)
    else:
        xlen = xlen

    if ylen is None:
        ylen = int(spec.detector.height / spec.detector.ybin / spec.detector.pix_size)
    else:
        ylen = ylen

    # set up the arrays
    x_arr = np.arange(xlen)
    y_arr = np.arange(ylen)
    arr = np.zeros((ylen, xlen))

    # Convert the spectrum into pixel space
    alpha = spec.gratang
    beta = spec.gratang - spec.camang
    dw = 0.5 * 1e7 * spec.calc_resolelement(alpha, beta)
    dx = spec.detector.xpos / (spec.detector.xbin * spec.detector.pix_scale)
    dy = spec.detector.ypos / (spec.detector.ybin * spec.detector.pix_scale)
    dbeta = np.degrees(np.arctan(spec.detector.xbin *
                                 spec.detector.pix_size *
                                 (x_arr -
                                  0.5 *
                                  x_arr.max() +
                                     dx) /
                                 spec.camera.focallength))

    for j in y_arr:
        gamma = np.degrees(np.arctan(spec.detector.ybin *
                                     spec.detector.pix_size *
                                     (j -
                                      0.5 *
                                      y_arr.max() +
                                         dy) /
                                     spec.camera.focallength))
        w_arr = 1e7 * spec.calc_wavelength(alpha, beta - dbeta, gamma=gamma)
        arr[j, x_arr] = np.interp(w_arr, spectrum.wavelength, spectrum.set_dispersion(dw, nkern=50))

    return arr

# -*- coding: utf-8 -*-
"""
Reads a MISS-image and corrects the "smiley" spectral image into
a nice rectangular image.

Outputs a matrix with the vertical axis being a proxy for the scan
angle (no calibration yet). The horizontal axis is wavelength from
400nm to 700nm

For each scan angle (image row), the known emission lines are used
to first construct a mapping between wavelengths and pixel columsn.
Then the intensities for wavelengths between 400..700nm at 1nm steps
are interpolated from the image.

NOTE:
    - the wavelength calibration is based on only three points, or
      the blue, green and red emission lines
    - the "scan angle" is not calibrated at all!


Created on Fri May 10 13:30:25 2024

@author: MikkoS
"""

import os
import numpy as np
import matplotlib.pyplot as plt

#=================================================================
# A user called Felix wrote a nice short reading routine for ASCII PGM-files
# https://stackoverflow.com/questions/46944048/how-to-read-pgm-p2-image-in-python
#
# The commonly used PIL for image reading in python seems to have trouble
# handling the comments in PGM-files, even though the comments are part
# of the "standard" for PNM-format.

def readpgm(name):
    with open(name) as f:
        lines = f.readlines()

    # Ignores commented lines
    for l in list(lines):
        if l[0] == '#':
            lines.remove(l)

    # Makes sure it is ASCII format (P2)
    assert lines[0].strip() == 'P2', 'File not an ASCII PGM-file'

    # Converts data to a list of integers
    data = []
    for line in lines[1:]:
        data.extend([int(c) for c in line.split()])

    data=(np.array(data[3:]),(data[1],data[0]),data[2])
    return np.reshape(data[0],data[1])


#=================================================================


def read_miss_spectral(filename):
    im=readpgm(filename)


    # Estimate the background level from an image corner and
    # remove the pixel offset
    bg_estimate=np.mean(im[0:29,0:29])
    im=np.maximum(im-bg_estimate,0).transpose()


    # From quick calibration using auroral emission lines,
    # see plot_misspeaks.m in the Matlab source code

    bluepoly=np.poly1d([-0.000401186790506, 0.118021155830754,
                        86.670020639834831]);
    redpoly=np.poly1d([-0.0003147574819, 0.1045665634675,
                            656.6050051599582]);
    greenpoly=np.poly1d([-0.0003805469556, 0.1139447884417,
                         462.5405056759545]);

    # Create a spectral image
    # - use data between rows 70 and 270 (needs scan angle calibration!)
    # - interpolate data from 400..700nm

    scanangle=np.arange(0,200)
    wavelengths=np.arange(400,701)
    spectralimage=np.zeros([len(scanangle),len(wavelengths)])
    colIndex=np.arange(0,im.shape[1])

    for alpha in scanangle:
        row=70+alpha
        blueline=bluepoly(row)      # Locations of the auroral emission lines
        redline=redpoly(row)        # at this scan angle, or image row in raw
        greenline=greenpoly(row)    # image data
        lambdas=np.polynomial.Polynomial.fit([427.8, 557.7, 630.0],
                                             [blueline, greenline, redline],2)
        cols=lambdas(wavelengths)
        thisrowvalues=im[row,:]
        spectralvalues=np.interp(cols,colIndex,thisrowvalues)
        spectralimage[alpha,:]=spectralvalues

    return spectralimage

#---------------------------------------------------------------
# Quick test plot

if __name__ == "__main__":
    filename=os.path.join('..','MISS-20221225-162100.pgm')
    spectralimage=read_miss_spectral(filename)

    fig, ax = plt.subplots()
    ax.imshow(np.sqrt(spectralimage),cmap='plasma', aspect='auto',
              extent=[400,700, 0, 347])
    ax.set_xlabel('Wavelength [nm]')
    ax.set_ylabel('Uncalibrated angle')

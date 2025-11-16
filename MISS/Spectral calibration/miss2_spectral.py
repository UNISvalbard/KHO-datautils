# -*- coding: utf-8 -*-
"""
Read a MISS2 image and remove the "smiley". The return image has
columns corresponding to wavelengths from 400 to 690nm with 1nm
steps. The rows correspond to uncalibrated zenith angle from north
(top of image) to south (bottom of image).

Mikko Syrjäsuo/UNIS, 2025-11-16

"""
from datetime import datetime
from os.path import isfile, join, basename
from glob import glob # It might be better to get an iterator?

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib import transforms
from scipy import signal
from PIL import Image

def miss2spectral(missFile):
    """
    The estimated "smiley", see miss2_calibration.py
    Note that, in the first setup, the polynomials
    were estimated using only three auroral emission lines.
    The most serious issue is the lack of a reference in
    the blue end of the spectrum.
    TO DO: use data where the auroral blue emission line is
           also visible
    """

    p_green=np.poly1d([-0.0003996, 0.1461,544])
    p_red=np.poly1d([-0.0003619, 0.1322,797.1])
    p_red2=np.poly1d([-0.0003952, 0.1534,816.3])

    """
    Based on the testplots, the wavelength range roughly 
    from 398nm to 697nm, so let's use 400 to 690nm as the 
    range to be interpolated from the spectral image. 
    In other words, the "scan angle" or zenith angle from north
    to south is roughly from row 70 to 270.
    """

    missImage=np.array(Image.open(missFile))
    imsize=np.shape(missImage)
    im=np.fliplr(np.rot90(missImage))

    """
    Create a spectral image where each column represents a constant wavelength
    - use data between 70 to 270 rows for the zenith angle, which
      results in roughly one degree resolution along the meridian
    - interpolate new datapoints for a range 400-690nm
    """

    scanangle=np.arange(0,200) # 270-70=200
    wavelengths=np.arange(400,691)
    spectralImage=np.zeros([len(scanangle),len(wavelengths)])
    colIndex=np.arange(0,im.shape[1])

    for alpha in scanangle:
        row=70+alpha
        greenline=p_green(row)
        redline=p_red(row)
        red2line=p_red2(row)

        waves=np.polynomial.Polynomial.fit([557.7, 630.0, 636.4], [greenline,redline,red2line],2)

        cols=waves(wavelengths) # Pixel columns corresponding to wavelengths
        thisrowvalues=im[row,:]
        spectralValues=np.interp(cols, colIndex, thisrowvalues)
        spectralImage[alpha,:]=spectralValues
    return spectralImage, wavelengths


if __name__ == "__main__":
    missFile="MISS2-20251115-072315.png"

    # Get the basename for the file for the plot title
    thisbasename=basename(missFile)

    spectralImage, wavelengths = miss2spectral(missFile)
    fig, axMiss = plt.subplots(figsize=(10,6))
    fig.suptitle(thisbasename)

    pos=axMiss.imshow(np.sqrt(spectralImage),cmap='plasma', aspect='auto',
                extent=[min(wavelengths),max(wavelengths),0, 200],
                vmin=0, vmax=100)
    axMiss.set_xlabel('Wavelength [nm]')
    axMiss.set_ylabel('Uncalibrated zenith angle')
    tick_positions = np.linspace(0,200, num=7)
    tick_labels = ["South", "-60", "-30", "Zenith", "30", "60", "North"]
    axMiss.set_yticks(tick_positions)
    axMiss.set_yticklabels(tick_labels) #, fontsize = 14)
    axMiss.grid(True)
    fig.colorbar(pos, ax=axMiss, label="Counts")
    
    # A quick check to see how well the green line matches the
    # output image...
    #axMiss.axvline(x=557.7,color='g')

    plt.show()
# -*- coding: utf-8 -*-
"""
A quickly written calibration routine that uses known emission
lines visible in MISS images to estimate parameters for correcting
the "smiley" effect. The curvature of the smiley is estimated using
a 2nd degree polynomial fit to points of maximum pixel brightness within
a small range around a provided centre column.

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


def detect_emission_line(rows,col_centre, offset, image):
    """
    - find the pixel with maximum brightness within a small column range
    - use the pixel locations and given rows to fit a 2nd degree polynomial ("smiley")
    """   
    cols=[]
    for thisrow in rows:
        values=smoothimage[thisrow,(col_centre-offset):(col_centre+offset+1)]
        thiscol=np.argmax(values)+col_centre-offset
        cols.append(thiscol)
        #print(thisrow, thiscol, values)
        thisimage[thisrow,(col_centre-offset):(col_centre+offset+1)]=2500
        

    z=np.polyfit(rows, cols,2)
    p_fit=np.poly1d(z)
    return p_fit

missFile="MISS2-20251115-072315.png"
missImage=np.array(Image.open(missFile))

# The raw data has 1039 rows with 347 columns, do some flipping 
thisimage=np.fliplr(np.rot90(missImage))

"""
There are several auroral spectral lines visible in the image
Approx. col 558 - 557.7nm
            668 - 589.0nm (Sodium line, light pollution from Mine 7)
            807 - 630.0nm
            829 - 636.4nm
"""

# Get the basename for the file for the plot title
thisbasename=basename(missFile)

"""
Process the image to filter noisy pixels out.
- the first one is used for the plot
- the second is an even more smoothed image for detecting
  the locations of the spectral lines more reliably
"""
thisimage=signal.medfilt2d(thisimage.astype('float32'))
smoothimage=signal.medfilt2d(thisimage.astype('float32'))

# Estimate the background from the side of the image and
# subtrack that as well
#bg=np.average(thisimage[0:30,0:30])
#thisimage=np.maximum(0,thisimage-bg)

# Green line
rows=range(80,270,15)
col_centre=556
offset=10
p_green=detect_emission_line(rows,col_centre, offset, smoothimage)

# Red line
col_centre=807
p_red=detect_emission_line(rows,col_centre,offset, smoothimage)

# Red double line
col_centre=829
p_red2=detect_emission_line(rows,col_centre,offset, smoothimage)

# Plot the spectral image

fig, axMiss = plt.subplots(figsize=(10,6))
fig.suptitle(thisbasename)

axMiss.imshow(np.sqrt(thisimage),cmap='gray', aspect='auto')#,
            #extent=[min(yp),max(yp), 347, 0]) #plasma

# Draw a couple of estimated emission lines for green, red and red-doublet
# for a visual sanity check
y=np.arange(50,300)
xgreen=p_green(y) # Estimate the pixel column for green line given the pixel row 
axMiss.plot(xgreen,y,color='g')

xred=p_red(y)
axMiss.plot(xred,y,color='r')

xred2=p_red2(y)
axMiss.plot(xred2,y,color='m')

"""
Do a quick estimate of where the auroral blue (427.8nm) and Sodium 
line (589.0nm) should be in the image
- use the green, red and red2 locations for each row to compute a linear fit
  in the column direction
- estimate the location (pixel columns) given the wavelength 589.0nm
"""
col_blue=[]
col_sodium=[]
for thisrow in rows:
    xgreen=p_green(thisrow)
    xred=p_red(thisrow)
    xred2=p_red2(thisrow)
    fit_lambda=np.polyfit([557.7, 630.0, 636.5],[xgreen,xred,xred2],1)
    p_lambda=np.poly1d(fit_lambda)
    col_blue.append(p_lambda(427.8))
    col_sodium.append(p_lambda(589.0))
    wavelengths=np.polyfit([xgreen,xred,xred2],[557.7, 630.0, 636.5],1)
    p_waves=np.poly1d(wavelengths)

z=np.polyfit(rows, col_blue,2)
p_blue=np.poly1d(z)
x=p_blue(y)
axMiss.plot(x,y,color='b')

z=np.polyfit(rows, col_sodium,2)
p_sodium=np.poly1d(z)
x=p_sodium(y)
axMiss.plot(x,y,color='c')

plt.show()

# Print the calibration polynomials to be copied
# to miss2_spectral.py
print("----------------------------")
print("p_green=")
print(p_green)

print("----------------------------")
print("p_red=")
print(p_red)

print("----------------------------")
print("p_red2=")
print(p_red2)

print("----------------------------")

"""
Save the latest MISS image with a vertically binned plot for web

"""

from os.path import basename

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from matplotlib import transforms
from scipy import signal

#=================================================================
# A user called Felix wrote a nice short reading routine for ASCII PGM-files
# https://stackoverflow.com/questions/46944048/how-to-read-pgm-p2-image-in-python

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


#=====================================================
# - find the latest captured image to process
# - write it to a suitable location such as web server...


file=open('c:\\Users\\mikkos\\MISS\\latestfilename.txt','r')
webfile='z:\\kho\\MISS\\latestmiss.png'
#webfile='latestmiss.png'

latestFile=file.readline().strip()
file.close()
#print(latestFile)

# Use the name of the file for the plot title

thisbasename=basename(latestFile)

# The filename uses local path at the MISS instrument computer, 
# so change the path to point to the shared disk if ran from 
# another computer during development...

#latestFile=latestFile.replace('D:\\MISSTEST','s:')
#latestFile=latestFile.replace('C:\\Users\\mikkos\\MISS','s:')

#print(latestFile)

thisimage=readpgm(latestFile)

# Use median filtering to reduce noise. Also,
# estimate the background from the side of the image and
# subtrack that to get the black level close to zero.

thisimage=signal.medfilt2d(thisimage.astype('float32'))
bg=np.average(thisimage[0:30,0:30])
thisimage=np.maximum(0,thisimage-bg)
thisimage=thisimage.transpose()


# Calibration peaks obtained using a calibration lamp at KHO

peaks=np.array([435.8, 546.1])
peakcolumns=np.array([123, 441])/3 # We are using 4x binning

z=np.polyfit(peakcolumns, peaks,1)
p=np.poly1d(z)

xp=np.arange(0,thisimage.shape[0])
yp=p(xp)


fig, axMiss = plt.subplots(figsize=(6,6))
fig.suptitle(thisbasename)

# The image itself
axMiss.imshow(np.sqrt(thisimage),cmap='gray', aspect='auto',
              extent=[min(yp),max(yp), 347, 0]) #plasma
plt.xlabel("Wavelength (nm)")
plt.ylabel("Pixel row number")

# Sideplots for vertically and horizontally binned values
# (copy & paste + modified from Matplotlib Scatter histogram example)
# - create new axes on the right and on the top of the image axes
# - the first argument of the new method is the the height (width)
#   of the axis to be created in inches

divider=make_axes_locatable(axMiss)
axTop=divider.append_axes("top", 1.2, pad=0.5)
axRight=divider.append_axes("right", 1.2, pad=0.5)

# Hide extra labels to clean the plot
axTop.xaxis.set_tick_params(labelbottom=False)
axRight.yaxis.set_tick_params(labelleft=False)


# Vertically and horizontally binned values
# - normalise to maximum values
# - go through the necessary moves to get the extra plots around the
#   main plot

fvb=np.sum(thisimage,axis=0)
fvb=fvb/np.max(fvb)
fvb=np.sqrt(fvb)
axTop.plot(fvb)
axTop.grid(True)

fhb=np.sum(thisimage,axis=1)
fhb=fhb/np.max(fhb)
fhb=np.sqrt(fhb)


base=axRight.transData
rot=transforms.Affine2D().rotate_deg(-90)
axRight.plot(fhb,transform=rot+base)
axRight.grid(True)

plt.savefig(webfile)
#plt.show()

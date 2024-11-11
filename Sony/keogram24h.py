# -*- coding: utf-8 -*-
"""

Create a keogram from the data covering the last 24 hours.

This script uses the filename conventions for the Sony A7s all-sky camera
operated at Kjell Henriksen Observatory (KHO).

The Sony A7S filename convention is fixed to

LYR-Sony-DDMMYY_HHMMSS.jpg

so, for example, LYR-Sony-010124_032032.jpg refers to an image captured on 1 Jan, 2024
at 03:20:32 UT. Similarly, the files are stored in a directory structure YYYY/MM/DD

@author: MikkoS
"""

import datetime as dt
import os
import numpy as np
import re
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.dates as mdates
from PIL import Image
from glob import glob
import sys

#=======================

savefilename=os.path.join('/mnt','khoweb','kho','Quicklooks','realtimekeo__sony_RGB.png')

basepath=os.path.join('/Data','Quicklooks')

mytimenow=dt.datetime.now(dt.UTC)-dt.timedelta(minutes=1)
mytimenow=mytimenow.replace(second=0,microsecond=0)
#print(mytimenow)

datapoints=[mytimenow-dt.timedelta(minutes=x) for x in range(0,24*60)]
starttime=min(datapoints)
endtime=max(datapoints)

myfiles=[]
mytimes=[]
# Search for any image within the minute rather than just the one with zero seconds
for mytime in datapoints:
    filepath=os.path.join(basepath,mytime.strftime('%Y'), mytime.strftime('%m'),mytime.strftime('%d'))
    globpath=os.path.join(filepath,mytime.strftime('LYR-Sony-%Y%m%d_%H%M??.jpg'))
    globfiles=glob(globpath)
    if(len(globfiles)==0):
       continue
    filename=globfiles[0]    # Just choose the first one
    myfiles.append(filename)
    mytimes.append(mytime)

if(len(myfiles)==0):
    print('No files')
    sys.exit()

keogram=np.zeros((480,24*60,3))
keogram_slice_used=np.zeros(24*60) 

for i in np.arange(0,len(myfiles)):
    thisfile=myfiles[i]
    thistime=mytimes[i]
    delta=endtime-thistime
    index=24*60-1-round(delta.seconds/60)-24*60*delta.days
    #if keogram_slice_used[index]==1:
    #    continue
    try:
        im=np.asarray(Image.open(thisfile))
        slice=im[:,240,:]
        keogram[:,index,:]=slice/255.0
        keogram_slice_used[index]=1
        #print(thistime,thisfile,index)
    except:
        print(f"Problems with {thisfile}")
        continue

fig, (ax3) = plt.subplots(1,1)
ax3.set_title('Sony A7s (KHO/UNIS) \nFrom '+
    min(datapoints).strftime('%Y-%m-%d %H:%M UT')+ ' to ' +
    max(datapoints).strftime('%Y-%m-%d %H:%M UT'), fontsize=18)

pngwidth=800
pngheight=400
mydpi=100
fig.set_size_inches(pngwidth/mydpi,pngheight/mydpi)
hours=mdates.HourLocator(byhour=range(0,24,2))
d_fmt=mdates.DateFormatter('%H:%M')
xlims=mdates.date2num([starttime,endtime])

ax3.set_ylabel('Zenith angle (positive north)')
plt.sca(ax3)

ax3.xaxis_date()
ax3.xaxis.set_major_locator(hours)
ax3.xaxis.set_major_formatter(d_fmt)

plt.yticks(np.arange(-90,90+45,45),np.arange(-90,90+45,45))

c=ax3.imshow(keogram,extent=[xlims[0],xlims[1],-90,90], aspect='auto')
fig.tight_layout()
plt.savefig(savefilename,dpi=mydpi)
#print(f"Stored {savefilename}")


# -*- coding: utf-8 -*-
"""

Create keograms for all sorts of instruments, but mainly auroral imagers.
This particular script is written for Sony A7S images from KHO, but it
should be easy to modify the file reading parts to accommodate other cameras.

@author: MikkoS
"""

import glob
import numpy as np
import os
import re
import datetime as dt
from PIL import Image
import matplotlib.pyplot as plt
import shutil


def keogramOneDaySony(year,month,day):
    monthpath=os.path.join('/','home','mikkos','Data',f'{year:04}',f'{month:02}')
    daypath=os.path.join(monthpath,f'{day:02}')

    keoname=os.path.join(monthpath,f'LYR-Sony-{year}{month:02}{day:02}.jpg')
    if os.path.isfile(keoname)==True:
        #print(f'Keogram {keoname} exists, skipping...')
        return

    webpath=os.path.join('/','mnt','khoweb','kho','Keograms','Sony')
    webname=os.path.join(webpath,f'LYR-Sony-{year}{month:02}{day:02}.jpg')

    imagefiles=glob.glob(os.path.join(daypath,"*.jpg"))
    imagefiles.sort()

    # The Sony A7S filename convention is fixed to
    # LYR-Sony-YYYYMMDD__HHMMSS.jpg, so, for example,
    #

    # The keogram is simply a fixed size 24-h plot with one-minute resolution.
    # We will use a "helper" vector to avoid having to read every file: a keogram
    # is a summary plot that provides an overview, not details.

    keogram=np.zeros((670,24*60,3))    # A keogram is an RGB image
    keogram_slice_used=np.zeros(24*60)

    filesread=0
    for i in np.arange(0,len(imagefiles)):
        thisfile=os.path.basename(imagefiles[i])

        # First check whether the name is of correct format and then check
        # for a valid date and time before continuing with the keogram

        filepattern=r"LYR-Sony-(\d\d\d\d)(\d\d)(\d\d)_(\d\d)(\d\d)(\d\d).jpg"
        checkname=re.match(filepattern, thisfile)
        if checkname == None:
            continue

        # There is probably a more stylish way to do this in python
        # but at least this is easy to understand...
        validname=re.split(filepattern, thisfile)

        fileday=int(validname[3])
        filemonth=int(validname[2])
        fileyear=int(validname[1])

        filehh=int(validname[4])
        filemm=int(validname[5])
        filess=int(validname[6])

        # Check the date is actually a valid date
        datefromfile=f'{fileyear}-{filemonth:02}-{fileday:02} {filehh:02}:{filemm:02}:{filess:02}'

        try:
            dt.datetime.strptime(datefromfile,'%Y-%m-%d %H:%M:%S')
        except ValueError:
            print('Funny date and time in',thisfile)
            continue


        # Read the image file and copy a meridional slice of the
        # image to a correct location in the keogram. 
        # Use seconds to round to the nearest full minute, but limit the index
        # to the current day

        index=min(60*filehh+filemm+round(filess/60),24*60-1)

        if keogram_slice_used[index]==1:
            # print("Skipping",thisfile)
            continue

        # print(i,datefromfile,index)

        # The following should probably be replaced with a code that only takes
        # the slice *inside* of the field-of-view.
        try:
            im=np.asarray(Image.open(imagefiles[i]).resize((700,700)))
            slice=im[22:692,350,:]
        except:
            print('Problems with',thisfile)
            continue

        keogram[:,index,:]=slice
        keogram_slice_used[index]=1
        filesread=filesread+1


    fig, (ax) = plt.subplots(1,1)
    pngwidth=1200
    pngheight=800
    mydpi=100
    fig.set_size_inches(pngwidth/mydpi,pngheight/mydpi)

    ax.set_xlabel('Time (UT)')
    ax.set_ylabel('Zenith angle')
    plt.sca(ax)

    plt.xticks(np.arange(0,24,1)*60,np.arange(0,24,1))
    ax.set_ylim(ymax=670)
    # Ticks every 30 degrees
    ss=670/180*30
    plt.yticks(np.arange(0,670+1,step=ss),['South',-60,-30,'Zenith',30,60,'North'])

    ax.set_title(f'KHO/UNIS Sony A7S {year}-{month:02}-{day:02}', fontsize=14)

    ax.imshow(np.flipud(keogram/255), aspect='auto')

    fig.tight_layout()
    #plt.show()

    plt.savefig(keoname, dpi=mydpi)

    # Copy to web
    if os.path.isfile(webname)==True:
        #print(f'Keogram {webname} exists, skipping...')
        return

    shutil.copyfile(keoname,webname)



#=====================================================================
# Create keograms for the past two weeks only. If there are obvious
# gaps in the daily keograms, then one should be able to figure it
# out within two weeks, right? :-)
# Any missing keograms can/should be then created manually.

#year=2024
#month=10

mydt=dt.datetime.now(dt.UTC)

for i in range(1,15):
    checkdt=mydt-dt.timedelta(days=i)
    year=checkdt.year
    month=checkdt.month
    day=checkdt.day
    keogramOneDaySony(year,month,day)



# -*- coding: utf-8 -*-
"""

This short script browses through all Sony images and creates
any missing "thumbnail" images suitable for AuroraX (480x480 jpg)

@author: MikkoS
"""

import glob
import numpy as np
import os
import re
import datetime as dt
from PIL import Image, ImageDraw, ImageFont
import cv2

def oneDayThumbnails(year,month,day,overWriteExisting=False):
    basepath=os.path.join('/','home','mikkos','Data',f'{year:04}', f'{month:02}',
                          f'{day:02}')
    imagefiles=glob.glob(os.path.join(basepath,'*.jpg'))
    imagefiles.sort()

    auroraXpath=os.path.join('/','home','mikkos','Data','Quicklooks')
    
    # The Sony A7S filename convention is fixed to
    # LYR-Sony-DDMMYY_HHMMSS.jpg, so, for example,
    # LYR-Sony-050124_032032.jpg refers to an image captured on 5 Jan, 2024
    # at 03:20:32 UT
    #
    # The corresponding AuroraX thumbnail for the is named in a more
    # conventional way:
    # 
    # LYR-Sony-20240105-032032.jpg

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


        # Create a new directory if needed
        auroraXdir=os.path.join(auroraXpath,f'{fileyear}',f'{filemonth:02}',f'{fileday:02}')
        auroraXname=f'LYR-Sony-{fileyear}{filemonth:02}{fileday:02}_{filehh:02}{filemm:02}{filess:02}.jpg'
        auroraXthumb=os.path.join(auroraXdir,auroraXname)

        if overWriteExisting==False:
            if os.path.isfile(auroraXthumb)==True:
                print(f'    {auroraXname} exists, skipping...')
                continue
        try:
            os.makedirs(auroraXdir) # Create possibly missing subdirectories
        except FileExistsError:
            pass

        # Our scientists preferred the CV2 library to PIL for resizing the images...
        image=cv2.imread(imagefiles[i])
        w=480
        h=480
        resized_image=cv2.resize(image,(w,h),interpolation=cv2.INTER_NEAREST)
        #resized_image=cv2.resize(image,(w,h),interpolation=cv2.INTER_LANCZOS4)

        # Add captions: the text writing routines in PIL are much more
        # flexible...
        cv2_im=cv2.cvtColor(resized_image,cv2.COLOR_BGR2RGB)
        im=Image.fromarray(cv2_im)

        font1base=r"/usr/share/fonts/opentype/noto" 
        font2base=r"/usr/share/fonts/truetype/ubuntu"
        font1=ImageFont.truetype(os.path.join(font1base,"NotoSansCJK-Bold.ttc"),20)
        font2=ImageFont.truetype(os.path.join(font2base,"UbuntuMono-R.ttf"),18)
        d=ImageDraw.Draw(im)
        d.text((5,3),"UNIS/KHO", font=font1, fill=(255,255,255))
        d.text((5,30),"Sony A7s", font=font1, fill=(255,255,255))
        d.text((5,460),f'{fileyear}-{filemonth:02}-{fileday:02}', font=font2, fill=(255,255,255))
        d.text((365,460),f'{filehh:02}:{filemm:02}:{filess:02} UT', font=font2, fill=(255,255,255))
        d.text((440,3)," N ", font=font2, fill=(255,255,255))
        d.text((440,3+16),"E W", font=font2, fill=(255,255,255))
        d.text((440,3+16+16)," S ", font=font2, fill=(255,255,255))
        im.save(auroraXthumb,"JPEG", quality=85, optimize=True)
        print(f'Created {auroraXthumb}')
#        with open(os.path.join(auroraXpath,"latest_thumbnail.txt"),'w') as f:
#            f.write(f'{auroraXthumb}')


#=====================================================================
# Manual keograms before archiving to NIRD...

for day in np.arange(1,32):
    oneDayThumbnails(2024,10,day)


#years=(2016,2017,2018,2019,2020,2021,2022,2023,2024)
#for year in years:
#    for month in (1,2,3,4,10,11,12):
#        for day in np.arange(1,32):
#            oneDayThumbnails(year,month,day,overWriteExisting=True)


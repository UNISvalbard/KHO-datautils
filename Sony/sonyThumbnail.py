# -*- coding: utf-8 -*-
"""

Given a filename pointing to a Sony A7s all-sky image, create a thumbnail image
with appropriate timestamp etc.

@author: MikkoS
"""

import sys
#import glob
import numpy as np
import os
import re
import datetime as dt
from PIL import Image, ImageDraw, ImageFont
#import cv2

def oneThumbnail(imagefile,overWriteExisting=False):
    auroraXpath=os.path.join('/','home','mikkos','Data','Quicklooks')
    
    # The all-sky images use a strict filename convention
    # 
    # LYR-Sony-YYYYMMDD-HHMMSS.jpg

    thisfile=os.path.basename(imagefile)
    # First check whether the name is of correct format and then check
    # for a valid date and time before continuing with the keogram

    filepattern=r"LYR-Sony-(\d\d\d\d)(\d\d)(\d\d)_(\d\d)(\d\d)(\d\d).jpg"
    checkname=re.match(filepattern, thisfile)
    if checkname == False:
        return

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
        return


    # Create a new directory if needed
    auroraXdir=os.path.join(auroraXpath,f'{fileyear}',f'{filemonth:02}',f'{fileday:02}')
    auroraXname=f'LYR-Sony-{fileyear}{filemonth:02}{fileday:02}_{filehh:02}{filemm:02}{filess:02}.jpg'
    auroraXthumb=os.path.join(auroraXdir,auroraXname)

    if overWriteExisting==False:
        if os.path.isfile(auroraXthumb)==True:
            print(f'    {auroraXthumb} exists, skipping...')
            return
    try:
        os.makedirs(auroraXdir) # Create possibly missing subdirectories
    except FileExistsError:
        pass

    # Add captions: the text writing routines in PIL are much more
    # flexible...

    with Image.open(imagefile).resize((480,480)) as im:
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


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("sonyThumbnail [filename]")

    imagefile=sys.argv[1]
    oneThumbnail(imagefile,overWriteExisting=True)



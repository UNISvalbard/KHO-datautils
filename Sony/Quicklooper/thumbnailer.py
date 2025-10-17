# -*- coding: utf-8 -*-
"""

A quick routine that "watches" /Data/latest_filename.txt to detect a new image. 
  - any changes trigger the creation of a new thumbnail image with relevant captions
  - the thumbnail image will also be copied to web server

@author: MikkoS
"""

import os
import time
import sys
import numpy as np
import re
import datetime as dt
from PIL import Image, ImageDraw, ImageFont
import shutil

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
    # If the image is complete white/black, then PIL may treat the image as greyscale image,
    # so ensure it is read as a colour image.

    with Image.open(imagefile).convert("RGB").resize((480,480),resample=Image.Resampling.LANCZOS) as im:
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
        shutil.copy(auroraXthumb,"/mnt/khoweb/kho/Quicklooks/kho_sony.jpg")
        print(f'Created {auroraXthumb} (copied to web)')
 
"""
Keep an eye on changes of a file, create new thumbnails when necessary.

"""

def detect_file_changes(file_path, interval=1):
    last_modified = os.path.getmtime(file_path)
    try:
        while True:
            current_modified = os.path.getmtime(file_path)
            if current_modified != last_modified:
                print("File has changed!")
                last_modified = current_modified
                with open(file_path) as file:
                    newfile=file.readline().strip()
                    print(f"Latest image file is *{newfile}*")
                    oneThumbnail(newfile)
            time.sleep(interval)
    except KeyboardInterrupt:
        return


if __name__ == "__main__":
   watch_file="/Data/latest_filename.txt"
   print("Sony thumbnailer starting...")
   detect_file_changes(watch_file)
   print("...done.")



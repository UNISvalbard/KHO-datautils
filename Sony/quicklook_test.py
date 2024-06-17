# -*- coding: utf-8 -*-
"""
Created on Fri Jun 14 11:18:35 2024

@author: MikkoS

The first version of the sony2aurorax script produces blurry images!!!
This short script reads a full res raw image and saves it as a resized smaller
image using various methods...

"""
from PIL import Image, ImageDraw, ImageFont
import cv2

filename='LYR-Sony-011223_084008.jpg'
fileyear=2023
filemonth=12
fileday=1
filehh=8
filemm=40
filess=8

with Image.open(filename).resize((480,480)) as im:
    font1=ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf",20)
    font2=ImageFont.truetype(r"C:\Windows\Fonts\courbd.ttf",16)
    d=ImageDraw.Draw(im)
    d.text((5,3),"UNIS/KHO", font=font1, fill=(255,255,255))
    d.text((5,30),"Sony A7s", font=font1, fill=(255,255,255))
    d.text((5,460),f'{fileyear}-{filemonth:02}-{fileday:02}', font=font2, fill=(255,255,255))
    d.text((365,460),f'{filehh:02}:{filemm:02}:{filess:02} UT', font=font2, fill=(255,255,255))
    d.text((440,3)," N ", font=font2, fill=(255,255,255))
    d.text((440,3+16),"E W ", font=font2, fill=(255,255,255))
    d.text((440,3+16+16)," S ", font=font2, fill=(255,255,255))
    im.save('test_baseline.jpg',"JPEG")
    print('Created a basic quicklook image')

with Image.open(filename).resize((480,480),resample=Image.Resampling.NEAREST) as im:
    font1=ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf",20)
    font2=ImageFont.truetype(r"C:\Windows\Fonts\courbd.ttf",16)
    d=ImageDraw.Draw(im)
    d.text((5,3),"UNIS/KHO", font=font1, fill=(255,255,255))
    d.text((5,30),"Sony A7s", font=font1, fill=(255,255,255))
    d.text((5,460),f'{fileyear}-{filemonth:02}-{fileday:02}', font=font2, fill=(255,255,255))
    d.text((365,460),f'{filehh:02}:{filemm:02}:{filess:02} UT', font=font2, fill=(255,255,255))
    d.text((440,3)," N ", font=font2, fill=(255,255,255))
    d.text((440,3+16),"E W ", font=font2, fill=(255,255,255))
    d.text((440,3+16+16)," S ", font=font2, fill=(255,255,255))
    im.save('test_resample_nearest.jpg',"JPEG",quality=80,optimize=True)
    print('Created a nearest neighbour quicklook image')

with Image.open(filename).resize((480,480),resample=Image.Resampling.BILINEAR) as im:
    font1=ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf",20)
    font2=ImageFont.truetype(r"C:\Windows\Fonts\courbd.ttf",16)
    d=ImageDraw.Draw(im)
    d.text((5,3),"UNIS/KHO", font=font1, fill=(255,255,255))
    d.text((5,30),"Sony A7s", font=font1, fill=(255,255,255))
    d.text((5,460),f'{fileyear}-{filemonth:02}-{fileday:02}', font=font2, fill=(255,255,255))
    d.text((365,460),f'{filehh:02}:{filemm:02}:{filess:02} UT', font=font2, fill=(255,255,255))
    d.text((440,3)," N ", font=font2, fill=(255,255,255))
    d.text((440,3+16),"E W ", font=font2, fill=(255,255,255))
    d.text((440,3+16+16)," S ", font=font2, fill=(255,255,255))
    im.save('test_resample_bilinear.jpg',"JPEG")
    print('Created a bilinear quicklook image')

with Image.open(filename).resize((480,480),resample=Image.Resampling.BICUBIC) as im:
    font1=ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf",20)
    font2=ImageFont.truetype(r"C:\Windows\Fonts\courbd.ttf",16)
    d=ImageDraw.Draw(im)
    d.text((5,3),"UNIS/KHO", font=font1, fill=(255,255,255))
    d.text((5,30),"Sony A7s", font=font1, fill=(255,255,255))
    d.text((5,460),f'{fileyear}-{filemonth:02}-{fileday:02}', font=font2, fill=(255,255,255))
    d.text((365,460),f'{filehh:02}:{filemm:02}:{filess:02} UT', font=font2, fill=(255,255,255))
    d.text((440,3)," N ", font=font2, fill=(255,255,255))
    d.text((440,3+16),"E W ", font=font2, fill=(255,255,255))
    d.text((440,3+16+16)," S ", font=font2, fill=(255,255,255))
    im.save('test_resample_bicubic.jpg',"JPEG")
    print('Created a bicubic quicklook image')

with Image.open(filename).resize((480,480),resample=Image.Resampling.LANCZOS) as im:
    font1=ImageFont.truetype(r"C:\Windows\Fonts\arialbd.ttf",20)
    font2=ImageFont.truetype(r"C:\Windows\Fonts\courbd.ttf",16)
    d=ImageDraw.Draw(im)
    d.text((5,3),"UNIS/KHO", font=font1, fill=(255,255,255))
    d.text((5,30),"Sony A7s", font=font1, fill=(255,255,255))
    d.text((5,460),f'{fileyear}-{filemonth:02}-{fileday:02}', font=font2, fill=(255,255,255))
    d.text((365,460),f'{filehh:02}:{filemm:02}:{filess:02} UT', font=font2, fill=(255,255,255))
    d.text((440,3)," N ", font=font2, fill=(255,255,255))
    d.text((440,3+16),"E W ", font=font2, fill=(255,255,255))
    d.text((440,3+16+16)," S ", font=font2, fill=(255,255,255))
    im.save('test_resample_lanczos.jpg',"JPEG",quality=80,optimize=True)
    print('Created a lanczos quicklook image')

image=cv2.imread(filename)
w=480
h=480
resized_image=cv2.resize(image,(w,h),interpolation=cv2.INTER_NEAREST_EXACT)
cv2.imwrite('test_cv2-nearest_exact.jpg',resized_image)

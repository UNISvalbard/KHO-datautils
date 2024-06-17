# -*- coding: utf-8 -*-
"""
Created 2024-05-21

A quick script to copy the first Sony thumbnail image from each hour
of observation. The script is used to generate a nice compact set of
images for evaluating the cloudyness in the sky.

@author: MikkoS
"""



import glob
import numpy as np
import os
import shutil

def oneDayPruning(year,month,day):
    basepath=os.path.join("D:\\","KHO","Sony","Quicklooks",
                          f'{year:04}', f'{month:02}',f'{day:02}')

    targetpath=os.path.join("D:\\","KHO","Sony","OneHourResolution",
                          f'{year:04}', f'{month:02}',f'{day:02}')

    print(targetpath)

    for hh in np.arange(0,24):
        filename=f'LYR-Sony-{year:04}{month:02}{day:02}_{hh:02}*.jpg'
        imagefiles=glob.glob(os.path.join(basepath,filename))
        imagefiles.sort()
        if len(imagefiles)>=1:
            oneFile=imagefiles[0]
            oneFileBase=os.path.basename(oneFile)
            print(oneFile)
            destinationfile=os.path.join(targetpath,oneFileBase)
            #print(destinationfile)
            
            if os.path.isfile(destinationfile)==True:
                print('    Already copied, skipping...')
                continue
            
            try:
                 os.makedirs(targetpath) # Create possibly missing subdirectories
            except FileExistsError:
                 pass
            
            shutil.copy(oneFile,targetpath)
    

# =================================================================


year=2018
for month in np.arange(1,13):
    for day in np.arange(1,31):
        oneDayPruning(year,month,day)


# years=(2018,2019,2020,2021,2022,2023,2024)
# for year in years:
#     for month in (1,2,3,4,10,11,12):
#         for day in np.arange(1,32):
#             oneDayPruning(year,month,day)


# -*- coding: utf-8 -*-
"""
A short script for creating a bat-file for archival of Sony data
to NIRD. The earlier tar.gz-files have a broken directory structure. The
intention is that when unpacking the archived files, the images will be
in yearly, then monthly and then daily directories like this:

YYYY/MM/DD/Images/*.jpg

Created on Tue Jul  9 09:45:04 2024

@author: MikkoS
"""

import os

year=2024
batfile=f'archive-{year:04}.bat'
with open(batfile,"w") as outputfile:
    for month in range(1,13,1):
        for day in range(1,32,1):
            datapath=os.path.join(f'{year:04}', f'{month:02}',
                                  f'{day:02}','Images')
            if os.path.isdir(datapath)==True:
                tarball=f'sony-{year:04}{month:02}{day:02}.tgz'
                if os.path.isfile(tarball)==True:
                    print(f'{tarball} exists, skipping...')
                outputfile.write(f'tar cfvz {tarball} {datapath}\n')


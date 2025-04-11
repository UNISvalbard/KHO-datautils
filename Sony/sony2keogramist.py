import os
import numpy as np
from datetime import datetime, timedelta
from PIL import Image
import shutil
import time

dataYear = 2025

for dataMonth in range(1, 3):
    for dataDay in range(1,31):
        ts = None
        start_time = time.time()
        
        imgpath = os.path.join('/Data',  'Quicklooks', str(dataYear), 
                               f'{dataMonth:02d}', f'{dataDay:02d}')
        
        img_files = [f for f in os.listdir(imgpath) if f.endswith('.jpg')]
        
        auroraxpath = os.path.join('/Data', 'AuroraX', 'unis', 'kho_sony', 
                                   str(dataYear), f'{dataMonth:02d}', f'{dataDay:02d}')
        
        if os.path.exists(auroraxpath):
            print(f'Data exists, skipping {auroraxpath}')
            continue
        
        os.makedirs(auroraxpath)
        
        framepath = os.path.join('/dev/shm/Frames') #auroraxpath, 'Frames')
        if not os.path.exists(framepath):
            os.makedirs(framepath)
        
        N = len(img_files)
        
        if ts is None:
            print('Creating timelist...')
            ts = np.full(N, np.nan)
            
            for i, filename in enumerate(img_files):
                # Parse the filename for timestamp info
                year = filename[9:13]
                month = filename[13:15]
                day = filename[15:17]
                hh = filename[18:20]
                mm = filename[20:22]
                ss = filename[22:24]
                
                if i % 100 == 0:
                    timecaption = f'{year}-{month}-{day} {hh}:{mm}:{ss} UT'
                    print(f' - {i} {timecaption}')
                    time.sleep(0.01)
                
                ts[i] = int(hh) * 3600 + int(mm) * 60 + int(ss)
            
            print('Timelist ready!')
        
        print('Creating keogram...')
        keogram = 255 * np.ones((480, 8640, 3), dtype=np.uint8)  # Empty and white keogram
        
        ephname = os.path.join(auroraxpath, f'ephemeris_kho_sony_{dataYear}{dataMonth:02d}{dataDay:02d}.txt')
        
        with open(ephname, 'w') as fileID:
            fileID.write('# program: UNIS/KHO\n')
            fileID.write('# platform: Longyearbyen\n')
            fileID.write('# instrument_type: colour ASI\n')
            fileID.write('# geo_lat: 78.148\n')
            fileID.write('# geo_lon: 16.043\n')
            fileID.write('timestamp\n')
            
            startOfDay = datetime(dataYear, dataMonth, dataDay, 0, 0, 0)
            
            # 12-s intervals = 5 images/minute -> 5*60*24=7200 images per day
            # 10-s intervals = 6 images/minute -> 6*60*24=8640 images per day

            for thistime in range(8640):  # 0 to 7199 (for each 12 seconds)
                thisseconds = thistime * 10  # Each time slot corresponds to 12s
                deltas = np.abs(thisseconds - ts)
                min_delta, ind = np.min(deltas), np.argmin(deltas)
                
                thisframe = 255 * np.ones((480, 480, 3), dtype=np.uint8)   # Empty white videoframe
                if min_delta < 20:
                    # Read the image corresponding to the minimum delta
                    filename = img_files[ind]
                    img = np.array(Image.open(os.path.join(imgpath, filename)), dtype=np.float64)
                    keogram[:, thistime, :] = img[:, 240, :]  # N-S slice
                    
                    mytime = startOfDay + timedelta(seconds=thisseconds)
                    mytimestamp = mytime.strftime('%Y-%m-%dT%H:%M:%S')
                    fileID.write(f'{mytimestamp}\n')
                    
                    thisframe = img
                    
                    if thistime % 100 == 0:
                        print(f'{thistime}\t{mytimestamp}\t{filename}')
                
                framename = os.path.join(framepath, f'frame{thistime:04d}.jpg')
                Image.fromarray(np.uint8(thisframe)).save(framename)
        
        # Save keogram
        keoname = os.path.join(auroraxpath, f'{dataYear}{dataMonth:02d}{dataDay:02d}__kho_sony_hires-keogram.jpg')
        Image.fromarray(keogram).save(keoname)
        
        mp4name = os.path.join(auroraxpath, f'{dataYear}{dataMonth:02d}{dataDay:02d}_unis_kho_sony-rgb.mp4')

        os.system(f'/home/mikkos/bin/createMovie2pass.sh {mp4name}')
        os.system('rm -rf /dev/shm/Frames')
        os.system('rm ffmpeg2pass*.log*')
        elapsed_time = time.time() - start_time
        print(f'Time taken: {elapsed_time:.2f} seconds')


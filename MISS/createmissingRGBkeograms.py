"""
Traverse the MISS data directory and check for any missing keograms
- create all missing ones

"""

import datetime
from os.path import isfile, join, basename, isdir

from glob import glob # It might be better to get an iterator?

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
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


#=================================================================

# Form the path to the data files and list the files that
# appear to be correct (i.e. pgm-files)

def createKeogram(basepath, myday, savefilename):
    #basepath='D:\\MISSTEST'
    #myday=datetime.date(2017,12,18) #time.utcnow()

    print('Checking data for', myday)
    dirpath=join(myday.strftime('%Y'),myday.strftime('%m'),myday.strftime('%d'))
    globpath=join(basepath,dirpath,'MISS-????????-??????.pgm')
    #print(globpath)
    myfiles=glob(globpath)

    if(len(myfiles)==0):
        return

    #-------------------------------------------------------------
    # Prepare empty keograms to be filled by processing all files

    keo557=np.zeros((180,24*60))
    keo630=np.zeros((180,24*60))
    keo428=np.zeros((180,24*60))


    # Process all files
    # Expect the filename to be of correct format with the year,
    # month and day encoded in fixed locations
    #
    #           1111111111
    # 01234567890123456789
    # MISS-20181007-000000.pgm
    # MISS-%Y%m%d-%H%M%S.pgm

    # From the raw image, these columns mark the northen and southern
    # horizon. This is used in extracting the values within the fied-of-view
    # of the instrument

    northcol=267
    southcol=70

    # For each file
    # - read the raw file
    # - extract spectral line with an associated background
    # - remove the background values
    # - collect the values into a time vs. latitude plot (keogram)

    for thisfile in myfiles:
        thisbasename=basename(thisfile)
        thisfiletime=datetime.datetime.strptime(thisbasename,'MISS-%Y%m%d-%H%M%S.pgm')
        if (thisfiletime.second != 0):
            continue
        print('     ',thisbasename)

        try:
            thisimage=readpgm(thisfile)

            # Bin the data if required
            if(thisimage.shape==(1039,347)):
                thisimage=thisimage[:-1,:] # Ignore the last column
                thisimage=(thisimage[0::3,:]+thisimage[1::3,:]+thisimage[2::3,:])/3.0


            # Process the image to filter noisy pixels out. Also,
            # estimate the general background level from the side
            # of the image and subtrack that as well. Note that this
            # is not a proper background subtraction that should be done
            # by choosing column next to the spectral line column.
            
            thisimage=signal.medfilt2d(thisimage.astype('float32'))
            bg=np.average(thisimage[0:30,0:30])
            thisimage=np.maximum(0,thisimage-bg)
            
            index=thisfiletime.hour*60+thisfiletime.minute

            datavals=np.linspace(southcol,northcol, num=180)

            # Process 557.7nm, the locations of the spectral line and its
            # background are from a vertically binned image (manual work...)
            # New version: with 4-times binning in X-direction we should
            # sum three rows to get a 12-pixel binning in spectrum

            myline=thisimage[159,:]+thisimage[158,:]+thisimage[160,:]
            #mylinebg=thisimage[164,:]

            thisline=np.interp(datavals,np.arange(0,len(myline)),myline)
            #thislinebg=np.interp(datavals,np.arange(0,len(mylinebg)),mylinebg)
            keo557[:,index]=thisline #np.maximum(thisline-thislinebg,0)

            # Process 630.0nm

            myline=thisimage[224,:]+thisimage[223,:]+thisimage[225,:]
            #mylinebg=thisimage[217,:]

            thisline=np.interp(datavals,np.arange(0,len(myline)),myline)
            #thislinebg=np.interp(datavals,np.arange(0,len(mylinebg)),mylinebg)
            keo630[:,index]=thisline #np.maximum(thisline-thislinebg,0)

            # Process 427.8nm

            myline=thisimage[34,:]+thisimage[33,:]+thisimage[35,:]
            #mylinebg=thisimage[36,:]

            thisline=np.interp(datavals,np.arange(0,len(myline)),myline)
            #thislinebg=np.interp(datavals,np.arange(0,len(mylinebg)),mylinebg)
            keo428[:,index]=thisline #np.maximum(thisline-thislinebg,0)
     
        except:
            print('Could not process', thisfile)


    fig, (ax0) = plt.subplots(1,1)
    pngwidth=800
    pngheight=400
    mydpi=100
    fig.set_size_inches(pngwidth/mydpi,pngheight/mydpi)


    #-------- RGB composite
    rgbkeo=np.zeros((180,24*60,3))
    rgbkeo[...,0]=np.sqrt(np.minimum(1,keo630/1500.0))
    rgbkeo[...,1]=np.sqrt(np.minimum(1,keo557/3000.0))
    rgbkeo[...,2]=np.sqrt(np.minimum(1,keo428/1000.0))
    ax0.set_xlabel('Time (UT)')
    ax0.set_ylabel('Meridian')
    plt.sca(ax0)

    plt.xticks(np.arange(0,24,3)*60,np.arange(0,24,3))
    plt.yticks(np.arange(-90,90+45,45)+90,np.arange(-90,90+45,45))
    
    c=ax0.imshow(rgbkeo, aspect='auto')
                 #extent=[xlims[0],xlims[1],-90,90], aspect='auto')

    ax0.set_title('Meridian Imaging Spectrograph in Svalbard (KHO/UNIS) '
                 + thisfiletime.strftime('%Y-%m-%d'), fontsize=14)

    fig.tight_layout()
    #plt.show()

    # Store the summary plot into monthly directories

#    keoname='MISS-'+myday.strftime('%Y%m%d')+'.png'
#    monthpath=join(basepath,myday.strftime('%Y'),myday.strftime('%m'))

    #savefilename=keoname
#    savefilename=join(monthpath,keoname)
    plt.savefig(savefilename,dpi=mydpi)
    print('Stored ' + savefilename)


#======================================================================


basepath='C:\\Users\\mikkos\\MISS'
basepath='u:\\'

for year in [2023, 2024]:
    for month in range(10,13):
        for day in range(1,32):

            # Form a correct directory name for each day,
            # ignore impossible dates :-)

            checkDir=join(basepath,'{:04d}'.format(year),
                      '{:02d}'.format(month),
                      '{:02d}'.format(day))

            if(isdir(checkDir)):
                myday=datetime.date(year,month,day)
                # Skip today's data (and similarly all future days)
                todayutc=datetime.datetime.utcnow().date()
                if(myday>=todayutc):
                    continue
                
                # Store the keograms into monthly directories
                monthpath=join(basepath,myday.strftime('%Y'),
                               myday.strftime('%m'))
                keoname=join(monthpath,'MISS-RGB-'+myday.strftime('%Y%m%d')+'.png')
         
                if(isfile(keoname)==False):
                    print('Missing keogram for',checkDir)
                    createKeogram(basepath,myday,keoname)
                
                    

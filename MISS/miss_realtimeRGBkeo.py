"""
Create a realtime RGB keogram from the past few hours
- the image sizes, colours etc. are a result of heuristic selection process...
- note that the filename convention is strict and assumed to be correct for each file
"""

import datetime
from os.path import isfile, join, basename

#from glob import glob # It might be better to get an iterator?
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.dates as mdates
import datetime as dt
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
# Create a keogram from the last X hours of data
# - search for matching files based on the current time

def createkeogram(basepath, savefilename):
    # Ignore the last five minutes of data to ensure that
    # there is data. Align to whole minutes.
    latest=dt.datetime.utcnow()-dt.timedelta(minutes=5)
    latest=latest.replace(second=0, microsecond=0)

    # Change the number of hours from 8 to whatever you prefer
    datapoints=[latest-dt.timedelta(minutes=x) for x in range(0,8*60)]

    myfiles=[]

    # Search for data
    for myfile in datapoints:
        dirpath=join(myfile.strftime('%Y'),myfile.strftime('%m'),myfile.strftime('%d'))
        filename=myfile.strftime('MISS-%Y%m%d-%H%M00.pgm')
        filepath=join(basepath,dirpath,filename)
        if(isfile(filepath)==True):
           #print(filepath)
           myfiles.append(filepath)

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

        try:
            thisimage=readpgm(thisfile)

            # Bin the data if required (leftover from instrument tests...)
            if(thisimage.shape==(1039,347)):
                thisimage=thisimage[:-1,:] # Ignore the last column
                thisimage=(thisimage[0::3,:]+thisimage[1::3,:]+thisimage[2::3,:])/3.0


            # Process the image to filter noisy pixels out. Also,
            # estimate the background from the side of the image and
            # subtract that as well.
            thisimage=signal.medfilt2d(thisimage.astype('float32'))
            bg=np.average(thisimage[0:30,0:30])
            thisimage=np.maximum(0,thisimage-bg)
            
            delta=latest-thisfiletime
            index=24*60-1-round(delta.seconds/60)-24*60*delta.days
            print('     ',thisbasename, delta, delta.seconds,index)

            datavals=np.linspace(southcol,northcol, num=180)

            # The locations of the spectral lines and their
            # backgrounds are from a vertically binned image (calibration...)
            # New version: with 4-times CCD-binning in X-direction we should
            #              sum three rows to get a 12-pixel binning in spectrum
            #
            # Note: the background determined near the spectral line needs more
            #       work to look good (= do a better calibration)

            #-----------------
            # Process 557.7nm
            
            myline=thisimage[159,:]+thisimage[158,:]+thisimage[160,:]
            #mylinebg=thisimage[164,:]

            thisline=np.interp(datavals,np.arange(0,len(myline)),myline)
            #thislinebg=np.interp(datavals,np.arange(0,len(mylinebg)),mylinebg)
            keo557[:,index]=thisline #np.maximum(thisline-thislinebg,0)

            #-----------------
            # Process 630.0nm
    
            myline=thisimage[224,:]+thisimage[223,:]+thisimage[225,:]
            #mylinebg=thisimage[217,:]

            thisline=np.interp(datavals,np.arange(0,len(myline)),myline)
            #thislinebg=np.interp(datavals,np.arange(0,len(mylinebg)),mylinebg)
            keo630[:,index]=thisline #np.maximum(thisline-thislinebg,0)

            #------------------
            # Process 427.8nm
    
            myline=thisimage[34,:]+thisimage[33,:]+thisimage[35,:]
            #mylinebg=thisimage[36,:]

            thisline=np.interp(datavals,np.arange(0,len(myline)),myline)
            #thislinebg=np.interp(datavals,np.arange(0,len(mylinebg)),mylinebg)
            keo428[:,index]=thisline #np.maximum(thisline-thislinebg,0)
        except:
            print('Could not process', thisfile)


    fig, (ax3) = plt.subplots(1,1)
    ax3.set_title('Meridian Imaging Spectrograph in Svalbard (KHO/UNIS) \n'+
                  min(datapoints).strftime('%Y/%m/%d %H:%M UT')+ ' to ' +
                  max(datapoints).strftime('%Y/%m/%d %H:%M UT'), fontsize=18)


    pngwidth=800
    pngheight=400
    mydpi=100
    fig.set_size_inches(pngwidth/mydpi,pngheight/mydpi)

    hours=mdates.HourLocator(byhour=range(0,24,2))
    d_fmt=mdates.DateFormatter('%H:%M')
    xlims=mdates.date2num([min(datapoints),max(datapoints)])
    

    #----------------
    # RGB composite
    # - the constants were manually "tuned"
    
    rgbkeo=np.zeros((180,24*60,3))
    rgbkeo[...,0]=np.sqrt(np.minimum(1,keo630/1500.0))
    rgbkeo[...,1]=np.sqrt(np.minimum(1,keo557/3000.0))
    rgbkeo[...,2]=np.sqrt(np.minimum(1,keo428/1000.0))
    
    ax3.set_ylabel('Zenith angle (positive north)')
    plt.sca(ax3)
    
    ax3.xaxis_date()
    ax3.xaxis.set_major_locator(hours)
    ax3.xaxis.set_major_formatter(d_fmt)
                 
    plt.yticks(np.arange(-90,90+45,45),np.arange(-90,90+45,45))
    
    c=ax3.imshow(rgbkeo,
                 extent=[xlims[0],xlims[1],-90,90], aspect='auto')



    fig.tight_layout()
    #plt.show()

    # Store the summary plot into monthly directories

    plt.savefig(savefilename,dpi=mydpi)
    print('Stored ' + savefilename)

# For development, it's convenient to have the data stored...
#    np.save("keo557",keo557);
#    np.save("keo630",keo630);
#    np.save("keo428",keo428);
#    np.save("xlims",xlims);


#======================================================================


basepath='C:\\Users\\mikkos\MISS'

webbase='Z:\\kho\\MISS'
webfile=join(webbase,'miss-keo24hours.png')

createkeogram(basepath,webfile)

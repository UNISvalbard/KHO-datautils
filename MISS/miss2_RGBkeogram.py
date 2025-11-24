"""
Create a realtime RGB keogram from the past few hours
- the image sizes, colours etc. are a result of heuristic selection process...
- note that the filename convention is strict and assumed to be correct for each file
"""

"""
In the beginning of the the early season 2024-2025, the binning was different
from what it is now. So, check the image size and ignore early data.

TO DO: either resize the images to match the size or redo the calibration
for the smaller images.
"""


from os.path import isfile, join, basename, isdir

#from glob import glob # It might be better to get an iterator?
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.dates as mdates
import datetime as dt
import glob

from scipy import signal
from PIL import Image

def read_miss2(filename):
    """
    Read a MISS png-image, flip and rotate to have north up and increasing wavelength towards right.
    """
    missImage=np.array(Image.open(filename))

    # The raw data has 1039 rows with 347 columns, do some flipping 
    thisimage=np.fliplr(np.rot90(missImage))
    
    return thisimage


#=================================================================
# Create a keogram from the last X hours of data
# - search for matching files based on the current time

def createRGBkeogram(basepath, myday, savefilename):
    print('Checking data for', myday)
    dirpath=join(myday.strftime('%Y'),myday.strftime('%m'),myday.strftime('%d'))
    globpath=join(basepath,dirpath,'MISS2-????????-??????.png')
    #print(globpath)
    myfiles=glob.glob(globpath)

    if(len(myfiles)==0):
        print("No data for ",myday)
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
    # MISS2-20181007-000000.png
    # MISS2-%Y%m%d-%H%M%S.png

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
    
    blue_col=103
    green_col=558
    red_col=807
    keogramIsEmpty=True

    for thisfile in myfiles:
        thisbasename=basename(thisfile)
        filetime=dt.datetime.strptime(thisbasename,'MISS2-%Y%m%d-%H%M%S.png')
        thisfiletime=filetime.replace(tzinfo=dt.timezone.utc)
        if (thisfiletime.second != 0):
            continue

        try:
            thisimage=read_miss2(thisfile)

            # Ignore spectral images that are not of correct size
            if thisimage.shape!=(347,1039):
                continue
            

            # Process the image to filter noisy pixels out. Also,
            # estimate the background from the side of the image and
            # subtract that as well.
            thisimage=signal.medfilt2d(thisimage.astype('float32'))
            bg=np.average(thisimage[0:30,0:30])
            thisimage=np.maximum(0,thisimage-bg)
            
            index=thisfiletime.hour*60+thisfiletime.minute
            print('     ',thisbasename, index)

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
            # - pixel column
            
            myline=thisimage[:,green_col-1]+thisimage[:,green_col]+thisimage[:,green_col+1]
            thisline=np.interp(datavals,np.arange(0,len(myline)),myline)
            keo557[:,index]=thisline

            #-----------------
            # Process 630.0nm
    
            myline=thisimage[:,red_col-1]+thisimage[:,red_col]+thisimage[:,red_col+1]
            thisline=np.interp(datavals,np.arange(0,len(myline)),myline)
            keo630[:,index]=thisline

            #------------------
            # Process 427.8nm
    
            myline=thisimage[:,blue_col-1]+thisimage[:,blue_col]+thisimage[:,blue_col+1]
            thisline=np.interp(datavals,np.arange(0,len(myline)),myline)
            keo428[:,index]=thisline

            keogramIsEmpty=False

        except Exception as error:
            print('Could not process', thisfile)
            print(error)

    # Do not bother saving empty keograms
    if keogramIsEmpty==True:
        print(f"Empty keogram for this day, no file saved...")
        return
    
    fig, ax = plt.subplots(1,1)
    titleDate=thisfiletime.strftime('%Y-%m-%d')
    fig.suptitle(f"MISS-2 (KHO/UNIS) {titleDate}", fontsize=16)
    ax.set_title("RGB composite from 427.8, 557.7 and 630.0 nm emission lines", fontsize=11)


    pngwidth=800
    pngheight=400
    mydpi=100
    fig.set_size_inches(pngwidth/mydpi,pngheight/mydpi)

    hours=mdates.HourLocator(byhour=range(0,24,2))
    d_fmt=mdates.DateFormatter('%H:%M')
    #xlims=mdates.date2num([min(datapoints),max(datapoints)])
    

    #----------------
    # RGB composite
    # - the constants were manually "tuned"
    
    rgbkeo=np.zeros((180,24*60,3))
    rgbkeo[...,0]=np.clip(np.sqrt(keo630/40000), a_min=0, a_max=1)
    rgbkeo[...,1]=np.clip(np.sqrt(keo557/60000), a_min=0, a_max=1)
    rgbkeo[...,2]=np.clip(np.sqrt(keo428/10000), a_min=0, a_max=1)

    ax.set_ylabel('Zenith angle')
    ax.set_xlabel('Time (UT)')
    #plt.sca(ax3)

    ax.xaxis_date()
    ax.xaxis.set_major_locator(hours)
    ax.xaxis.set_major_formatter(d_fmt)

    ax.set_xticks(np.arange(0,24,3)*60,np.arange(0,24,3))                 
    ax.set_yticks(np.arange(-90,90+45,45),np.arange(-90,90+45,45))
    ax.set_yticklabels(['South', '-45°', 'Zenith', '45° N','North'])#, fontsize = 14)
    c=ax.imshow(rgbkeo, aspect='auto', extent=[0,24*60,-90,90])



    fig.tight_layout()
    #plt.show()

    # Store the summary plot into monthly directories

    plt.savefig(savefilename,dpi=mydpi)
    print('Stored ' + savefilename)

# For development, it's convenient to have the data stored...
    #np.save("keo557",keo557);
    #np.save("keo630",keo630);
    #np.save("keo428",keo428);
    #np.save("xlims",xlims);


#======================================================================

def createKeogram(year,month,day,overWrite=False):
    basepath='d:\\'
    basepath=join(basepath,"KHO","MISS-2")
    checkDir=join(basepath,'{:04d}'.format(year),
            '{:02d}'.format(month),
            '{:02d}'.format(day))
    print(checkDir)
    if(isdir(checkDir)):
        myday=dt.datetime(year,month,day,tzinfo=dt.timezone.utc)
        #myday.replace,tzinfo=dt.timezone.utc)
        # Skip today's data (and similarly all future days)
        todayutc=dt.datetime.now(dt.timezone.utc)
        if(myday>=todayutc):
            return
        
        # Store the keograms into monthly directories
        monthpath=join(basepath,myday.strftime('%Y'),
                    myday.strftime('%m'))
        keoname=join(monthpath,'MISS2-RGB-'+myday.strftime('%Y%m%d')+'.png')

        if(overWrite==True or isfile(keoname)==False):
            print('Creating keogram for',checkDir)
            createRGBkeogram(basepath,myday,keoname)
        else:
            print(f"Skipping existing {keoname}")

if __name__ == "__main__":
    for year in [2024, 2025, 2026]:
        for month in [1, 2, 3, 10, 11, 12]:
            for day in range(1,32):
                createKeogram(year,month,day, overWrite=True)
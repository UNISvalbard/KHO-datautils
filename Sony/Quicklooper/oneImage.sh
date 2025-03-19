#!/bin/bash

# A quick script to capture one image from Sony
# MS/27 Sep 2024
#
# TO DO:
# - errorhandling!!!!
#
# The script uses gphoto2 and jhead command-line tools

DATADIR="/home/mikkos/Data"

# Create a proper filename

IMAGENAME=`/bin/date -u +LYR-Sony-%Y%m%d_%H%M%S.jpg`

# Extract year, month and day for constructing a good path

YEAR=${IMAGENAME:9:4}
MONTH=${IMAGENAME:13:2}
DAY=${IMAGENAME:15:2}
HH=${IMAGENAME:18:2}
MM=${IMAGENAME:20:2}
SS=${IMAGENAME:22:2}

PATH="$DATADIR/$YEAR/$MONTH/$DAY"
/bin/mkdir -p $PATH

FULLNAME="$PATH/$IMAGENAME"

# No need to store temporary data onto the disk, so used shared memory ("ramdisk")
cd /dev/shm

# Capture an image, crop and correct the EXIF data to show the capture time

/usr/bin/gphoto2 -q --capture-image-and-download --frames 1 --no-keep --force-overwrite 1>/dev/null
/usr/bin/convert -crop 2832x2832+660-0 -rotate -90 capt0000.jpg $FULLNAME
/usr/bin/jhead -q -ts$YEAR:$MONTH:$DAY-$HH:$MM:$SS $FULLNAME

# Update the filename of the latest image in order to creating a thumbnail image...
echo $FULLNAME > $DATADIR/latest_filename.txt


#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "createMovie2pass {outputfile}"
    exit 0
fi 


# The mp4-file naming convention is strict and should be YYYYMMDD_unis_kho_sony-rgb.mp4
# NOTE: the number of frames needs has wwo possibilities: 7200 (12-sec cadence) or 8640 (10-sec cadence)
ffmpeg -f image2 -framerate 10 -start_number 0 -i Frames/frame%04d.jpg -vframes 7200 -c:v libx264 $1

#!/bin/bash

if [ "$#" -ne 1 ]; then
    echo "createMovie2pass {outputfile}"
    exit 0
fi 


# The mp4-file naming convention is strict and should be YYYYMMDD_unis_kho_sony-rgb.mp4


ffmpeg -y -f image2 -framerate 15 -start_number 0 -i /dev/shm/Frames/frame%04d.jpg -vframes 7200 -b:v 300k -c:v libx264 -pass 1 -f null /dev/null && 
ffmpeg -f image2 -framerate 15 -start_number 0 -i /dev/shm/Frames/frame%04d.jpg -vframes 7200 -b:v 300k -c:v libx264 -pass 2 $1

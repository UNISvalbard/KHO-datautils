#!/bin/bash


# The mp4-file naming convention is strict and should be YYYYMMDD_unis_kho_sony-rgb.mp4

ffmpeg -f image2 -framerate 10 -start_number 0 -i Frames/frame%04d.jpg -vframes 7200 -b:v 300k -c:v libx264 20241201_unis_kho_sony-rgb.mp4

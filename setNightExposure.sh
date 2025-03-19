#!/bin/bash

# Set the camera 
#   - 4-sec exposure
#   - ISO 16000  (24)  (night)
#   - ISO  4000  (18)  (full moon and late spring)
#   - ISO  1000  (12)  (full moon and late spring?)
/usr/bin/gphoto2 --set-config-index /main/capturesettings/shutterspeed=9
/usr/bin/gphoto2 --set-config-index /main/imgsettings/iso=18


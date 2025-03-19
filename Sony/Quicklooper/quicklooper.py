# -*- coding: utf-8 -*-
"""

A quick routine that captures all-sky images whenever the Sun is
more than 9 degrees below the horizon.

@author: MikkoS
"""


import datetime as dt
import os
import numpy as np
import time
import astropy.units as u
from astropy.constants import R_earth
from astropy.time import Time
from astropy.coordinates import EarthLocation, AltAz
from astropy.coordinates import get_sun

# Getting an error from IERS_Auto using predictive values that
# are more than 30 days old.
# BUG FIX NEEDED: there should be an automatic download in Astropy,
# but the age check is only done when starting the program. So, if
# left running for months for automatic imaging, you may find out
# that the program has stopped capturing images...
#
# The following will disable the warnings/errors

from astropy.utils.iers import conf
conf.auto_max_age = None

# Location of the camera

kho = EarthLocation(lat=78.148*u.deg, lon=16.043*u.deg, height=520*u.m)

try:
    while True:
        rightNow=Time.now()
        while not(rightNow.datetime.second % 10 == 0):
            rightNow=Time.now()

        frame_observation = AltAz(obstime=rightNow, location=kho)
        sunaltaz = get_sun(rightNow).transform_to(frame_observation)
        print("At",rightNow)
        print("- solar altitude %.1f deg" % sunaltaz.alt.deg)

        if sunaltaz.alt.deg<-9:
            print("- taking a photo")
            os.system("oneImage.sh") 
        time.sleep(1)
except KeyboardInterrupt:
    print("\nStopping imaging program")

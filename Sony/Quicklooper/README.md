# Simple scripts for capturing all-sky images

A common task for auroral imagers is to capture images at a fixed cadence whenever the Sun is more than e.g. 10 degrees below the horizon. 
The "Quicklooper" comprises of a couple of scripts that provide a very minimal yet working setup.

The key component is a single command-line tool `oneImage.sh` that uses `gphoto2` to acquire an image and download it to the computer. 
The filenamin convention g and directory structures are strict and automatically defined from the UT-time of the computer.
If the camera does not have a GPS for correct date and time (like our first generation Sony A7s), one should "fix" the EXIF-data 
to avoid confusion between EXIF-data and filename. This is easy to do with `jhead`.

The python-code `quicklooper.py` uses the current time and location to compute the elevation of the Sun using AstroPy. If the Sun is below the horizon,
it will use `oneImage.sh` every X seconds (we use 10-sec intervals between images).

For practical purposes, such as realtime data in web, we create small 480x480 thumbnail images including location, date, time etc. 

| Script | Description |
| ------ | ----------- |
| <samp>quicklooper.py</samp> | The main routine that uses oneImage.sh to capture images regularly |
| <samp>oneImage.sh</samp> | Command to capture and download one image from the camera to disk |
| <samp>thumbnailer.py</samp> | Create small thumbnail images for any new images |

## A note on the operational side

As these scripts are really simple and bare-bones, directory names etc. are hard-coded into the scripts. One should first change/modify the directories etc. in `oneImage.sh`.
Then one can use the script from command line to confirm that capturing images to disk works as intended.

For `quicklooper.py` it may be easiest to run it from command line as well. Here, it is very practical to use `screen`. For `thumbnailer.py`, 
one can start another screen-session similarly.

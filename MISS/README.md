# Software for Meridian Imaging Svalbard Spectrograph (MISS)

The [University Centre in Svalbard](https://www.unis.no) operates an optical observatory, [Kjell Henriksen Observatory](http://kho.unis.no), for space research in Svalbard, Norway. 
This repository collects various routines and software for using the data from the [Meridian Imaging Svalbard Spectrograph (MISS)](https://kho.unis.no/Instruments/MISS.html).

MISS uses custom optics to record visible spectra along the (magnetic) meridian. Nominally, the instrument operates during the dark time of the day and continuously records images, where one
axis represents the zenith angle (from north to south along the meridian) and the other axis provides the spectra in the visible wavelengths (400-700nm). The realtime data found at the KHO website 
uses a very simplified "calibration", which should not be trusted for proper scientific analysis. Similarly, the RGB composite keograms are for visual purposes only.

The first years of operation use [PGM-format](https://netpbm.sourceforge.net/) for the data. Nominally, the data is stored in [PNG-format](https://en.wikipedia.org/wiki/PNG) (16-bit greyscale values).

## Data use in practice

An example of how the data can be used for research: [Partamies et al., "First observations of continuum emission in dayside aurora", 2025](https://doi.org/10.5194/angeo-43-349-2025)

# (Very) Basic spectral calibration

The spectral image is not perfectly aligned with image rows or column. Among others, there is a clear "smile" distortion. 
More detailed characterisation of the effects requires laboratory experiments, but a first-order approximation can (probably)
be carried out by using the three brightest auroral emission lines (427.8nm, 557.7nm and 630.0nm).

Because the researcher needing the calibration prefers to work in Matlab, these quick calibration scripts were first written in Matlab, but there
is also a python example using the parameters determined using Matlab. 

The basic form of the image is scan angle i.e. position along the meridian versus wavelength. For each row, the script searches the columns for each intensity peak.
Then the detected column locations are used to estimate parameters for a polynomial fit. Eventually a new spectral image is constructed where the polynomials are used
for correcting the distortion. Some of the values were obtained by zooming into the Matlab plots.

## MISS-1 vs. MISS-2

There are two "identical" MISSes. As the alignment of optics varies between the units, there are different calibration coefficients for each. The example codes
used data from the first MISS i.e. MISS-1, so the same routines cannot be used with MISS-2. 

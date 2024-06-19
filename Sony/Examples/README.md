# Examples of resized images

The raw data from the Sony A7s all-sky imager at Kjell Henriksen Observatory are 2832x2832 RGB-images stored in JPG-format. For general browsing of data smaller quicklook images (480x480) are often sufficient.

If there is no aurora in the image, there are too option: either the clouds prevent the observation of existing aurora or the skies are clear and there simply is no aurora to be seen. To separate these cases, one can try to see stars (or the Moon) in the image.

"Better" interpolation methods used for resizing the image (correctly) use a smoothing filter before resampling and this tends to remove the stars from the quicklook images. Here are two quicklook examples:

| Cubic spline interpolation | Nearest neighbour |

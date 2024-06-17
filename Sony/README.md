# Collected scripts for Sony A7s all-sky imager at KHO

Please note that most of these scripts have hardcoded directory names and various levels of error checking, failure recovering etc.

| Script | Description |
| ------ | ----------- |
| <samp>sony2aurorax.py</samp> | Traverse a data directory of full resolution image and create thumbnail images (480x480) with simple captions into a new directory. |
| <samp>sonykeogram.py</samp> | Create keograms from Sony data |
| <samp>sony_pruning.py</samp> | Traverse a data directory structure and copy the first (thumbnail) image to another directory |
| <samp>quicklook_test.py</samp> | Testing various interpolation methods in PIL and OpenCV. In short, use nearest neighbour method to preserve some stars in thumbnail images! |

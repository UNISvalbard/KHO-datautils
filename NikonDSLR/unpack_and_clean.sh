#!/bin/bash

# Untar all tar-balls and remove Quicklook and tmp subdirectories

find . -name '*.tar.gz' -exec tar xvfz {} \;
rm -rf */Quicklooks */tmp */Raw




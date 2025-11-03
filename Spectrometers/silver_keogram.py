# -*- coding: utf-8 -*-
"""
Created on Tue Jan 21 10:59:54 2025

@author: MikkoS
"""

import os
import datetime as dt
import numpy as np
import matplotlib.pyplot as plt
import glob

# "Flatten" a list, clever function from stackoverflow
# https://stackoverflow.com/questions/952914/how-do-i-make-a-flat-list-out-of-a-list-of-lists
def flatten(xss):
    return [x for xs in xss for x in xs]

# A helper function for choosing the maximum counts to be plotted
def next_multiple_of_100(value):
    return((value//100)+1)*100



def read_silver_data(filename):
    with open(filename, 'r') as file:
        # Skip the first 6 rows
        for _ in range(6):
            next(file)

        all_data = []  # To store the list of (header, data) pairs

        while True:
            # Read the first row (header) which should contain 13 elements
            header_line = next(file, None)
            if header_line is None:
                break  # End of file reached

            # Debugging: Print the raw header line
            #print(f"Header line: {header_line.strip()}")

            # Split the header line into parts
            header_parts = header_line.strip().split()

            if not header_parts:  # Skip empty lines
                continue
            
            if len(header_parts) != 13:
                raise ValueError(f"Header line has {len(header_parts)} columns, expected 13 columns: {header_line.strip()}")
            
            # Extract header information with appropriate types (int or float)
            try:
                year, month, day, hour, minute, second, order = map(int, header_parts[:7])  # These are integers
                startwave, stopwave, integration, elevation = map(float, header_parts[7:11])  # These are floats
                slits, num_data_points = map(int, header_parts[11:13])  # These are integers
            except ValueError as e:
                raise ValueError(f"Error parsing header values: {header_line.strip()}") from e

            header = {
                'year': year,
                'month': month,
                'day': day,
                'hour': hour,
                'minute': minute,
                'second': second,
                'order': order,
                'startwave': startwave,
                'stopwave': stopwave,
                'integration': integration,
                'elevation': elevation,
                'slits': slits,
                'num_data_points': num_data_points
            }

            # Initialize list to store the data points for this header
            data_points = []

            # Variable to track the total number of data points we have read
            total_data_points_read = 0

            # Read data until we've accumulated the correct number of data points
            while total_data_points_read < num_data_points:
                data_line = next(file, None)
                if data_line is None:
                    raise EOFError(f"Reached end of file before reading the expected {num_data_points} data points.")

                try:
                    data_parts = list(map(int, data_line.strip().split()))
                except ValueError:
                    raise ValueError(f"Error parsing data line: {data_line.strip()}")
                
                num_data_in_row = len(data_parts)
                total_data_points_read += num_data_in_row

                # Add this row of data points
                data_points.append(data_parts)

            # Check if we read the correct number of data points
            if total_data_points_read != num_data_points:
                raise ValueError(f"Expected {num_data_points} data points, but read {total_data_points_read}.")

            # Store the header and its corresponding data points
            all_data.append((header, flatten(data_points)))

        return all_data

def make_silver_keogram(filename,destination):
    all_data = read_silver_data(filename)
    if len(all_data)<1:
        raise Exception(f'No data in {filename}')
    
    keogram=np.zeros((381,24*60)) # One minute resolution
    
    # First read the first head to extract the date for the datafile
    (header, data_points) = all_data[0]
    fileyear, filemonth, fileday = header['year'],header['month'],header['day']
    
    datefromheader=f'{fileyear}-{filemonth:02}-{fileday:02}'
    try:
        dt.datetime.strptime(datefromheader,'%Y-%m-%d')
    except ValueError:
        print("\nHeader 1:")
        for key, value in header.items():
            print(f"{key}: {value}")
        raise Exception(f'Invalid date in {filename}')
    
    lambda_min=header['startwave']/10
    lambda_max=header['stopwave']/10
    
    # Go through the data and copy scan data to keogram.
    # Check that the dates for each scan are identical.
    # It is possible that some of the other parameters have changed, too,
    # but this is a summary plot...
    
    for i, (header, data_points) in enumerate(all_data):
        # Check that dates are identical in all headers
        thisyear=header['year']
        thismonth=header['month']
        thisday=header['day']
    
        if thisyear != fileyear or thismonth != filemonth or thisday != fileday:
            raise Exception(f'File date vs. record date mismatch in {filename}')        
    
        thishh=header['hour']
        thismm=header['minute']
        thisss=header['second']
    
        # Check the date is a valid date    
        datefromheader=f'{thisyear}-{thismonth:02}-{thisday:02} {thishh:02}:{thismm:02}:{thisss:02}'
        try:
            dt.datetime.strptime(datefromheader,'%Y-%m-%d %H:%M:%S')
        except ValueError:
            print(f"\nHeader {i + 1}:")
            for key, value in header.items():
                print(f"{key}: {value}")
            raise Exception(f'Invalid  date in {filename}')

        # Form the filename and skip the rest if it already exists    
        keofilename=os.path.join(destination,f'Silver_{fileyear}{filemonth:02}{fileday:02}.png')

        if os.path.isfile(keofilename)==True:
            print(f'   -- keogram {keofilename} exists, skipping...')
            return
        
        #print("\nData Points (first 3 numbers of this block):")
        #for row in data_points[:3]:
        #    print(row)
    
      
        spectrum=np.array(data_points)
        
        # Calculate the location in the keogram based on the time. Round
        # to the nearest full minute but limit the index to the current day.
        # Don't care about overwriting any previous data, this is a summary
        # plot...
        
        index=min(60*thishh+thismm+round(thisss/60),24*60-1)
        
        keogram[:,index]=spectrum
        
    # Limit the intensity range. The limit should probably be something
    # that is determined by the data rather than this fixed value.
    
    clipValue=next_multiple_of_100(np.percentile(keogram,99))
    keogram=np.clip(keogram,0,clipValue) 
    
    
    # Create the plot
    plt.figure(figsize=(12, 5))
    
    plt.imshow(keogram, aspect='auto', extent=[0, 24, lambda_min, lambda_max], origin='lower', cmap='viridis')
    
    # Set labels for the axes
    plt.xlabel("Time (hours)")
    ticks=np.arange(0,25,2)
    tick_labels=[f"{int(t):02d}" for t in ticks]
    plt.xticks(ticks,tick_labels)
    
    plt.ylabel("Wavelength (nm)")
    plt.colorbar(label='Counts')
    
    plt.title(f'KHO/UNIS 1m Silver Ebert-Fastie spectrometer {fileyear}-{filemonth:02}-{fileday:02}')
    
    # Save the plot as a PNG file for the keogram website
    plt.savefig(keofilename, dpi=100, bbox_inches='tight')
    plt.close()

#------------------
# - make a keogram from all silver bullet data

#sourcepath=os.path.join('D:\\','KHO','saasdata','data25','Silver')
sourcepath=os.path.join('E:\\','Incoming','saasdata','data26','Silver')
destination=os.path.join('D:\\','KHO','saasdata','Keograms','Silver')

files=glob.glob(os.path.join(sourcepath,'s??????2.lyr'))

for datafile in files:
    #datafile='s0101232.lyr'
    print(f'Processing {datafile}')
    filename=os.path.join('D:\\','KHO','Spectrometers','Software',datafile)
    make_silver_keogram(filename,destination)
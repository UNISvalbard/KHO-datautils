# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 10:34:35 2025

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

sourcepath=os.path.join('D:\\','KHO','saasdata','data23','Green')
destination=os.path.join('D:\\','KHO','saasdata','Keograms','Green')

files=glob.glob(os.path.join(sourcepath,'??????G2.lyr'))
filename=files[0]

# Read the green spectrometer data, which is a bit more involved
def read_green_spectrometer(filename):
    with open(filename, 'r') as file:
        # Skip the first 6 rows
        for _ in range(25):
            next(file)
    
        all_data = []  # To store the list of (header, data) pairs
    
        while True:
            # Read and expect to get either "Setup # 1" or "Setup # 2"
            setup_line = next(file, None)
            if setup_line is None:
                break # EOF reached
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
            
            if len(header_parts) != 15:
                raise ValueError(f"Header line has {len(header_parts)} columns, expected 15 columns: {header_line.strip()}")
            
            # Extract header information with appropriate types (int or float)
            try:
                year, month, day, hour, minute, second = map(int, header_parts[:6]) 
                startangle, stopangle, order = map(float, header_parts[6:9])
                slits = float(header_parts[9])
                startwave, stopwave, calFac, integration = map(float, header_parts[10:14])  # These are floats
                num_data_points = int(header_parts[14])  # These are integers
            except ValueError as e:
                raise ValueError(f"Error parsing header values: {header_line.strip()}") from e
    
            header = {
                'setup':setup_line.strip(),
                'year': year, #0
                'month': month, #1
                'day': day, #2
                'hour': hour, #3
                'minute': minute, #4
                'second': second, #5
                'startangle': startangle, #6
                'stopangle': stopangle, #7
                'order': order, #8
                'slits': slits, #9
                'startwave': startwave, #10
                'stopwave': stopwave, #11
                'calFac': calFac, #12
                'integration': integration, #13
                'num_data_points': num_data_points #14
            }
            #break
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


def make_green_keogram(filename,destination, overwrite=False):
    all_data=read_green_spectrometer(filename)
    if len(all_data)<1:
        raise Exception(f'No data in {filename}')
    
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
    

    keogram1=np.zeros((708,24*60))  # This is for Setup #1 (top plot)
    keogram2=np.zeros((814,24*60))  # This is for Setup #2 (bottom plot)
    
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
    
        spectrum=np.array(data_points)
        index=min(60*thishh+thismm+round(thisss/60),24*60-1)
    
        if header['setup'] == 'Setup # 1':
            lambda_min1=header['startwave']/10
            lambda_max1=header['stopwave']/10
            keogram1[:,index]=spectrum
            # Extend the "width" of each timeslot to cover
            # missing data in the keogram
            if index+1 < 24*60:
                keogram1[:,index+1]=spectrum
        elif header['setup'] == 'Setup # 2':
            lambda_min2=header['startwave']/10
            lambda_max2=header['stopwave']/10
            keogram2[:,index]=spectrum
            if index+1 < 24*60:
                keogram2[:,index+1]=spectrum
        else:
            raise Exception(f"Unidentified setup {header['setup']} in {filename}")
    
    # Limit the intensity range. The limit should probably be something
    # that is determined by the data rather than this fixed value.
    
    clipValue=next_multiple_of_100(np.percentile(keogram1,99))
    keogram1=np.clip(keogram1,0,clipValue) 
    
    clipValue=next_multiple_of_100(np.percentile(keogram2,99))
    keogram2=np.clip(keogram2,0,clipValue) 
    

    # Save the plot as a PNG file
    keofilename = os.path.join(destination, f'Green_{fileyear}{filemonth:02}{fileday:02}.png')
    if overwrite==False and os.path.isfile(keofilename)==True:
        print(f'   -- keogram {keofilename} exists, skipping...')
        return    
    
    # Create the subplots with shared X-axis
    fig, (ax2, ax1) = plt.subplots(2, 1, figsize=(12, 6), sharex=True)
    
    # Plot the lower wavelength range
    cax1 = ax1.imshow(keogram1, aspect='auto', extent=[0, 24, lambda_min1, lambda_max1], origin='lower', cmap='viridis')
    ax1.set_ylabel("Wavelength (nm)")
    ax1.set_xticks(np.arange(0, 25, 2))
    ax1.set_xticklabels([f"{int(t):02d}" for t in np.arange(0, 25, 2)])
    ax1.set_xlabel("Time (hours)")
    
    # Plot the higher wavelength range    
    cax2 = ax2.imshow(keogram2, aspect='auto', extent=[0, 24, lambda_min2, lambda_max2], origin='lower', cmap='viridis')
    ax2.set_ylabel("Wavelength (nm)")
    ax2.set_title(f'KHO/UNIS 1m Green Ebert-Fastie spectrometer {fileyear}-{filemonth:02}-{fileday:02}')
    
    # Add colorbars
    fig.colorbar(cax1, ax=ax1, label='Counts')
    fig.colorbar(cax2, ax=ax2, label='Counts')
    
    # Adjust layout to avoid overlapping elements
    plt.tight_layout()
    #plt.show()
    plt.savefig(keofilename, dpi=100, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":

    sourcepath=os.path.join('E:\\','Incoming','saasdata','data26','Green')
    #sourcepath=os.path.join('D:\\','KHO','saasdata','data24','Green')
    destination=os.path.join('D:\\','KHO','saasdata','Keograms','Green')
    
    
    files=glob.glob(os.path.join(sourcepath,'??????G2.lyr'))
    for filename in files:
        print(f"Processing {filename}...")

        make_green_keogram(filename, destination)

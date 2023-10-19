"""
Python Script for converting the .fits files from the MarSurf Meterology software
and convert them to the common .tiff standard

No copyright is available. 

For internal lab distribution only. 

Author: Jeremy Ruhter (2023), University of Illinois Institute for Genomic Biology

Usage: python fits2tif.py -i <input filename> -o <output filename> -g <Gain value>

Description: takes a .fits file for an input and converts it a tiff following astopy.io 
             image standards putting a "D" or and "I" to denote the depth or Intensity 
             image

"""


import numpy as np
from astropy.io import fits
from PIL import Image
import argparse

argParser = argparse.ArgumentParser()
argParser.add_argument("-i", "--input", help="input filename")
argParser.add_argument("-o", "--output", help="output filename")
argParser.add_argument("-g", "--gain", help="output filename")

args = argParser.parse_args()
#print("args.name=%s" % args.name)

#Add the filename
filename = args.input
outputFN = args.output

#Increase this value to make the image brighter
gain = int(args.gain)
y = fits.open(filename)

im = Image.fromarray(np.uint8(y[1].data)).convert('RGB')
im.save('D_'+outputFN)
im2 = Image.fromarray(y[2].data.astype(np.uint16)*gain)
im2.save('I_'+outputFN)

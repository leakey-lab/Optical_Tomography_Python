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

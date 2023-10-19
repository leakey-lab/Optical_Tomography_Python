"""
Python Script for converting the .nms files from the MarSurf Meterology software
and convert them to the common .tiff standard

No copyright is available. 

For internal lab distribution only. 

Author: Jeremy Ruhter (2023), University of Illinois Institute for Genomic Biology

Usage: python NMS2TIFF.py

Description: Iterate through the current directory looking for files with the .nms suffix 
             and extracts the laser information and drops the topography. It will save a .tiff
             file with the same name as the .nms

"""





import os
import array
import struct
import binascii
import shutil
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

#This can be changed to any directory the user chooses
directory = '.'


#Directory walk through the files and check for .nms
for filename in sorted(os.listdir(directory)):
    if filename.endswith(".nms"):
        
        filename_out = os.path.splitext(filename)
        filename_stem = filename_out[0]

    #    shutil.copy(filename, filename_stem[2:-1]+').tif')
   #     os.remove(filename)
  #      print('Removed ', filename)
        
        with open(filename, mode='rb') as file:
            fileContent = file.read() 

        #Spam the console with debug information 
        print(filename, ' ',fileContent[1368:1384])
        byteData = bytearray(fileContent[1368:1372])
        widthImA = struct.unpack('<i',byteData)
        byteData = bytearray(fileContent[1372:1376])
        heightImA = struct.unpack('<i',byteData)
        print(filename, ' ',widthImA, heightImA)

        #The height and width are read in from the header information
        #corrupt files will cause errors
        heightIm = int(heightImA[0])
        widthIm = int(widthImA[0])

        imSize = heightIm*widthIm
        imOffset = 3468 

  #      depthBytes = bytearray(fileContent[imOffset:imOffset+imSize*2])
        laserBytes = bytearray(fileContent[imOffset+imSize*2:imOffset+imSize*3])

        laserInArray = np.array(laserBytes)

        #If the topo is wanted uncomment this information
        #Naive method for depth Info
        #depthInArray = np.zeros((imSize,1,1), dtype=np.short)
        #for i in range(imSize-1):
        #    depthS = struct.unpack('<h',depthBytes[i*2:(i+1)*2])
        #    depthInArray[i] = depthS[0]
            
        #depthIn2Array = np.resize(depthInArray, (heightIm, widthIm))
        laserIn2Array = np.resize(laserInArray, (heightIm, widthIm))

        #Save the image out as a .tif
        #depthImg =Image.fromarray(depthIn2Array)
        laserImg = Image.fromarray(laserIn2Array)
    #    print(laserImg.size, ' ', len(laserInArray), ' ', heightImA, widthImA)
       # cplaserImg = laserImg.crop((1,1, widthIm-1,heightIm-1,))
      #  print('Saving Image ', filename_stem[2:-1]+').tif', 'From ', filename)
        filenameOut = filename_stem+'.tif'
        laserImg.save(filenameOut)
        

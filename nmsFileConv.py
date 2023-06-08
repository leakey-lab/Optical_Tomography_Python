#install.packages("tiff")
#require("tiff")
#import cv2
import ftplib as FTP
import struct
import os
from PIL import Image
import numpy as np

workingDir = "."
for subdir, dirs, files in os.walk(workingDir): 
#fileIn = file("test.fits", "rb")
    for filename in files:
        if filename.endswith(".nms"):           
            nmsfile = open(filename, mode="rb")
            filecontent = nmsfile.read()
#test = readBin(fileIn, n=16, raw(), size=1, endian = "little")        
            struct.unpack_from("<16x", filecontent[0:16])       
#testd = readBin(fileIn, n=2, double(),  endian = "little")
            struct.unpack_from("<2d", filecontent[16:32])                        
##RawBuff = readBin(fileIn, n=1336, raw(), size=1, endian = "little")
            struct.unpack_from("<1336x", filecontent[32:1368])                           
##testY = readBin(fileIn, n=4, integer(), size=2, endian = "little")
            pos_array = struct.unpack_from("<4h", filecontent[1368:1376])                               
##widthIm = testY[1];
            widthIm = pos_array[0]            
##heightIm = testY[3];
            heightIm = pos_array[2]
##testd2 = readBin(fileIn, n=2, double(),  endian = "little")            
            idx= 1376
            num = 2
            size = 8
            struct.unpack_from("<2d", filecontent[idx:idx+num*size])           
##RawBuff2 = readBin(fileIn, n=2076, raw(), size=1, endian = "little")
            idx = idx+num*size
            num = 2076
            size = 1          
            struct.unpack_from("<2076x", filecontent[idx:idx+num*size])   
##DepthIn = readBin(fileIn, n= widthIm*heightIm, integer(), size=2, signed=FALSE, endian = "little")
            idx = idx+num*size
            num = widthIm*heightIm
            size = 2
            dataSz = "<"+str(num)+"H"
            DepthIn = struct.unpack_from(dataSz, filecontent[idx:idx+num*size])
##LaserIn = readBin(fileIn, n= widthIm*heightIm, integer(), size=1, signed=FALSE, endian = "little")
            idx = idx+num*size
            num = widthIm*heightIm
            size = 1
            dataSz = "<"+str(num)+"B"
            LaserIn = struct.unpack_from(dataSz, filecontent[idx:idx+num*size])
            a = np.array(LaserIn,dtype=np.uint8)
            array = a.reshape(widthIm, heightIm)
##writeTIFF(array(as.double(LaserIn)/255,dim = c(512,512,3)),"laserOut.tif",8,"LZW",reduce=TRUE)
            im = Image.fromarray(array, mode="L")
            im.save(filename.split('.')[0]+'.tiff')


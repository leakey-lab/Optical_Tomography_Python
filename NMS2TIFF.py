import os
import array
import struct
import binascii
import shutil
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

directory = '.'


for filename in sorted(os.listdir(directory)):
    if filename.endswith(".nms"):
        
        filename_out = os.path.splitext(filename)
        filename_stem = filename_out[0]

    #    shutil.copy(filename, filename_stem[2:-1]+').tif')
   #     os.remove(filename)
  #      print('Removed ', filename)
        
        with open(filename, mode='rb') as file:
            fileContent = file.read() 

        print(filename, ' ',fileContent[1368:1384])
        byteData = bytearray(fileContent[1368:1372])
        widthImA = struct.unpack('<i',byteData)
        byteData = bytearray(fileContent[1372:1376])
        heightImA = struct.unpack('<i',byteData)
        print(filename, ' ',widthImA, heightImA)

        heightIm = int(heightImA[0])
        widthIm = int(widthImA[0])

        imSize = heightIm*widthIm
        imOffset = 3468 

  #      depthBytes = bytearray(fileContent[imOffset:imOffset+imSize*2])
        laserBytes = bytearray(fileContent[imOffset+imSize*2:imOffset+imSize*3])

        laserInArray = np.array(laserBytes)

        #Naive method for depth Info
        #depthInArray = np.zeros((imSize,1,1), dtype=np.short)
        #for i in range(imSize-1):
        #    depthS = struct.unpack('<h',depthBytes[i*2:(i+1)*2])
        #    depthInArray[i] = depthS[0]
            
        #depthIn2Array = np.resize(depthInArray, (heightIm, widthIm))
        laserIn2Array = np.resize(laserInArray, (heightIm, widthIm))

        #depthImg =Image.fromarray(depthIn2Array)
        laserImg = Image.fromarray(laserIn2Array)
    #    print(laserImg.size, ' ', len(laserInArray), ' ', heightImA, widthImA)
       # cplaserImg = laserImg.crop((1,1, widthIm-1,heightIm-1,))
      #  print('Saving Image ', filename_stem[2:-1]+').tif', 'From ', filename)
        filenameOut = filename_stem+'.tif'
        laserImg.save(filenameOut)
        

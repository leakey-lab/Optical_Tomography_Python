
import os
import re
import binascii

from PIL import Image

#os.chdir('/Users/jruhter/Desktop')

wDir = os.getcwd();


for filesIn in sorted(os.listdir(wDir)):
    if filesIn.endswith(".rtf"):
        with open(filesIn, 'r') as file1:
                rtf_data = file1.read().rstrip()

        NDC_Start = [_.start() for _ in re.finditer('emfblip',rtf_data)];
        NDC_Stop  = [_.start() for _ in re.finditer('000}}}',rtf_data)]

        if len(NDC_Start) != len(NDC_Stop):
            error(0)
        else:
            print("Extracting", len(NDC_Start), " images")

        i = 0    
        for i in range(len(NDC_Start)):
            iNDCs = int(NDC_Start[i])+8
            iNDCp = int(NDC_Stop[i])+3
            print('First Range is ', str(iNDCs), ' ', str(iNDCp))
            img_data = re.sub(r'\n', '', rtf_data[iNDCs:iNDCp])
            filename_out = filesIn+str(i)+'.emf'
            with open(filename_out, 'wb') as f:
                f.write(binascii.unhexlify(img_data))
            f.close()
            filename_out_j = filesIn+str(i)+'.tiff'
            Image.open(filename_out).save(filename_out_j)
    

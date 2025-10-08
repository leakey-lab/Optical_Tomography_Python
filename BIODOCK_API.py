
import requests
import os
import json
import time
import numpy as np
import cv2

import zipfile

API_KEY = "l2pG99uk2QPmWG8g18DTxaPtVgyPi/aYBDaoZhTq2su8t4VC"
URL = 'https://app.biodock.ai/api/external/filesystem-items/upload-file'
headers = {"X-API-KEY": API_KEY, "Content-Type": "application/json"}

os.chdir(r'C:\\Users\\CMExplorer600252\\Desktop\\test')
local_path = r'C:\\Users\\CMExplorer600252\\Desktop\\test\\'
FILENAME_IN = 'temp5.tif'
FILE_TO_UPLOAD = local_path + FILENAME_IN
DESIRED_FOLDER = 'API_TEST'
PIPELINE_ID = '62f421862c90ca016540a422'

def download_file(url, local_filename):
    """
    Downloads a file from a given URL and saves it locally.

    Args:
        url (str): The URL of the file to download.
        local_filename (str): The path and filename to save the downloaded file.
    """
    try:
        with requests.get(url, stream=True) as r:
            r.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"File '{local_filename}' downloaded successfully from '{url}'")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file: {e}")


def overlay_bounding_boxes(json_path, image_path, output_path='output_with_boxes.png'):
    """
    Read JSON file containing bounding box data and overlay boxes on an image.
    
    Args:
        json_path: Path to the JSON file with bbox data
        image_path: Path to the input image (e.g., 'temp3.tif')
        output_path: Path to save the output image with boxes
    """
    # Read the JSON file
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Read the image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not read image at {image_path}")
    
    # Create a copy to draw on
    overlay = img.copy()
    
    # Extract objects and their bounding boxes
    objects = data.get('objects', {})
    
    # Define colors (BGR format for OpenCV)
    box_color = (0, 255, 0)  # Green
    text_color = (0, 0, 0)  # BLACK
    thickness = 2
    
    # Iterate through all objects and draw bounding boxes
    for obj_id, obj_data in objects.items():
        bbox = obj_data.get('bbox')
        pred_class = obj_data.get('pred_class', 'Unknown')
        model_score = obj_data.get('model_score', 0)
        
        if bbox and len(bbox) == 4:
            x1, y1, x2, y2 = bbox
            
            # Draw rectangle
            cv2.rectangle(overlay, (x1, y1), (x2, y2), box_color, thickness)
            
            # Prepare label text
            label = f"{pred_class} ({model_score:.2f})"
            
            # Calculate text size for background
            (text_width, text_height), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
            )
            
            # Draw background rectangle for text
            cv2.rectangle(
                overlay,
                (x1, y1 - text_height - baseline - 5),
                (x1 + text_width, y1),
                box_color,
                -1  # Filled rectangle
            )
            
            # Draw text
            cv2.putText(
                overlay,
                label,
                (x1, y1 - baseline - 2),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                text_color,
                1,
                cv2.LINE_AA
            )
    
    # Save the output image
    cv2.imwrite(output_path, overlay)
    print(f"Processed {len(objects)} objects")
    print(f"Output saved to: {output_path}")
    
    return overlay



#URL = 'https://app.biodock.ai/api/external/filesystem-items'
#response = requests.get(URL, headers=headers)
#print(response.text)

def upload_file_biodock(to_upload):
    
    URL = "https://app.biodock.ai/api/external/filesystem-items/upload-file"
    with open(to_upload, "rb") as file_to_upload:
        data = {"fileName": to_upload, "destinationFolder": DESIRED_FOLDER}
        headers = {"X-API-KEY": API_KEY}
        files = {"upload": file_to_upload}
        response = requests.post(URL, data=data, headers=headers, files=files)
        return(response.text)


def analyze_file_biodock(folder_id):
    URL = "https://app.biodock.ai/api/external/analysis-jobs"
    data = {"filesystemIds": folder_id, "pipelineId": PIPELINE_ID}
    response = requests.post(URL, json=data, headers=headers)
    return(response.text)

def get_filesystem_status():
    URL = "https://app.biodock.ai/api/external/filesystem-items"
    response = requests.get(URL, headers=headers)
    return(response.text)
    

def get_analysis_status(ANALYSIS_JOB_IDX):
    URL = f"https://app.biodock.ai/api/external/analysis-jobs/{ANALYSIS_JOB_IDX}"
    response = requests.get(URL, headers=headers)
    return(response.text)

def download_mask(ANALYSIS_JOB_IDY):
    URL = f"https://app.biodock.ai/api/external/analysis-jobs/{ANALYSIS_JOB_IDY}/download-masks"
    headers = {"X-API-KEY": API_KEY, "Content-Type": "application/json"}
    response = requests.get(URL, headers=headers)
    return(response.text)

def submit_mask_job(ANALYSIS_JOB_IDZ):
    URL = fURL = f"https://app.biodock.ai/api/external/analysis-jobs/{ANALYSIS_JOB_IDZ}/download-masks"
    headers = {"X-API-KEY": API_KEY, "Content-Type": "application/json"}
    response = requests.post(URL, headers=headers)
    return(response.text)

def unzip_download(zip_file_path ):
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:

        g_list = zip_ref.infolist()
        json_file_in_zip = g_list[1].filename
        zip_ref.extractall('.')
    print(f"Extracted all files to: .")
    return(json_file_in_zip)


def main():
    local_path = r'C:\\Users\\CMExplorer600252\\Desktop\\test\\'
    os.chdir(local_path)
    biodock_stat = json.loads(upload_file_biodock(FILENAME_IN))
    print('Sleeping')
    time.sleep(5)
    print('Woke up')
    out = json.loads(get_filesystem_status())
    print(out)
    FOLDER_ID = [out['results'][0]['id']]
    biodock_stat = json.loads(analyze_file_biodock(FOLDER_ID))
    print('Getting results')
    anaylsis_job_id  = biodock_stat['id']
    print('Analysis ID:' + anaylsis_job_id)
    time.sleep(1)
    print('Success')
    biodock_stat = json.loads(get_analysis_status(anaylsis_job_id))
    while(biodock_stat['analysisJob']['percentageCompleted'] != 100):
        biodock_stat = json.loads(get_analysis_status(anaylsis_job_id))
        print(str(biodock_stat['analysisJob']['percentageCompleted'] ))
        time.sleep(1)

    biodock_stat = json.loads(submit_mask_job(anaylsis_job_id))    
    time.sleep(1)    
    biodock_stat = json.loads(download_mask(anaylsis_job_id))
    time.sleep(1)
    while(biodock_stat['downloadMasksJob']['percentageCompleted'] != 100):
        biodock_stat = json.loads(download_mask(anaylsis_job_id))
        print(str(biodock_stat['downloadMasksJob']['percentageCompleted'] ))
        time.sleep(1)

    file_url = biodock_stat['downloadMasksJob']['masksZipUrl']
    zip_trunk = 'temp'
    output_filename = zip_trunk + '.zip'
    download_file(file_url, output_filename)
    json_file = unzip_download(output_filename )
    image_sav = zip_trunk+'.png'
    result = overlay_bounding_boxes(json_file, FILENAME_IN , image_sav)
    

if __name__ == '__main__':
    main()

    

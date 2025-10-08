import sys
import cv2
import numpy as np
from astropy.io import fits
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt
import pymysql
import os
import requests
import json
import time
import zipfile

class FITSViewerDB(QMainWindow):
    def __init__(self):
        super().__init__()
        self.fits_file = None
        self.fits_data = None
        self.tif_file = None
        
        # BioDock API configuration
        self.API_KEY = "l2pG99uk2QPmWG8g18DTxaPtVgyPi/aYBDaoZhTq2su8t4VC"
        self.DESIRED_FOLDER = 'API_TEST'
        self.PIPELINE_ID = '62f421862c90ca016540a422'
        
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('FITS Image Viewer & Database Registration')
        self.setGeometry(100, 100, 500, 500)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # File selection section
        file_layout = QHBoxLayout()
        self.file_label = QLabel('No file selected')
        self.file_label.setStyleSheet('padding: 5px; background-color: #f0f0f0;')
        file_btn = QPushButton('Select FITS File')
        file_btn.clicked.connect(self.select_file)
        file_layout.addWidget(self.file_label)
        file_layout.addWidget(file_btn)
        layout.addLayout(file_layout)
        
        # Display image button
        display_btn = QPushButton('Display Image')
        display_btn.clicked.connect(self.display_image)
        layout.addWidget(display_btn)
        
        # Database fields section
        layout.addWidget(QLabel('\nDatabase Registration Fields:'))
        
        # PI field
        pi_layout = QHBoxLayout()
        pi_layout.addWidget(QLabel('PI:'))
        self.pi_input = QLineEdit()
        pi_layout.addWidget(self.pi_input)
        layout.addLayout(pi_layout)
        
        # SPECIES field
        species_layout = QHBoxLayout()
        species_layout.addWidget(QLabel('SPECIES:'))
        self.species_input = QLineEdit()
        species_layout.addWidget(self.species_input)
        layout.addLayout(species_layout)
        
        # DATE field
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel('DATE:'))
        self.date_input = QLineEdit()
        self.date_input.setPlaceholderText('YYYY-MM-DD')
        date_layout.addWidget(self.date_input)
        layout.addLayout(date_layout)
        
        # TECH field
        tech_layout = QHBoxLayout()
        tech_layout.addWidget(QLabel('TECH:'))
        self.tech_input = QLineEdit()
        tech_layout.addWidget(self.tech_input)
        layout.addLayout(tech_layout)
        
        # Register button (GREEN)
        register_btn = QPushButton('Register to Database')
        register_btn.clicked.connect(self.register_to_db)
        register_btn.setStyleSheet('background-color: #4CAF50; color: white; padding: 10px;')
        layout.addWidget(register_btn)
        
        # BioDock API button (ORANGE)
        biodock_btn = QPushButton('Analyze with BioDock API')
        biodock_btn.clicked.connect(self.analyze_with_biodock)
        biodock_btn.setStyleSheet('background-color: #FF8C00; color: white; padding: 10px; font-weight: bold;')
        layout.addWidget(biodock_btn)
        
        # Status label
        self.status_label = QLabel('')
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
    def select_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, 
            'Select FITS File', 
            '', 
            'FITS Files (*.fits *.fit);;All Files (*)'
        )
        if filename:
            self.fits_file = filename
            self.file_label.setText(os.path.basename(filename))
            self.status_label.setText(f'File selected: {filename}')
            
    def display_image(self):
        if not self.fits_file:
            QMessageBox.warning(self, 'No File', 'Please select a FITS file first.')
            return
            
        try:
            # Open FITS file
            with fits.open(self.fits_file) as hdul:
                # Get the primary HDU data
                self.fits_data = hdul[2].data
                
                if self.fits_data is None:
                    QMessageBox.warning(self, 'Error', 'No image data found in FITS file.')
                    return
                
                # Normalize the data for display
                data_normalized = self.normalize_image(self.fits_data)
                
                # Convert to 8-bit for OpenCV
                img_8bit = (data_normalized * 255).astype(np.uint8)
                
                # Display with OpenCV
                cv2.namedWindow('FITS Image', cv2.WINDOW_NORMAL)
                cv2.resizeWindow('FITS Image', 800, 600) 
                cv2.imshow('FITS Image', img_8bit)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
                
                self.status_label.setText('Image displayed successfully.')
                
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Error displaying image: {str(e)}')
            self.status_label.setText(f'Error: {str(e)}')
            
    def normalize_image(self, data):
        """Normalize image data to 0-1 range for display"""
        # Handle potential NaN or inf values
        data_clean = np.nan_to_num(data, nan=0.0, posinf=0.0, neginf=0.0)
        
        # Get min and max values
        vmin = np.percentile(data_clean, 1)  # Use 1st percentile to avoid outliers
        vmax = np.percentile(data_clean, 99)  # Use 99th percentile
        
        # Normalize
        if vmax > vmin:
            normalized = (data_clean - vmin) / (vmax - vmin)
            normalized = np.clip(normalized, 0, 1)
        else:
            normalized = np.zeros_like(data_clean)
            
        return normalized
    
    def register_to_db(self):
        if not self.fits_file:
            QMessageBox.warning(self, 'No File', 'Please select a FITS file first.')
            return
            
        # Get field values
        pi = self.pi_input.text().strip()
        species = self.species_input.text().strip()
        date = self.date_input.text().strip()
        tech = self.tech_input.text().strip()
        
        # Validate inputs
        if not all([pi, species, date, tech]):
            QMessageBox.warning(self, 'Missing Fields', 'Please fill in all fields.')
            return
        
        # Get image filename
        image_name = os.path.basename(self.fits_file)
        
        try:
            # Connect to database
            connection = pymysql.connect(
                host='biodatabase.igb.illinois.edu',
                user='leakey_stomata',
                password='Stomata2025',
                database='leakey_stomata',
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            print('Connected to database')
            
            with connection:
                with connection.cursor() as cursor:
                    # Insert data
                    sql = """INSERT INTO Ingress (image_name, PI, SPECIES, TECH) 
                             VALUES (%s, %s, %s, %s)"""
                    cursor.execute(sql, (image_name, pi, species, tech))
                    
                connection.commit()
                
                QMessageBox.information(self, 'Success', 
                                      f'Image "{image_name}" registered successfully!')
                self.status_label.setText('Registration successful.')
                
                # Clear fields
                self.pi_input.clear()
                self.species_input.clear()
                self.date_input.clear()
                self.tech_input.clear()
                
        except Exception as e:
            QMessageBox.critical(self, 'Database Error', 
                               f'Error registering to database:\n{str(e)}')
            self.status_label.setText(f'Database error: {str(e)}')

    # ========== BioDock API Integration ==========
    
    def analyze_with_biodock(self):
        """Main function to analyze image with BioDock API"""
        if not self.fits_file:
            QMessageBox.warning(self, 'No File', 'Please select a FITS file first.')
            return
        
        try:
            self.status_label.setText('Converting FITS to TIF...')
            QApplication.processEvents()
            
            # Convert FITS to TIF
            tif_filename = self.convert_fits_to_tif()
            
            if not tif_filename:
                return
            
            self.status_label.setText(f'Uploading {tif_filename} to BioDock...')
            QApplication.processEvents()
            
            # Upload file
            biodock_stat = json.loads(self.upload_file_biodock(tif_filename))
            time.sleep(5)
            
            # Get filesystem status
            self.status_label.setText('Getting file system status...')
            QApplication.processEvents()
            out = json.loads(self.get_filesystem_status())
            FOLDER_ID = [out['results'][0]['id']]
            
            # Start analysis
            self.status_label.setText('Starting analysis...')
            QApplication.processEvents()
            biodock_stat = json.loads(self.analyze_file_biodock(FOLDER_ID))
            analysis_job_id = biodock_stat['id']
            
            # Wait for analysis to complete
            self.status_label.setText('Analyzing... 0%')
            QApplication.processEvents()
            time.sleep(1)
            
            biodock_stat = json.loads(self.get_analysis_status(analysis_job_id))
            while biodock_stat['analysisJob']['percentageCompleted'] != 100:
                biodock_stat = json.loads(self.get_analysis_status(analysis_job_id))
                progress = biodock_stat['analysisJob']['percentageCompleted']
                self.status_label.setText(f'Analyzing... {progress}%')
                QApplication.processEvents()
                time.sleep(1)
            
            # Submit mask job
            self.status_label.setText('Requesting masks...')
            QApplication.processEvents()
            biodock_stat = json.loads(self.submit_mask_job(analysis_job_id))
            time.sleep(1)
            
            # Download masks
            self.status_label.setText('Downloading masks... 0%')
            QApplication.processEvents()
            biodock_stat = json.loads(self.download_mask(analysis_job_id))
            time.sleep(1)
            
            while biodock_stat['downloadMasksJob']['percentageCompleted'] != 100:
                biodock_stat = json.loads(self.download_mask(analysis_job_id))
                progress = biodock_stat['downloadMasksJob']['percentageCompleted']
                self.status_label.setText(f'Downloading masks... {progress}%')
                QApplication.processEvents()
                time.sleep(1)
            
            # Download and process results
            file_url = biodock_stat['downloadMasksJob']['masksZipUrl']
            file_stem = os.path.splitext(os.path.basename(self.fits_file))[0]
            zip_filename = f'{file_stem}_results.zip'
            
            self.status_label.setText('Downloading results...')
            QApplication.processEvents()
            self.download_file(file_url, zip_filename)
            
            # Extract and overlay bounding boxes
            self.status_label.setText('Processing results...')
            QApplication.processEvents()
            json_file = self.unzip_download(zip_filename)
            output_image = f'{file_stem}_annotated.png'
            self.overlay_bounding_boxes(json_file, tif_filename, output_image)
            
            # Display the annotated image in a popup window
            self.display_annotated_image(output_image)
            
            QMessageBox.information(self, 'Success', 
                                  f'Analysis complete!\nAnnotated image saved as:\n{output_image}')
            self.status_label.setText(f'Analysis complete! Results saved.')
            
        except Exception as e:
            QMessageBox.critical(self, 'BioDock Error', 
                               f'Error during BioDock analysis:\n{str(e)}')
            self.status_label.setText(f'BioDock error: {str(e)}')
    
    def convert_fits_to_tif(self):
        """Convert FITS file to TIF format"""
        try:
            with fits.open(self.fits_file) as hdul:
                data = hdul[2].data
                
                if data is None:
                    QMessageBox.warning(self, 'Error', 'No image data found in FITS file.')
                    return None
                
                # Normalize the data
                data_normalized = self.normalize_image(data)
                
                # Convert to 8-bit
                img_8bit = (data_normalized * 255).astype(np.uint8)
                
                # Create TIF filename using FITS file stem
                file_stem = os.path.splitext(os.path.basename(self.fits_file))[0]
                tif_filename = f'{file_stem}.tif'
                
                # Save as TIF
                cv2.imwrite(tif_filename, img_8bit)
                self.tif_file = tif_filename
                
                return tif_filename
                
        except Exception as e:
            QMessageBox.critical(self, 'Conversion Error', 
                               f'Error converting FITS to TIF:\n{str(e)}')
            return None
    
    def upload_file_biodock(self, to_upload):
        """Upload file to BioDock"""
        URL = "https://app.biodock.ai/api/external/filesystem-items/upload-file"
        with open(to_upload, "rb") as file_to_upload:
            data = {"fileName": to_upload, "destinationFolder": self.DESIRED_FOLDER}
            headers = {"X-API-KEY": self.API_KEY}
            files = {"upload": file_to_upload}
            response = requests.post(URL, data=data, headers=headers, files=files)
            return response.text
    
    def analyze_file_biodock(self, folder_id):
        """Start analysis job on BioDock"""
        URL = "https://app.biodock.ai/api/external/analysis-jobs"
        data = {"filesystemIds": folder_id, "pipelineId": self.PIPELINE_ID}
        headers = {"X-API-KEY": self.API_KEY, "Content-Type": "application/json"}
        response = requests.post(URL, json=data, headers=headers)
        return response.text
    
    def get_filesystem_status(self):
        """Get filesystem status from BioDock"""
        URL = "https://app.biodock.ai/api/external/filesystem-items"
        headers = {"X-API-KEY": self.API_KEY, "Content-Type": "application/json"}
        response = requests.get(URL, headers=headers)
        return response.text
    
    def get_analysis_status(self, analysis_job_id):
        """Get analysis job status"""
        URL = f"https://app.biodock.ai/api/external/analysis-jobs/{analysis_job_id}"
        headers = {"X-API-KEY": self.API_KEY, "Content-Type": "application/json"}
        response = requests.get(URL, headers=headers)
        return response.text
    
    def download_mask(self, analysis_job_id):
        """Get download mask status"""
        URL = f"https://app.biodock.ai/api/external/analysis-jobs/{analysis_job_id}/download-masks"
        headers = {"X-API-KEY": self.API_KEY, "Content-Type": "application/json"}
        response = requests.get(URL, headers=headers)
        return response.text
    
    def submit_mask_job(self, analysis_job_id):
        """Submit mask download job"""
        URL = f"https://app.biodock.ai/api/external/analysis-jobs/{analysis_job_id}/download-masks"
        headers = {"X-API-KEY": self.API_KEY, "Content-Type": "application/json"}
        response = requests.post(URL, headers=headers)
        return response.text
    
    def download_file(self, url, local_filename):
        """Download a file from URL"""
        try:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                with open(local_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            print(f"File '{local_filename}' downloaded successfully")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading file: {e}")
            raise
    
    def unzip_download(self, zip_file_path):
        """Extract zip file and return JSON filename"""
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            g_list = zip_ref.infolist()
            json_file_in_zip = g_list[1].filename
            zip_ref.extractall('.')
        print(f"Extracted all files to current directory")
        return json_file_in_zip
    
    def overlay_bounding_boxes(self, json_path, image_path, output_path):
        """Overlay bounding boxes on image"""
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Could not read image at {image_path}")
        
        overlay = img.copy()
        objects = data.get('objects', {})
        
        box_color = (0, 255, 0)  # Green
        text_color = (0, 0, 0)  # Black
        thickness = 2
        
        for obj_id, obj_data in objects.items():
            bbox = obj_data.get('bbox')
            pred_class = obj_data.get('pred_class', 'Unknown')
            model_score = obj_data.get('model_score', 0)
            
            if bbox and len(bbox) == 4:
                x1, y1, x2, y2 = bbox
                
                cv2.rectangle(overlay, (x1, y1), (x2, y2), box_color, thickness)
                
                label = f"{pred_class} ({model_score:.2f})"
                
                (text_width, text_height), baseline = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
                )
                
                cv2.rectangle(
                    overlay,
                    (x1, y1 - text_height - baseline - 5),
                    (x1 + text_width, y1),
                    box_color,
                    -1
                )
                
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
        
        cv2.imwrite(output_path, overlay)
        print(f"Processed {len(objects)} objects")
        print(f"Output saved to: {output_path}")
    
    def display_annotated_image(self, image_path):
        """Display the annotated image in an OpenCV window"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Could not read image at {image_path}")
            
            # Create window with specific name
            window_name = 'BioDock Analysis Results'
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_name, 800, 600)
            cv2.imshow(window_name, img)
            
            # Wait for user to close window
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            
        except Exception as e:
            print(f"Error displaying annotated image: {e}")

def main():
    # Check for command line argument
    if len(sys.argv) > 1:
        fits_file_arg = sys.argv[1]
    else:
        fits_file_arg = None
    
    app = QApplication(sys.argv)
    window = FITSViewerDB()
    
    # If file provided as argument, load it
    if fits_file_arg and os.path.exists(fits_file_arg):
        window.fits_file = fits_file_arg
        window.file_label.setText(os.path.basename(fits_file_arg))
        window.status_label.setText(f'File loaded: {fits_file_arg}')
    
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

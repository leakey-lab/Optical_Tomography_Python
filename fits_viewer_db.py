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

class FITSViewerDB(QMainWindow):
    def __init__(self):
        super().__init__()
        self.fits_file = None
        self.fits_data = None
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle('FITS Image Viewer & Database Registration')
        self.setGeometry(100, 100, 500, 400)
        
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
        
        # Register button
        register_btn = QPushButton('Register to Database')
        register_btn.clicked.connect(self.register_to_db)
        register_btn.setStyleSheet('background-color: #4CAF50; color: white; padding: 10px;')
        layout.addWidget(register_btn)
        
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

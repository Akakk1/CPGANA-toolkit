'''
Copyright 2024 JunqiaoZhu Zhejiang Sci-Tech University

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
'''

import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QFileDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QProgressBar, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from Bio import SeqIO

class KaksTransformApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.species_folder_path = None
        self.reference_species_folder_path = None
        self.output_folder_path = None
    
    def initUI(self):
        layout = QVBoxLayout()

        # Title label
        title_label = QLabel('Transform ccds to pairwise sequence')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont('Arial', 16))
        layout.addWidget(title_label)

        # Horizontal layout for species folder
        species_layout = QHBoxLayout()
        self.species_label = QLabel("Input Directory:")
        layout.addWidget(self.species_label)
        self.species_path_box = QTextEdit("A folder containing all pending species of cCDS to be processed")
        self.species_path_box.setReadOnly(True)
        species_layout.addWidget(self.species_path_box)
        self.species_button = QPushButton("Browse")
        self.species_button.clicked.connect(self.select_species_folder)
        species_layout.addWidget(self.species_button)
        layout.addLayout(species_layout)
        
        # Horizontal layout for reference species folder
        reference_layout = QHBoxLayout()
        self.reference_label = QLabel("Reference Species:")
        reference_layout.addWidget(self.reference_label)
        self.reference_path_box = QTextEdit("A folder for reference species")
        self.reference_path_box.setReadOnly(True)
        self.reference_path_box.setMaximumHeight(30)
        reference_layout.addWidget(self.reference_path_box)
        self.reference_button = QPushButton("Browse")
        self.reference_button.clicked.connect(self.select_reference_folder)
        reference_layout.addWidget(self.reference_button)
        layout.addLayout(reference_layout)
        
        # Horizontal layout for output folder
        output_layout = QHBoxLayout()
        self.output_label = QLabel("Output Directory:")
        output_layout.addWidget(self.output_label)
        self.output_path_box = QTextEdit()
        self.output_path_box.setReadOnly(True)
        self.output_path_box.setMaximumHeight(30)
        output_layout.addWidget(self.output_path_box)
        self.output_button = QPushButton("Browse")
        self.output_button.clicked.connect(self.select_output_folder)
        output_layout.addWidget(self.output_button)
        layout.addLayout(output_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)
        
        # Run button
        self.run_button = QPushButton("Run Integration")
        self.run_button.clicked.connect(self.run_integration)
        layout.addWidget(self.run_button)
        
        self.setLayout(layout)
        self.setWindowTitle('Folder Selection')
        self.show()
    
    def select_species_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Species Folder")
        if folder_path:
            self.species_folder_path = folder_path
            self.species_path_box.setText(folder_path)
    
    def select_reference_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Reference Species Folder")
        if folder_path:
            self.reference_species_folder_path = folder_path
            self.reference_path_box.setText(folder_path)
    
    def select_output_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Output Folder")
        if folder_path:
            self.output_folder_path = folder_path
            self.output_path_box.setText(folder_path)
    
    def run_integration(self):
        if not self.species_folder_path or not self.reference_species_folder_path or not self.output_folder_path:
            QMessageBox.warning(self, "Warning", "Please select all folders before running integration.")
            return

        # Reference species details
        reference_species = os.path.basename(self.reference_species_folder_path)
        reference_cds_sequences = {}
        
        # Get reference species CDS sequences
        for ref_filename in os.listdir(self.reference_species_folder_path):
            if ref_filename.endswith('.fasta'):
                ref_filepath = os.path.join(self.reference_species_folder_path, ref_filename)
                ref_cds_name = os.path.splitext(ref_filename)[0]
                
                reference_cds_sequences[ref_cds_name] = []
                
                with open(ref_filepath, 'r') as ref_input_handle:
                    for record in SeqIO.parse(ref_input_handle, 'fasta'):
                        sequence = str(record.seq)
                        reference_cds_sequences[ref_cds_name].append(sequence)
        
        # Process each species folder
        species_folders = [folder for folder in os.listdir(self.species_folder_path) if os.path.isdir(os.path.join(self.species_folder_path, folder))]
        total_species = len(species_folders)
        self.progress_bar.setMaximum(total_species)
        
        for i, species_folder in enumerate(species_folders):
            species_folder_path = os.path.join(self.species_folder_path, species_folder)
            
            # Output file path
            output_file = f'{species_folder}_and_{reference_species}.fasta'
            output_path = os.path.join(self.output_folder_path, output_file)
            
            # Write integrated sequences to output file
            with open(output_path, 'w') as output_handle:
                for filename in os.listdir(species_folder_path):
                    if filename.endswith('.fasta'):
                        filepath = os.path.join(species_folder_path, filename)
                        cds_name = os.path.splitext(filename)[0]
                        
                        output_handle.write(f">{cds_name}\n")
                        
                        with open(filepath, 'r') as input_handle:
                            for record in SeqIO.parse(input_handle, 'fasta'):
                                sequence = str(record.seq)
                                output_handle.write(f"{sequence}\n")
                        
                        if cds_name in reference_cds_sequences:
                            for sequence in reference_cds_sequences[cds_name]:
                                output_handle.write(f"{sequence}\n")
                        
                        output_handle.write("\n")
            
            self.progress_bar.setValue(i + 1)
            print(f"Integration for {species_folder} and {reference_species} completed.")
        
        QMessageBox.information(self, "Completed", f"Integration completed. Files saved in {self.output_folder_path}.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = KaksTransformApp()
    sys.exit(app.exec_())

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

import sys
import os
import logging
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QFileDialog, QPlainTextEdit, QVBoxLayout, QHBoxLayout, QMessageBox, QLineEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from Bio import SeqIO

class commoncdsExtractApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.logger = self.setup_logger()

    def initUI(self):
        self.setWindowTitle('Common CDS Extraction')
        self.setGeometry(100, 100, 600, 400)

        # Widgets for selecting GenBank files
        file_layout = QHBoxLayout()
        self.file_label = QLabel('GenBank file(s):')
        self.file_textedit = QPlainTextEdit()
        self.file_textedit.setReadOnly(True)
        self.file_textedit.setMinimumWidth(300)  # Adjusted height
        self.browse_button = QPushButton('Browse')
        self.browse_button.clicked.connect(self.browse_files)

        file_layout.addWidget(self.file_label)
        file_layout.addWidget(self.file_textedit)
        file_layout.addWidget(self.browse_button)

        # Widgets for selecting output directory
        output_layout = QHBoxLayout()
        self.output_label = QLabel('Output directory:')
        self.output_textedit = QLineEdit()  # Changed to QLineEdit
        self.output_button = QPushButton('Browse')
        self.output_button.clicked.connect(self.select_output_directory)

        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_textedit)
        output_layout.addWidget(self.output_button)

        # Run button
        self.run_button = QPushButton('Run Extraction')
        self.run_button.clicked.connect(self.run_extraction)

        # Main layout
        layout = QVBoxLayout()
        label_title = QLabel('Extract Common CDS')
        label_title.setFont(QFont('Arial', 16))
        layout.addWidget(label_title, alignment=Qt.AlignCenter)
        
        layout.addLayout(file_layout)
        layout.addLayout(output_layout)
        layout.addWidget(self.run_button)
        
        self.setLayout(layout)

    def browse_files(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, 'GenBank file(s)', '', 'GenBank Files (*.gb *.gbk)', options=options)
        if files:
            self.file_textedit.setPlainText('\n'.join(files))

    def select_output_directory(self):
        options = QFileDialog.Options()
        directory = QFileDialog.getExistingDirectory(self, 'Output Directory', options=options)
        if directory:
            self.output_textedit.setText(directory)

    def run_extraction(self):
        input_files = self.file_textedit.toPlainText().strip().split('\n')
        output_directory = self.output_textedit.text().strip()

        if not input_files or not output_directory:
            self.logger.error('Please select input files and output directory.')
            QMessageBox.warning(self, 'Missing Input', 'Please select input files and output directory.')
            return

        common_cds = self.find_common_cds(input_files)
        if common_cds:
            self.logger.info(f'Common CDS names: {common_cds}')
            success = self.extract_and_save_cds_sequences(input_files, output_directory, common_cds)
            if success:
                QMessageBox.information(self, 'Extraction Complete', 'CDS extraction and saving completed successfully.')
            else:
                QMessageBox.critical(self, 'Extraction Failed', 'Failed to extract and save CDS sequences.')
        else:
            QMessageBox.warning(self, 'No Common CDS', 'No common CDS names found.')

    def find_common_cds(self, input_files):
        """Find common CDS names from all GenBank files in the given directory."""
        common_cds = None
        for input_file in input_files:
            if os.path.isfile(input_file) and (input_file.endswith(".gb") or input_file.endswith(".gbk")):
                cds_names = set()
                with open(input_file, 'r') as handle:
                    for record in SeqIO.parse(handle, 'genbank'):
                        for feature in record.features:
                            if feature.type == 'CDS':
                                gene_name = feature.qualifiers.get('gene', feature.qualifiers.get('locus_tag', ['Unknown']))[0]
                                cds_names.add(gene_name)
                if common_cds is None:
                    common_cds = cds_names
                else:
                    common_cds = common_cds.intersection(cds_names)
                self.logger.info(f"Updated common CDS names after processing {input_file}: {common_cds}")
        return common_cds

    def extract_and_save_cds_sequences(self, input_files, output_directory, common_cds):
        """Extract and save CDS sequences of common CDS names from all GenBank files."""
        try:
            individual_dir = os.path.join(output_directory, "individual_cds")
            os.makedirs(individual_dir, exist_ok=True)
            
            combined_dir = os.path.join(output_directory, "common_cds")
            os.makedirs(combined_dir, exist_ok=True)
            
            cds_sequences = {cds: [] for cds in common_cds}

            for input_file in input_files:
                if os.path.isfile(input_file) and (input_file.endswith(".gb") or input_file.endswith(".gbk")):
                    species_name = os.path.splitext(os.path.basename(input_file))[0]
                    species_dir = os.path.join(individual_dir, species_name)
                    os.makedirs(species_dir, exist_ok=True)
                    self.logger.info(f"Processing file {input_file}")
                    
                    with open(input_file, "r") as handle:
                        for record in SeqIO.parse(handle, "genbank"):
                            for feature in record.features:
                                if feature.type == "CDS":
                                    gene_name = feature.qualifiers.get("gene", feature.qualifiers.get("locus_tag", ["Unknown"]))[0]
                                    if gene_name in common_cds:
                                        cds_sequence = feature.location.extract(record).seq
                                        
                                        individual_fasta_file = os.path.join(species_dir, f"{gene_name}.fasta")
                                        with open(individual_fasta_file, "w") as individual_fasta_handle:
                                            individual_fasta_handle.write(f">{species_name}_{gene_name}\n{cds_sequence}\n")
                                        self.logger.info(f"Saved CDS sequence for {gene_name} from {species_name} to {individual_fasta_file}")
                                        
                                        fasta_entry = f">{species_name}_{gene_name}\n{cds_sequence}\n"
                                        cds_sequences[gene_name].append(fasta_entry)

            for gene_name, sequences in cds_sequences.items():
                combined_fasta_file = os.path.join(combined_dir, f"{gene_name}.fasta")
                with open(combined_fasta_file, "w") as combined_fasta_handle:
                    combined_fasta_handle.writelines(sequences)
                self.logger.info(f"Saved combined CDS sequences for {gene_name} to {combined_fasta_file}")

            self.combine_species_cds_sequences(individual_dir, common_cds)
            return True  # Assume success for simplicity

        except Exception as e:
            self.logger.error(f"Error during extraction: {e}")
            QMessageBox.critical(self, 'Extraction Error', f'Error during extraction: {e}')
            return False

    def combine_species_cds_sequences(self, individual_dir, common_cds):
        """Combine CDS sequences of each species into a single file without duplicates."""
        for species_folder in os.listdir(individual_dir):
            species_folder_path = os.path.join(individual_dir, species_folder)
            if os.path.isdir(species_folder_path):
                combined_species_file = os.path.join(individual_dir, f"{species_folder}_combined.fasta")
                seen_sequences = set()
                with open(combined_species_file, "w") as combined_fasta_handle:
                    for cds_name in common_cds:
                        cds_file = os.path.join(species_folder_path, f"{cds_name}.fasta")
                        if os.path.exists(cds_file):
                            with open(cds_file, "r") as single_cds_handle:
                                for line in single_cds_handle:
                                    if line.startswith(">"):
                                        sequence_id = line.strip()
                                        sequence = ""
                                    else:
                                        sequence = line.strip()
                                        if sequence not in seen_sequences:
                                            combined_fasta_handle.write(f"{sequence_id}\n{sequence}\n")
                                            seen_sequences.add(sequence)
                self.logger.info(f"Combined CDS sequences for {species_folder} into {combined_species_file}")

    def setup_logger(self):
        log_file = "genbank_cds_extraction.log"
        logging.basicConfig(level=logging.INFO, 
                            format='%(asctime)s - %(levelname)s - %(message)s',
                            handlers=[
                                logging.FileHandler(log_file),
                                logging.StreamHandler()
                            ])
        return logging.getLogger()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = commoncdsExtractApp()
    ex.show()
    sys.exit(app.exec_())

"""
This code is built based on the following work
CPStools-RSCU.py
Author: Xu wenbo
Org:    China Pharmaceutical University
Email:  xwb7533@163.com
site:   https://github.com/Xwb7533/CPStools
"""

import os
import sys
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit, 
                             QPushButton, QFileDialog, QMessageBox, QGridLayout, QWidget, QCheckBox, QComboBox, QProgressBar)
from Bio import SeqIO

class RSCUCalculateApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("RSCU Calculator")       
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QGridLayout()
        layout.setVerticalSpacing(20)
        central_widget.setLayout(layout)
                
        # Title label
        title_label = QLabel("Calculate RSCU Values")
        title_label.setFont(QFont('Arial', 16))
        layout.addWidget(title_label, 0, 0, 1, 3, alignment=Qt.AlignCenter)
        
        # GenBank Files
        self.file_label = QLabel("GenBank Files:")
        layout.addWidget(self.file_label, 1, 0)
        
        self.file_entry = QLineEdit(self)
        layout.addWidget(self.file_entry, 1, 1)
        
        self.browse_button = QPushButton("Browse", self)
        self.browse_button.clicked.connect(self.browse_button_clicked)
        layout.addWidget(self.browse_button, 1, 2)

        # Output Directory
        self.output_dir_label = QLabel("Output Directory:")
        layout.addWidget(self.output_dir_label, 2, 0)
        
        self.output_dir_entry = QLineEdit(self)
        layout.addWidget(self.output_dir_entry, 2, 1)
        
        self.output_dir_button = QPushButton("Browse", self)
        self.output_dir_button.clicked.connect(self.output_dir_button_clicked)
        layout.addWidget(self.output_dir_button, 2, 2)
        
        # Filter Length
        self.filter_checkbox = QCheckBox("Filter sequences by length", self)
        self.filter_checkbox.setChecked(True)
        self.filter_checkbox.stateChanged.connect(self.toggle_filter_length_entry)
        layout.addWidget(self.filter_checkbox, 3, 0, 1, 2)
        
        self.filter_length_label = QLabel("Filter Length:")
        layout.addWidget(self.filter_length_label, 4, 0)
        
        self.filter_length_entry = QLineEdit(self)
        self.filter_length_entry.setText("300")
        layout.addWidget(self.filter_length_entry, 4, 1)
        
        # Filter non-ATG start
        self.filter_nonatg_checkbox = QCheckBox("Keep non-ATG start codons", self)
        self.filter_nonatg_checkbox.setChecked(False)
        layout.addWidget(self.filter_nonatg_checkbox, 5, 0, 1, 2)
        
        # Run Button
        self.run_button = QPushButton("Run RSCU Calculation", self)
        self.run_button.clicked.connect(self.run_rscu_calculation)
        layout.addWidget(self.run_button, 7, 1, alignment=Qt.AlignCenter)

        # Progress Bar
        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar, 8, 0, 1, 3)
        
    def toggle_filter_length_entry(self):
        self.filter_length_entry.setEnabled(self.filter_checkbox.isChecked())

    def browse_button_clicked(self):
        file_paths, _ = QFileDialog.getOpenFileNames(self, "Select GenBank Files", "", "GenBank files (*.gb *.gbk)")
        if file_paths:
            self.file_entry.setText(";".join(file_paths))

    def output_dir_button_clicked(self):
        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if output_dir:
            self.output_dir_entry.setText(output_dir)

    def run_rscu_calculation(self):
        file_paths_str = self.file_entry.text()
        file_paths = file_paths_str.split(";")
        
        output_dir = self.output_dir_entry.text()
        if not output_dir:
            QMessageBox.critical(self, "Error", "Please select an output directory.")
            return

        filter_sequences = self.filter_checkbox.isChecked()
        if filter_sequences:
            filter_length = self.filter_length_entry.text()
            try:
                filter_length = int(filter_length)
            except ValueError:
                QMessageBox.critical(self, "Error", "Filter Length must be a valid integer.")
                return
        else:
            filter_length = None
        
        keep_non_atg = self.filter_nonatg_checkbox.isChecked()
        
        if not file_paths_str:
            QMessageBox.critical(self, "Error", "Please select GenBank file(s).")
            return

        self.thread = CalculationThread(file_paths, filter_length, keep_non_atg, output_dir)
        self.thread.progress.connect(self.update_progress)
        self.thread.finished.connect(self.calculation_finished)
        self.thread.start()
        
    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def calculation_finished(self):
        QMessageBox.information(self, "Finished", "RSCU calculation completed successfully for all files.")

class CalculationThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, file_paths, filter_length, keep_non_atg, output_dir):
        super().__init__()
        self.file_paths = file_paths
        self.filter_length = filter_length
        self.keep_non_atg = keep_non_atg
        self.output_dir = output_dir

    def run(self):
        total_files = len(self.file_paths)
        for index, file_path in enumerate(self.file_paths):
            try:
                self.process_genbank_file(file_path, self.filter_length, self.keep_non_atg, self.output_dir)
            except Exception as e:
                print(f"Error occurred processing {file_path}: {str(e)}")
                continue
            self.progress.emit(int((index + 1) / total_files * 100))
        self.finished.emit()

    def process_genbank_file(self, file_path, filter_length, keep_non_atg, output_dir):
        genes = set()
        for rec in SeqIO.parse(file_path, 'genbank'):
            for feature in rec.features:
                if feature.type == 'CDS' and 'gene' in feature.qualifiers:
                    genes.add(feature.qualifiers['gene'][0])
        
        file_name, file_extension = os.path.splitext(os.path.basename(file_path))
        results_dir = os.path.join(output_dir, file_name + '_results')
        os.makedirs(results_dir, exist_ok=True)
        
        print(f"Processing {os.path.basename(file_path)}...")
        
        no_duplicates_file = os.path.join(results_dir, 'no_duplicates.fasta')
        self.remove_duplicate_sequences(file_path, no_duplicates_file, genes)
        
        if filter_length is not None:
            filtered_file = os.path.join(results_dir, f'filtered_{filter_length}.fasta')
            self.filter_sequences_by_length(no_duplicates_file, filtered_file, filter_length, keep_non_atg, results_dir)
            final_input_file = filtered_file
        else:
            final_input_file = no_duplicates_file
        
        merged_file = os.path.join(results_dir, 'merged_cds.fasta')
        self.merge_sequences(final_input_file, merged_file)
        
        output_file = os.path.join(results_dir, 'RSCU_values.txt')
        self.calculate_rscu_values(merged_file, output_file)
        
        print(f"RSCU calculation completed for {os.path.basename(file_path)}.")
    
    def remove_duplicate_sequences(self, input_file, output_file, genes):
        with open(output_file, 'w') as ff:
            for gene in genes:
                for rec in SeqIO.parse(input_file, 'genbank'):
                    sequences = [feature.extract(rec.seq) for feature in rec.features if feature.type == 'CDS' and feature.qualifiers['gene'][0] == gene]
                    
                    if len(sequences) == 1:
                        ff.write(f'>{gene}\n{str(sequences[0])}\n')
                    elif len(sequences) == 2:
                        longer_seq = max(sequences, key=len)
                        ff.write(f'>{gene}\n{str(longer_seq)}\n')

    def filter_sequences_by_length(self, input_file, output_file, filter_length, keep_non_atg, results_dir):
        filter_log_file = os.path.join(results_dir, 'filter_log.txt')
        saved_sequences_file = os.path.join(results_dir, 'saved_sequences.txt')
        
        with open(output_file, 'w') as ff, open(filter_log_file, 'w') as filter_log, open(saved_sequences_file, 'w') as saved_sequences:
            saved_count = 0
            for rec in SeqIO.parse(input_file, 'fasta'):
                if len(rec.seq) >= filter_length and (keep_non_atg or rec.seq[:3] == 'ATG'):
                    saved_sequences.write(f"{rec.id}\n")
                    saved_count += 1
                    ff.write(f'>{rec.id}\n{str(rec.seq)}\n')
                else:
                    if len(rec.seq) < filter_length:
                        filter_log.write(f"{rec.id}\tSequence length smaller than {filter_length} bp\n")
                    if not keep_non_atg and rec.seq[:3] != 'ATG':
                        filter_log.write(f"{rec.id}\tSequence does not start with ATG\n")
            
            print(f"After filtering, {saved_count} sequences were saved.")
            saved_sequences.write(f"Total saved: {saved_count}\n")

    def merge_sequences(self, input_file, output_file):
        with open(output_file, 'w') as merge_fasta:
            merge_fasta.write(">merged_cds\n")
            for rec in SeqIO.parse(input_file, 'fasta'):
                merge_fasta.write(str(rec.seq))
                
    def calculate_rscu_values(self, input_file, output_file):
        condonTable = {
            'TGG': 'Trp', 'GGT': 'Gly', 'AGG': 'Arg', 'CGA': 'Arg',
            'TGT': 'Cys', 'GGG': 'Gly', 'AGA': 'Arg', 'CGC': 'Arg',
            'TGC': 'Cys', 'GGA': 'Gly', 'AGC': 'Ser', 'CGG': 'Arg',
            'TAC': 'Tyr', 'GGC': 'Gly', 'AGT': 'Ser', 'CGT': 'Arg',
            'TAT': 'Tyr', 'GAT': 'Asp', 'AAG': 'Lys', 'CAA': 'Gln',
            'TCT': 'Ser', 'GAC': 'Asp', 'AAA': 'Lys', 'CAG': 'Gln',
            'TCG': 'Ser', 'GAA': 'Glu', 'AAC': 'Asn', 'CAT': 'His',
            'TCA': 'Ser', 'GAG': 'Glu', 'AAT': 'Asn', 'CAC': 'His',
            'TCC': 'Ser', 'GCA': 'Ala', 'ACC': 'Thr', 'CCT': 'Pro',
            'TTT': 'Phe', 'GCC': 'Ala', 'ACA': 'Thr', 'CCG': 'Pro',
            'TTC': 'Phe', 'GCG': 'Ala', 'ACG': 'Thr', 'CCA': 'Pro',
            'TTG': 'Leu', 'GCT': 'Ala', 'ACT': 'Thr', 'CCC': 'Pro',
            'TTA': 'Leu', 'GTA': 'Val', 'ATC': 'Ile', 'CTA': 'Leu',
            'TAG': 'Ter', 'GTC': 'Val', 'ATA': 'Ile', 'CTT': 'Leu',
            'TGA': 'Ter', 'GTG': 'Val', 'ATT': 'Ile', 'CTC': 'Leu',
            'TAA': 'Ter', 'GTT': 'Val', 'ATG': 'Met', 'CTG': 'Leu'
        }
        
        seqs = [rec.seq for rec in SeqIO.parse(input_file, format='fasta')][0]
        seqs = str(seqs)
        
        aa_list = [seqs[i:i+3] for i in range(0, len(seqs), 3)]
        
        number_codon = [[key, aa_list.count(key), value] for key, value in condonTable.items()]
        
        with open(output_file, 'w') as calculate_results:
            all_single_amino_number = {}
            all_same_number = {}
            
            for codon_name, codon_number, amino_name in number_codon:
                if amino_name not in all_single_amino_number:
                    all_single_amino_number[amino_name] = codon_number
                    all_same_number[amino_name] = 1
                else:
                    all_single_amino_number[amino_name] += codon_number
                    all_same_number[amino_name] += 1
            
            for codon_name, codon_number, amino_name in number_codon:
                rscu_value = round(codon_number / (all_single_amino_number[amino_name] / all_same_number[amino_name]), 2)
                calculate_results.write(f"{amino_name}\t{codon_name}\t{codon_number}\t{rscu_value}\n")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = RSCUCalculateApp()
    main_window.show()
    sys.exit(app.exec_())

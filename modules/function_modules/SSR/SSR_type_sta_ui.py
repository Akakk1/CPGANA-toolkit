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
import pandas as pd
from tqdm import tqdm
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QFileDialog, QMessageBox, QHBoxLayout, QCheckBox)

class SSRCounter_typeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_files = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle("SSRCounter - Type")

        layout = QVBoxLayout()

        # Title label
        label_title = QLabel("Count SSRs - Type")
        label_title.setStyleSheet("font-size: 16px;")
        layout.addWidget(label_title)

        # Frame for directory selection
        frame_directory = QHBoxLayout()
        
        label_directory = QLabel("Selected Files:")
        frame_directory.addWidget(label_directory)
        
        self.entry_directory = QLineEdit()
        frame_directory.addWidget(self.entry_directory)
        
        button_select = QPushButton("Select Files")
        button_select.clicked.connect(self.select_files)
        frame_directory.addWidget(button_select)
        
        layout.addLayout(frame_directory)
        
        # Checkbox for complementary type statistics
        self.checkbox_complementary = QCheckBox("Include complementary type statistics")
        layout.addWidget(self.checkbox_complementary)
        
        # Frame for buttons
        frame_buttons = QHBoxLayout()
        
        button_start = QPushButton("Start Processing")
        button_start.clicked.connect(self.start_processing)
        frame_buttons.addWidget(button_start)

        layout.addLayout(frame_buttons)

        self.setLayout(layout)

    def select_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select Files", "", "Text Files (*);;All Files (*)")
        if files:
            self.selected_files = files
            self.entry_directory.setText(", ".join(files))

    def count_type_counts(self, file_path):
        # Count different types in the first column, skipping the first row
        df = pd.read_csv(file_path, sep='\t', header=None, skiprows=1)
        type_counts = df.iloc[:, 0].value_counts()  # 1st column index is 0
        
        return type_counts.to_dict()

    def reverse_complement(self, seq):
        complement = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
        try:
            return ''.join(complement[base] for base in reversed(seq))
        except KeyError as e:
            print(f"Warning: Skipping invalid character {e} in sequence {seq}")
            return seq

    def canonical_form(self, seq):
        rev_comp = self.reverse_complement(seq)
        return min(seq, rev_comp)

    def canonical_key(self, seq):
        rev_comp = self.reverse_complement(seq)
        return f"{seq}/{rev_comp}" if seq < rev_comp else f"{rev_comp}/{seq}"

    def main(self, files, output_file, complementary):
        all_type_counts = {}
        
        for file in tqdm(files, desc="Processing files"):
            file_path = file
            species_name = '_'.join(os.path.basename(file).split('_')[:2])
            species_name = species_name.replace('_', ' ').replace('.anno', '')
            type_counts = self.count_type_counts(file_path)
            all_type_counts[species_name] = type_counts
        
        all_types = sorted(set.union(*[set(counts.keys()) for counts in all_type_counts.values()]))
        
        with open(output_file, 'w') as f:
            # Write header
            f.write('Species\t' + '\t'.join(all_types) + '\tTotal\n')
            
            # Write data for each species
            for species_name, type_counts in all_type_counts.items():
                counts = [type_counts.get(key, 0) for key in all_types]
                total_count = sum(counts)
                f.write(species_name + '\t' + '\t'.join(map(str, counts)) + f'\t{total_count}\n')
        
        # If complementary statistics are needed
        if complementary:
            classified_counts = {}
            for species_name, type_counts in all_type_counts.items():
                classified_counts[species_name] = {}
                for type_, count in type_counts.items():
                    canonical_type = self.canonical_form(type_)
                    key = self.canonical_key(type_)
                    if key in classified_counts[species_name]:
                        classified_counts[species_name][key] += count
                    else:
                        classified_counts[species_name][key] = count
            
            output_file_2 = os.path.join(os.path.dirname(output_file), 'output_SSR_counts_type_2.statistics')
            all_classified_types = sorted(set.union(*[set(counts.keys()) for counts in classified_counts.values()]))
            
            with open(output_file_2, 'w') as f:
                # Write header
                f.write('Species\t' + '\t'.join(all_classified_types) + '\tTotal\n')
                
                # Write data for each species
                for species_name, type_counts in classified_counts.items():
                    counts = [type_counts.get(key, 0) for key in all_classified_types]
                    total_count = sum(counts)
                    f.write(species_name + '\t' + '\t'.join(map(str, counts)) + f'\t{total_count}\n')
            
            QMessageBox.information(self, "Success", f"Output files have been created:\n{output_file}\n{output_file_2}")
        else:
            QMessageBox.information(self, "Success", f"Output file has been created: {output_file}")

    def start_processing(self):
        if self.selected_files:
            directory = os.path.dirname(self.selected_files[0])
            output_file = os.path.join(directory, 'output_SSR_counts_type_1.statistics')
            complementary = self.checkbox_complementary.isChecked()
            self.main(self.selected_files, output_file, complementary)
        else:
            QMessageBox.warning(self, "Warning", "Please select files first.")

def main():
    app = QApplication(sys.argv)
    window = SSRCounter_typeApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

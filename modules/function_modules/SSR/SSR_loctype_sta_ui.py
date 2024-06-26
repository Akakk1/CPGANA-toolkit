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
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QFileDialog, QMessageBox, QHBoxLayout)

class SSRCounter_loctypeApp(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_files = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle("SSRCounter - LocationType")

        layout = QVBoxLayout()

        # Title label
        label_title = QLabel("Count SSRs - LocationType")
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
        # Count different types in the sixth column
        df = pd.read_csv(file_path, sep='\t')
        type_counts = df.iloc[:, 5].value_counts()  # 6th column index is 5
        
        return type_counts.to_dict()

    def main(self, files, output_file):
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
            f.write('Species\t' + '\t'.join(all_types) + '\n')
            
            # Write data for each species
            for species_name, type_counts in all_type_counts.items():
                counts = [type_counts.get(key, 0) for key in all_types]
                f.write(species_name + '\t' + '\t'.join(map(str, counts)) + '\n')

        QMessageBox.information(self, "Success", f"Output file has been created: {output_file}")

    def start_processing(self):
        if self.selected_files:
            directory = os.path.dirname(self.selected_files[0])
            output_file = os.path.join(directory, 'output_SSR_counts_loctype.statistics')
            self.main(self.selected_files, output_file)
        else:
            QMessageBox.warning(self, "Warning", "Please select files first.")

def main():
    app = QApplication(sys.argv)
    window = SSRCounter_loctypeApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

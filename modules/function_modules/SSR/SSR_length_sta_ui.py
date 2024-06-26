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
                             QFileDialog, QMessageBox, QHBoxLayout)

class SSRCounter_lengthApp(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_files = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle("SSRCounter - Length")

        layout = QVBoxLayout()

        # Title label
        label_title = QLabel("Count SSRs - Length")
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

    def count_repeats(self, file_path):
        df = pd.read_csv(file_path, sep='\t', header=None, skiprows=1)
        repeat_counts = df[0].value_counts()
        
        length_counts = {}
        for repeat, count in repeat_counts.items():
            length = len(repeat)
            key = f'P{length}'
            if key in length_counts:
                length_counts[key] += count
            else:
                length_counts[key] = count
        
        return length_counts

    def main(self, files, output_file):
        all_length_counts = {}
        
        for file in tqdm(files, desc="Processing files"):
            file_path = file
            species_name = '_'.join(os.path.basename(file).split('_')[:2])
            species_name = species_name.replace('_', ' ')
            length_counts = self.count_repeats(file_path)
            all_length_counts[species_name] = length_counts
        
        all_keys = sorted(set.union(*[set(counts.keys()) for counts in all_length_counts.values()]), key=lambda x: int(x[1:]))
        
        with open(output_file, 'w') as f:
            f.write('Species\t' + '\t'.join(all_keys) + '\tTotal\n')
            
            for species_name, length_counts in all_length_counts.items():
                counts = [length_counts.get(key, 0) for key in all_keys]
                sum_counts = sum(counts)
                f.write(species_name + '\t' + '\t'.join(map(str, counts)) + f'\t{sum_counts}\n')

        QMessageBox.information(self, "Success", f"Output file has been created: {output_file}")

    def start_processing(self):
        if self.selected_files:
            directory = os.path.dirname(self.selected_files[0])
            output_file = os.path.join(directory, 'output_SSR_counts_length.statistics')
            self.main(self.selected_files, output_file)
        else:
            QMessageBox.warning(self, "Warning", "Please select files first.")

def main():
    app = QApplication(sys.argv)
    window = SSRCounter_lengthApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

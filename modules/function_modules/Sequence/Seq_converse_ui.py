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
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QFileDialog, QVBoxLayout, QWidget, QMessageBox, QComboBox, QHBoxLayout)
from Bio import SeqIO

class FileFormatConvertApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("File Format Conversion")
        self.setGeometry(100, 100, 600, 250)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Title label
        label_title = QLabel('Convert File Format')
        label_title.setFont(QFont('Arial', 16))
        layout.addWidget(label_title, alignment=Qt.AlignCenter)
        
        # Input Files
        input_layout = QHBoxLayout()
        self.label_input_files = QLabel("Input Files:")
        input_layout.addWidget(self.label_input_files)
        self.input_files_entry = QLineEdit(self)
        input_layout.addWidget(self.input_files_entry)
        self.button_browse_input = QPushButton("Select Input Files", self)
        self.button_browse_input.clicked.connect(self.select_input_files)
        input_layout.addWidget(self.button_browse_input)
        layout.addLayout(input_layout)

        # Input Format
        input_format_layout = QHBoxLayout()
        self.label_input_format = QLabel("Input Format:")
        input_format_layout.addWidget(self.label_input_format)
        self.input_format_combo = QComboBox(self)
        self.input_format_combo.addItems(["genbank", "fasta", "embl", "phd", "seqxml", "tab"])
        input_format_layout.addWidget(self.input_format_combo)
        layout.addLayout(input_format_layout)

        # Output Directory
        output_layout = QHBoxLayout()
        self.label_output_dir = QLabel("Output Directory:")
        output_layout.addWidget(self.label_output_dir)
        self.output_directory_entry = QLineEdit(self)
        output_layout.addWidget(self.output_directory_entry)
        self.button_browse_output = QPushButton("Select Output Directory", self)
        self.button_browse_output.clicked.connect(self.select_output_directory)
        output_layout.addWidget(self.button_browse_output)
        layout.addLayout(output_layout)

        # Output Format
        format_layout = QHBoxLayout()
        self.label_output_format = QLabel("Output Format:")
        format_layout.addWidget(self.label_output_format)
        self.output_format_combo = QComboBox(self)
        self.output_format_combo.addItems(["fasta", "gff", "embl", "phd", "seqxml", "tab"])
        format_layout.addWidget(self.output_format_combo)
        layout.addLayout(format_layout)

        # Convert Button
        self.convert_button = QPushButton("Convert", self)
        self.convert_button.clicked.connect(self.convert_files)
        layout.addWidget(self.convert_button)

    def select_input_files(self):
        file_dialog = QFileDialog()
        file_paths, _ = file_dialog.getOpenFileNames(self, "Select Input Files")
        if file_paths:
            self.input_files_entry.setText(";".join(file_paths))

    def select_output_directory(self):
        dir_dialog = QFileDialog()
        dir_path = dir_dialog.getExistingDirectory(self, "Select Output Directory")
        if dir_path:
            self.output_directory_entry.setText(dir_path)

    def convert_files(self):
        input_files = self.input_files_entry.text().split(';')
        input_format = self.input_format_combo.currentText()
        output_directory = self.output_directory_entry.text()
        output_format = self.output_format_combo.currentText()

        if not input_files or not input_format or not output_directory or not output_format:
            QMessageBox.warning(self, "Warning", "Please fill in all fields.")
            return

        try:
            for input_file in input_files:
                self.convert_format(input_file, input_format, output_directory, output_format)
            QMessageBox.information(self, "Conversion Successful", f"Files converted successfully to {output_format} format.")
        except Exception as e:
            QMessageBox.critical(self, "Conversion Error", f"An error occurred during conversion: {str(e)}")

    def convert_format(self, input_file, input_format, output_directory, output_format):
        input_basename = os.path.basename(input_file)
        output_file = os.path.join(output_directory, os.path.splitext(input_basename)[0] + f".{output_format}")

        try:
            with open(output_file, 'w') as out:
                records = SeqIO.parse(input_file, input_format)
                SeqIO.write(records, out, output_format)
        except Exception as e:
            raise e

def main():
    app = QApplication(sys.argv)
    main_window = FileFormatConvertApp()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
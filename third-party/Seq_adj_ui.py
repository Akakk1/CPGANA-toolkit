"""
This code is built based on the following work
CPStools-seq_adj.py
Author: Xu wenbo
Org:    China Pharmaceutical University
Email:  xwb7533@163.com
site:   https://github.com/Xwb7533/CPStools
"""

import os
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QFileDialog, QVBoxLayout, QWidget, QMessageBox, QComboBox, QHBoxLayout)
from Bio import SeqIO
from Bio.Seq import Seq
import re

class SequenceAdjustApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Sequence Adjustment")
        self.setGeometry(100, 100, 600, 300)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        # Title label
        label_title = QLabel('Adjust the Direction of Chloroplast Genome')
        label_title.setFont(QFont('Arial', 16))
        layout.addWidget(label_title, alignment=Qt.AlignCenter)

        # Input Directory Widgets
        input_dir_layout = QHBoxLayout()
        self.label_input_dir = QLabel("Input Directory:")
        input_dir_layout.addWidget(self.label_input_dir)
        self.entry_input_dir = QLineEdit(self)
        input_dir_layout.addWidget(self.entry_input_dir)
        self.button_browse_input = QPushButton("Browse", self)
        self.button_browse_input.clicked.connect(self.browse_input_dir)
        input_dir_layout.addWidget(self.button_browse_input)
        layout.addLayout(input_dir_layout)

        # Output Directory Widgets
        output_dir_layout = QHBoxLayout()
        self.label_output_dir = QLabel("Output Directory:")
        output_dir_layout.addWidget(self.label_output_dir)
        self.entry_output_dir = QLineEdit(self)
        output_dir_layout.addWidget(self.entry_output_dir)
        self.button_browse_output = QPushButton("Browse", self)
        self.button_browse_output.clicked.connect(self.browse_output_dir)
        output_dir_layout.addWidget(self.button_browse_output)
        layout.addLayout(output_dir_layout)

        # Info File and Mode Widgets
        info_mode_layout = QHBoxLayout()
        self.label_info_file = QLabel("Info File:")
        info_mode_layout.addWidget(self.label_info_file)
        self.entry_info_file = QLineEdit(self)
        info_mode_layout.addWidget(self.entry_info_file)
        self.button_browse_info = QPushButton("Browse", self)
        self.button_browse_info.clicked.connect(self.browse_info_file)
        info_mode_layout.addWidget(self.button_browse_info)
        
        self.label_mode = QLabel("Mode:")
        info_mode_layout.addWidget(self.label_mode)
        self.mode_combo = QComboBox(self)
        self.mode_combo.addItems(['SSC', 'LSC'])
        info_mode_layout.addWidget(self.mode_combo)
        
        layout.addLayout(info_mode_layout)

        # Run Button
        self.run_button = QPushButton("Run", self)
        self.run_button.clicked.connect(self.run_operation)
        layout.addWidget(self.run_button)

    def browse_input_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Input Directory")
        if directory:
            self.entry_input_dir.setText(directory)

    def browse_output_dir(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.entry_output_dir.setText(directory)

    def browse_info_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Info File", "", "Text files (*.txt);;All files (*)")
        if file_path:
            self.entry_info_file.setText(file_path)

    def run_operation(self):
        work_dir = self.entry_input_dir.text()
        save_dir = self.entry_output_dir.text()
        info_file = self.entry_info_file.text()
        mode = self.mode_combo.currentText()

        if work_dir and save_dir and info_file:
            if mode == 'SSC':
                self.adjust_SSC_forward(work_dir, save_dir, info_file)
            elif mode == 'LSC':
                self.adjust_start_to_LSC(work_dir, save_dir, info_file)
        else:
            QMessageBox.warning(self, "Warning", "Please fill in all fields.")

    def adjust_SSC_forward(self, work_dir, save_dir, info_file):
        with open(info_file, 'r') as info_cont:
            for info_line in info_cont:
                # Split the line by tab to get all columns
                columns = info_line.strip().split('\t')

                # Extract relevant columns
                file_name = columns[0]
                SSC_start_end = columns[6]  # Column containing SSC start-end
                SSC_loc_start = int(SSC_start_end.split('-')[0])
                SSC_loc_end = int(SSC_start_end.split('-')[1])

                print(f"Processing file: {file_name}")

                work_file = os.path.join(work_dir, file_name)
                save_file = os.path.join(save_dir, file_name)

                if os.path.exists(work_file):
                    with open(save_file, 'w') as ff:
                        for rec in SeqIO.parse(work_file, 'fasta'):
                            SSC_seq = Seq(str(rec.seq[SSC_loc_start:SSC_loc_end])).reverse_complement()
                            rev_seq = str(rec.seq[:SSC_loc_start]) + str(SSC_seq) + str(rec.seq[SSC_loc_end:])
                            ff.write(f'>{rec.id}\n{rev_seq}\n')
                else:
                    abs_path = os.path.abspath(work_file)
                    print(f"No such file: {abs_path}")

        print("Done")

    def adjust_start_to_LSC(self, work_dir, save_dir, info_file):
        with open(info_file, 'r') as info_cont:
            for info_line in info_cont:
                # Split the line by tab to get all columns
                columns = info_line.strip().split('\t')

                # Extract relevant columns
                file_name = columns[0]
                LSC_start_end = columns[4]  # Column containing LSC start-end
                LSC_loc_start = int(LSC_start_end.split('-')[0])
                LSC_loc_end = int(LSC_start_end.split('-')[1])

                print(f"Processing file: {file_name}")

                work_file = os.path.join(work_dir, file_name)
                save_file = os.path.join(save_dir, file_name)

                if os.path.exists(work_file):
                    with open(save_file, 'w') as ff:
                        for rec in SeqIO.parse(work_file, 'fasta'):
                            if LSC_loc_start == 1:
                                ff.write(f'>{rec.id}\n{rec.seq}')
                            else:
                                adj_seq = str(rec.seq[LSC_loc_start - 1:]) + str(rec.seq[:LSC_loc_start - 1])
                                ff.write(f'>{rec.id}\n{adj_seq}\n')
                else:
                    abs_path = os.path.abspath(work_file)
                    print(f"No such file: {abs_path}")

        print("Done")


def main():
    app = QApplication(sys.argv)
    main_window = SequenceAdjustApp()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

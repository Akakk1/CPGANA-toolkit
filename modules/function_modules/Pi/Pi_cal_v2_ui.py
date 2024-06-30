"""
This code is built based on the following work
CPStools-Pi_2.py
Author: Xu wenbo
Org:    China Pharmaceutical University
Email:  xwb7533@163.com
site:   https://github.com/Xwb7533/CPStools
"""

import os
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QComboBox
from Bio import SeqIO


class PiCalculateApp_V2(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Pi Calculator - IGS/Gene')
        self.setGeometry(100, 100, 600, 200)

        self.input_label = QLabel('Input Directory:')
        self.input_edit = QLineEdit()
        self.input_button = QPushButton('Browse...')
        self.input_button.clicked.connect(self.browse_input)

        self.output_label = QLabel('Output Directory:')
        self.output_edit = QLineEdit()
        self.output_button = QPushButton('Browse...')
        self.output_button.clicked.connect(self.browse_output)

        self.reference_label = QLabel('Reference File:')
        self.reference_edit = QLineEdit()
        self.reference_button = QPushButton('Browse...')
        self.reference_button.clicked.connect(self.browse_reference)

        self.mode_label = QLabel('Mode:')
        self.mode_combobox = QComboBox()
        self.mode_combobox.addItem('gene')
        self.mode_combobox.addItem('IGS')

        self.run_button = QPushButton('Run')
        self.run_button.clicked.connect(self.run_analysis)

        vbox = QVBoxLayout()
        # Title label
        label_title = QLabel('Calculate Pi by IGS/Gene')
        label_title.setFont(QFont('Arial', 16))
        
        vbox.addWidget(label_title, alignment=Qt.AlignCenter) 
        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.input_label)
        hbox1.addWidget(self.input_edit)
        hbox1.addWidget(self.input_button)
        vbox.addLayout(hbox1)
        
        hbox_output = QHBoxLayout()
        hbox_output.addWidget(self.output_label)
        hbox_output.addWidget(self.output_edit)
        hbox_output.addWidget(self.output_button)
        vbox.addLayout(hbox_output)

        hbox_ref = QHBoxLayout()
        hbox_ref.addWidget(self.reference_label)
        hbox_ref.addWidget(self.reference_edit)
        hbox_ref.addWidget(self.reference_button)
        vbox.addLayout(hbox_ref)

        hbox_mode = QHBoxLayout()
        hbox_mode.addWidget(self.mode_label)
        hbox_mode.addWidget(self.mode_combobox)
        vbox.addLayout(hbox_mode)

        vbox.addWidget(self.run_button)
        self.setLayout(vbox)

    def browse_input(self):
        dir_path = QFileDialog.getExistingDirectory(self, 'Select Input Directory')
        if dir_path:
            self.input_edit.setText(dir_path)

    def browse_output(self):
        dir_path = QFileDialog.getExistingDirectory(self, 'Select Output Directory')
        if dir_path:
            self.output_edit.setText(dir_path)

    def browse_reference(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select Reference File')
        if file_path:
            self.reference_edit.setText(file_path)

    def run_analysis(self):
        input_dir = self.input_edit.text().strip()
        output_dir = self.output_edit.text().strip()
        reference_file = self.reference_edit.text().strip()
        mode = self.mode_combobox.currentText()

        if not os.path.isdir(input_dir):
            QMessageBox.critical(self, 'Error', f"The specified input directory '{input_dir}' does not exist.")
            return

        if not os.path.isdir(output_dir):
            QMessageBox.critical(self, 'Error', f"The specified output directory '{output_dir}' does not exist.")
            return

        if not os.path.isfile(reference_file):
            QMessageBox.critical(self, 'Error', f"The specified reference file '{reference_file}' does not exist.")
            return

        pi_results_path = calculate_Pi_values(input_dir)
        output_file = os.path.join(output_dir, f"{mode}_sort_as_cp_order.txt")
        sort_as_cp_order(pi_results_path, reference_file, output_file)

        QMessageBox.information(self, 'Process Complete',
                                f"The sorted results have been written into:\n{os.path.abspath(output_file)}")


def calculate_Pi_values(work_dir):
    if not work_dir.endswith('/'):
        work_dir += '/'
    all_pi_results = []
    for align_fasta in os.listdir(work_dir):
        if align_fasta.endswith('.fasta'):
            pi = calculate_pi_for_file(os.path.join(work_dir, align_fasta))
            all_pi_results.append(f"{align_fasta[:-6]}\t{pi}")
            print(f"{align_fasta[:-6]}\t{pi}")

    pi_results_file = os.path.join(work_dir, 'Pi_results.txt')
    with open(pi_results_file, 'w') as ff:
        for each_pi in all_pi_results:
            ff.write(f"{each_pi}\n")

    return pi_results_file


def calculate_pi_for_file(fasta_file):
    sequences = []
    gaps_positions = set()

    for rec in SeqIO.parse(fasta_file, format='fasta'):
        sequences.append(rec)
        gaps_positions.update(i for i, base in enumerate(rec.seq) if base == '-')

    all_number = len(sequences) * (len(sequences) - 1) / 2
    filtered_sequences = filter_out_gaps(sequences, gaps_positions)
    
    if not filtered_sequences:
        return format(0.0, '.5f')

    pi_value = calculate_pi(filtered_sequences, all_number)

    return format(pi_value, '.5f')


def filter_out_gaps(sequences, gaps_positions):
    filtered_sequences = []
    for seq in sequences:
        filtered_seq = ''.join(base for i, base in enumerate(seq.seq) if i not in gaps_positions)
        filtered_sequences.append(filtered_seq)
    return filtered_sequences


def calculate_pi(sequences, all_number):
    pi = 0
    num_sequences = len(sequences)
    
    if not sequences or not sequences[0]:
        return 0.0

    for i in range(len(sequences[0])):
        column = [seq[i] for seq in sequences]
        diff = sum(1 for j in range(num_sequences) for k in range(j + 1, num_sequences) if column[j] != column[k])
        pi += diff / all_number
    return pi / len(sequences[0])


def sort_as_cp_order(input_file1, input_file2, output_file):
    with open(input_file1, 'r') as pi_results, open(input_file2, 'r') as cp_order_results, open(output_file, 'w') as results_file:
        file1_line_list = pi_results.readlines()
        file2_line_list = cp_order_results.readlines()

        for cp_order_line in file2_line_list:
            cp_order_name = cp_order_line.strip()
            for pi_line in file1_line_list:
                if pi_line.split('\t')[0] == cp_order_name:
                    print(pi_line, end='', file=results_file)
                    break


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PiCalculateApp_V2()
    window.show()
    sys.exit(app.exec_())

"""
This code is built based on the following work
compute_pi_use_aln_fasta_v1.1.pl
Author: Xu lei
site:   https://blog.csdn.net/weixin_43362619/article/details/107239012?spm=1001.2014.3001.5502
"""

import sys
import os
import time
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QLineEdit, QPushButton, QTextEdit, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox
class PiCalculateApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Pi Calculator - Window')
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Widgets
        self.infile_label = QLabel('Input File:')
        self.infile_input = QLineEdit()
        self.browse_button = QPushButton('Browse')
        self.window_label = QLabel('Window Size:')
        self.window_input = QLineEdit()
        self.step_label = QLabel('Step Size:')
        self.step_input = QLineEdit()
        self.output_label = QLabel('Output Directory:')
        self.output_input = QLineEdit()
        self.browse_output_button = QPushButton('Browse')
        self.run_button = QPushButton('Run')
        self.output_text = QTextEdit()

        # Layouts
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        # Title label
        label_title = QLabel('Calculate Pi by Window')
        label_title.setFont(QFont('Arial', 16))
        main_layout.addWidget(label_title, alignment=Qt.AlignCenter) 

        # File Selection Row
        file_layout = QHBoxLayout()
        file_layout.addWidget(self.infile_label)
        file_layout.addWidget(self.infile_input)
        file_layout.addWidget(self.browse_button)
        main_layout.addLayout(file_layout)

        # Window and Step Size Row
        size_layout = QHBoxLayout()
        size_layout.addWidget(self.window_label)
        size_layout.addWidget(self.window_input)
        size_layout.addWidget(self.step_label)
        size_layout.addWidget(self.step_input)
        main_layout.addLayout(size_layout)

        # Output Directory Row
        output_layout = QHBoxLayout()
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_input)
        output_layout.addWidget(self.browse_output_button)
        main_layout.addLayout(output_layout)

        # Run Button
        main_layout.addWidget(self.run_button)

        # Output Text Area
        main_layout.addWidget(self.output_text)

        # Connections
        self.browse_button.clicked.connect(self.browse_files)
        self.browse_output_button.clicked.connect(self.browse_output_directory)
        self.run_button.clicked.connect(self.run_calculation)

    def browse_files(self):
        options = QFileDialog.Options()
        file, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "", "All Files (*);;Fasta Files (*.fasta)", options=options)
        if file:
            self.infile_input.setText(file)

    def browse_output_directory(self):
        options = QFileDialog.Options()
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory", options=options)
        if directory:
            self.output_input.setText(directory)

    def run_calculation(self):
        infile = self.infile_input.text()
        window = int(self.window_input.text()) if self.window_input.text() else 0
        step = int(self.step_input.text()) if self.step_input.text() else 0
        output_dir = self.output_input.text()

        if not os.path.isfile(infile):
            self.output_text.append("Input file does not exist!")
            return

        if not os.path.isdir(output_dir):
            self.output_text.append("Output directory does not exist!")
            return

        start_time = time.time()
        all_seq = get_aln_seq(infile)
        window = window if window > 0 else len(all_seq[0])
        step = step if step > 0 else len(all_seq[0])

        if window > len(all_seq[0]):
            self.output_text.append("Warning: window must be less than alignment sequence length")
            return

        conserved_site, for_old_pos = get_conserved_site(all_seq)
        conserved_len = len(conserved_site[0])

        if window > conserved_len:
            window = conserved_len
        if step > conserved_len:
            step = conserved_len
        if window < step:
            self.output_text.append("Warning: window must be larger than step")
            return
        else:
            all_pi_info = computer_pi_with_bin(conserved_site, conserved_len, conserved_len, for_old_pos)
            all_pi, all_S = map(float, all_pi_info[0].split()[2:4])

            self.output_text.append(f"#infile: {os.path.abspath(infile)}")
            self.output_text.append(f"#seq number: {len(all_seq)}")
            self.output_text.append(f"#aln length: {len(all_seq[0])}")
            self.output_text.append(f"#conserved length: {conserved_len}")
            self.output_text.append(f"#window length: {window}")
            self.output_text.append(f"#step size: {step}")
            self.output_text.append(f"#Nucleotide diversity, Pi: {all_pi}")
            self.output_text.append(f"#Number of polymorphic (segregating) sites, S: {all_S}")
            self.output_text.append("=" * 35)

            pi_info = computer_pi_with_bin(conserved_site, window, step, for_old_pos)
            self.output_text.append("Start\tEnd\tMidpoint\tPi\tS")
            output_lines = ["Start\tEnd\tMidpoint\tPi\tS"]
            for line in pi_info:
                parts = line.split()
                start_end = parts[0].split('-')
                start, end = start_end[0], start_end[1]
                midpoint, pi, s = parts[1], parts[2], parts[3]
                self.output_text.append(f"{start}\t{end}\t{midpoint}\t{pi}\t{s}")
                output_lines.append(f"{start}\t{end}\t{midpoint}\t{pi}\t{s}")

            with open(os.path.join(output_dir, 'pi_results.txt'), 'w') as f:
                f.write('\n'.join(output_lines))

            self.output_text.append("=" * 35)
            self.output_text.append(f"Done. Total elapsed time: {time.time() - start_time:.2f}s")

def get_aln_seq(infile):
    with open(infile, 'r') as f:
        data = f.read().split('>')[1:]
        all_seq = []
        for entry in data:
            lines = entry.split('\n')
            seq = ''.join(lines[1:]).replace('\n', '').replace(' ', '').upper()
            seq = seq.replace('N', '-')
            all_seq.append(list(seq))
    return all_seq

def compute_diff_site(sites):
    s = 0
    for i in range(len(sites) - 1):
        for j in range(i + 1, len(sites)):
            if sites[i] != sites[j]:
                s += 1
    return s

def get_conserved_site(all_seq):
    sample_nu = len(all_seq)
    conserved_site = []
    for_old_pos = {}
    i2 = 0

    for i in range(len(all_seq[0])):
        indel_flag = 0
        for j in range(sample_nu):
            if all_seq[j][i] not in "ATGC-":
                raise ValueError(f"Some site is not ATGC in conserved site: {all_seq[j][i]}")
            if all_seq[j][i] == '-':
                indel_flag = 1

        if indel_flag == 0:
            for k in range(sample_nu):
                if len(conserved_site) <= k:
                    conserved_site.append([])
                conserved_site[k].append(all_seq[k][i])
            for_old_pos[i2] = i
        else:
            for_old_pos[i2] = i
            i2 -= 1
        i2 += 1
    return conserved_site, for_old_pos

def get_conserved_sites_pi(all_seq):
    sample_nu = len(all_seq)
    sum_diff_sites = 0
    len_seq = len(all_seq[0])
    nu_mutations = 0

    if sample_nu <= 1:
        raise ValueError("Sample number is less than 2")

    for i in range(len_seq):
        sites = [all_seq[j][i] for j in range(sample_nu)]
        diff_sites = compute_diff_site(sites)
        sum_diff_sites += diff_sites
        if diff_sites:
            nu_mutations += 1

    di = sample_nu * (sample_nu - 1) / 2
    pi = sum_diff_sites / di / len_seq
    return pi, nu_mutations

def computer_pi_with_bin(all_seq, window, step, for_old_pos):
    len_seq = len(all_seq[0])
    loop = int((len_seq - window) / step)
    info = []

    for d in range(loop + 1):
        bin_site = [[all_seq[i][d * step + j] for j in range(window)] for i in range(len(all_seq))]
        start_new = d * step + 1
        end_new = start_new + window - 1
        mid_new = (end_new + start_new) // 2
        mid = for_old_pos[mid_new - 1] + 1

        pi, nu_mutations = get_conserved_sites_pi(bin_site)
        info.append(f"{start_new}-{end_new}\t{mid}\t{pi:.5f}\t{nu_mutations}")

    return info

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PiCalculateApp()
    window.show()
    sys.exit(app.exec_())

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
import re
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit, QFileDialog, QMessageBox, QLineEdit, QGridLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqUtils import GC

class RepeatFinderGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Region Find")
        self.setGeometry(100, 100, 600, 300)
        self.create_widgets()
        
    def create_widgets(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Title label
        label_title = QLabel('Find Regions of Chloroplast Genome')
        label_title.setFont(QFont('Arial', 16))
        layout.addWidget(label_title, alignment=Qt.AlignCenter)  

        input_frame = QWidget()
        input_layout = QGridLayout(input_frame)
        input_frame.setLayout(input_layout)
        
        layout.addWidget(input_frame)

        # Input file selection
        input_label = QLabel("Select Input Files:")
        self.input_file_entries = QTextEdit()
        browse_input_button = QPushButton("Browse")
        browse_input_button.clicked.connect(self.browse_files)

        input_layout.addWidget(input_label, 0, 0, 1, 1)
        input_layout.addWidget(self.input_file_entries, 1, 0, 1, 2)
        input_layout.addWidget(browse_input_button, 1, 2, 1, 1)

        # Output directory selection
        output_frame = QWidget()
        output_layout = QGridLayout(output_frame)
        output_frame.setLayout(output_layout)

        layout.addWidget(output_frame)

        output_label = QLabel("Select Output Directory:")
        self.output_dir_entry = QLineEdit()
        browse_output_button = QPushButton("Select Directory")
        browse_output_button.clicked.connect(self.browse_output_directory)

        output_layout.addWidget(output_label, 0, 0, 1, 1)
        output_layout.addWidget(self.output_dir_entry, 1, 0, 1, 2)
        output_layout.addWidget(browse_output_button, 1, 2, 1, 1)

        # Run button
        run_button = QPushButton("Run Analysis")
        run_button.clicked.connect(self.run_analysis)
        layout.addWidget(run_button)

    def browse_files(self):
        options = QFileDialog.Options()
        filenames, _ = QFileDialog.getOpenFileNames(self, "Select Files", "", "Fasta files (*.fasta *.fa);;GenBank files (*.gb *.gbk)", options=options)
        if filenames:
            self.input_file_entries.clear()
            self.input_file_entries.append("\n".join(filenames))

    def browse_output_directory(self):
        options = QFileDialog.Options()
        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory", options=options)
        if output_dir:
            self.output_dir_entry.setText(output_dir)

    def run_analysis(self):
        output_dir = self.output_dir_entry.text().strip()
        if not output_dir:
            QMessageBox.critical(self, "Error", "Please select an output directory.")
            return

        input_files = self.input_file_entries.toPlainText().splitlines()
        if not input_files:
            QMessageBox.critical(self, "Error", "Please select input files.")
            return

        results = []
        for input_file in input_files:
            input_file = input_file.strip()
            if input_file:
                try:
                    seq = self.check_files(input_file)
                    output_text, region_seqs = self.find_repeat_regions(seq, input_file)
                    results.append(f"{os.path.basename(input_file)}\t{output_text}\n")
                    self.save_regions_to_fasta(region_seqs, input_file, output_dir)
                except (ValueError, FileNotFoundError) as e:
                    results.append(f"Error processing {os.path.basename(input_file)}: {str(e)}\n")

        self.save_results_to_file(results, output_dir)

    def save_results_to_file(self, results, output_dir):
        filename = os.path.join(output_dir, "repeat_analysis_results.txt")
        try:
            with open(filename, 'w') as f:
                f.writelines(results)
            QMessageBox.information(self, "File Saved", f"Results saved successfully to {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save results: {str(e)}")
            
    def save_regions_to_fasta(self, region_seqs, input_file, output_dir):
        species_name = os.path.splitext(os.path.basename(input_file))[0]
        for region, seq in region_seqs.items():
            filename = os.path.join(output_dir, f"{species_name}_{region}.fasta")
            try:
                with open(filename, 'w') as f:
                    f.write(f">{species_name}_{region}\n{seq}\n")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save fasta file: {str(e)}")
                
    @staticmethod
    def check_files(input_file):
        try:
            if input_file.endswith(('.fasta', '.fa')):
                format = 'fasta'
            elif input_file.endswith(('.gb', '.gbk')):
                format = 'genbank'
            else:
                raise ValueError(f"Unsupported file format for '{input_file}'. Please use FASTA (.fasta or .fa) or GenBank (.gb or .gbk) files.")

            for rec in SeqIO.parse(input_file, format):
                if not re.fullmatch(r'[ATCG]*', str(rec.seq)):
                    raise ValueError("Sequence contains bases other than A, T, C, G.")
                return str(rec.seq)
        except FileNotFoundError:
            raise FileNotFoundError(f"No such file: {input_file}")
        except Exception as e:
            raise ValueError(f"Error processing file '{input_file}': {e}")

    @staticmethod
    def find_repeat_regions(sequence,input_file):
        replace_dict = {"A": "T", "C": "G", "T": "A", "G": "C", "a": "t", "c": "g", "t": "a", "g": "c"}
        sequence = sequence.lower()
        rev_seq = str(Seq(sequence).reverse_complement())

        all_list = []
        for i in range(0, len(sequence), 500):
            if i + 500 <= len(sequence):
                test_seq = sequence[i:i + 500]
                if test_seq in rev_seq:
                    all_list.append([i, i + 500])

        if not all_list:
            return "No repeated sequences longer than 1,000 bp were detected!"

        merged_sublists = []
        start, end = all_list[0]

        for sublist in all_list[1:]:
            sublist_start, sublist_end = sublist
            if sublist_start == end:
                end = sublist_end
            else:
                merged_sublists.append([start, end])
                start, end = sublist_start, sublist_end

        merged_sublists.append([start, end])
        longest_sublist = max(merged_sublists, key=lambda x: x[1] - x[0])
        start_pos, end_pos = longest_sublist
        max_seq = str(Seq(sequence[start_pos:end_pos]).reverse_complement())
        start_loc = sequence.find(max_seq)

        if start_loc == -1:
            return "The assembled sequence may be wrong!"

        seq_end = start_loc + len(max_seq)
        sorted_list = sorted([[start_loc, seq_end], [start_pos, end_pos]])
        start1, end1, start2, end2 = sorted_list[0][0], sorted_list[0][1], sorted_list[1][0], sorted_list[1][1]

        while sequence[end1 - 1] == replace_dict[sequence[start2]]:
            end1 += 1
            start2 -= 1

        if start1 != 0:
            if end2 != len(sequence):
                if sequence[start1 - 1] == replace_dict[sequence[end2]]:
                    new_start, new_end = start1 - 1, end2
                    while new_end < len(sequence) and sequence[new_start] == replace_dict[sequence[new_end]]:
                        new_start -= 1
                        new_end += 1

                    if new_end == len(sequence):
                        if sequence[new_start] == replace_dict[sequence[0]]:
                            new_end = 1
                            new_start -= 1
                            while sequence[new_start] == replace_dict[sequence[new_end]]:
                                new_start -= 1
                                new_end += 1

                            if (start2 - end1) <= (new_start - new_end):
                                result = (
                                    f"LSC:{new_end + 1}-{new_start + 1}\tIRb:{new_start + 2}-{end1 - 1}\t"
                                    f"SSC:{end1}-{start2 + 1}\tIRa:{start2 + 2}-{len(sequence)},1-{new_end}"
                                )
                            else:
                                result = (
                                    f"LSC:{end1}-{start2 + 1}\tIRb:{start2 + 2}-{len(sequence)},1-{new_end}\t"
                                    f"SSC:{new_end + 1}-{new_start + 1}\tIRa:{start1 + 2}-{end1 - 1}"
                                )
                        else:
                            if (start2 - end1) <= new_start:
                                result = (
                                    f"LSC:{1}-{new_start + 1}\tIRb:{new_start + 2}-{end1 - 1}\t"
                                    f"SSC:{end1}-{start2 + 1}\tIRa:{start2 + 2}-{new_end}"
                                )
                            else:
                                result = (
                                    f"LSC:{end1}-{start2 + 1}\tIRb:{start2 + 2}-{new_end}\tSSC:1-{new_start + 1}\tIRa:{new_start + 2}-{end1 - 1}"
                                )
                    else:
                        if (start2 - end1) <= (len(sequence) - new_end + new_start):
                            result = (
                                f"LSC:{new_end + 1}-{len(sequence)},1-{new_start + 1}\tIRb:{new_start + 2}-{end1 - 1}\t"
                                f"SSC:{end1}-{start2 + 1}\tIRa:{start2 + 2}-{new_end}"
                            )
                        else:
                            result = (
                                f"LSC:{end1}-{start2 + 1}\tIRb:{start2 + 2}-{new_end}\tSSC:{new_end + 1}-{len(sequence)},1-{new_start + 1}\t"
                                f"IRa:{new_start + 2}-{end1 - 1}"
                            )
                else:
                    result = (
                        f"LSC:{end1}-{start2 + 1}\tIRb:{start2 + 2}-{len(sequence)}\tSSC:{1}-{new_start + 1}\t"
                        f"IRa:{new_start + 2}-{end1 - 1}"
                    )
            else:
                result = (
                    f"LSC:{1}-{new_start + 1}\tIRb:{new_start + 2}-{end1 - 1}\tSSC:{end1}-{start2 + 1}\t"
                    f"IRa:{start2 + 2}-{new_end}"
                )
        else:
            result = (
                f"LSC:{end1}-{start2 + 1}\tIRb:{start2 + 2}-{len(sequence)},1-{new_start + 1}\tSSC:{new_start + 2}-{end1 - 1}"
            )

        pattern = r"\d+"

        matches = re.findall(pattern, result)

        LSC_start = int(matches[0])
        LSC_end = int(matches[1])
        IRb_start = int(matches[2])
        IRb_end = int(matches[3])
        SSC_start = int(matches[4])
        SSC_end = int(matches[5])
        IRa_start = int(matches[6])
        IRa_end = int(matches[7])

        LSC_seq = sequence[LSC_start-1:LSC_end]
        IRb_seq = sequence[IRb_start-1:IRb_end]
        SSC_seq = sequence[SSC_start-1:SSC_end]
        IRa_seq = sequence[IRa_start-1:IRa_end]

        region_seqs = {
            "LSC": LSC_seq,
            "IRb": IRb_seq,
            "SSC": SSC_seq,
            "IRa": IRa_seq
        }

        # Calculate GC content
        total_gc = GC(sequence)
        lsc_gc = GC(LSC_seq)
        ir_gc = GC(IRb_seq)  # IRb and IRa are considered the same for GC content
        ssc_gc = GC(SSC_seq)

        species_name = os.path.splitext(os.path.basename(input_file))[0]

        output_text = (
            f"{len(LSC_seq)}\t{len(IRb_seq)}\t{len(SSC_seq)}\t"
            f"{LSC_start}-{LSC_end}\t{IRb_start}-{IRb_end}\t{SSC_start}-{SSC_end}\t{IRa_start}-{len(sequence)}\t"
            f"{total_gc:.2f}\t{lsc_gc:.2f}\t{ir_gc:.2f}\t{ssc_gc:.2f}"
        )

        if len(IRb_seq) != len(IRa_seq):
            output_text += "\tIRa and IRb are not equal in length"

        return output_text, region_seqs        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = RepeatFinderGUI()
    main_window.show()
    sys.exit(app.exec_())

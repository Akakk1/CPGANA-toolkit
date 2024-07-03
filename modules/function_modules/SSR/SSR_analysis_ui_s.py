"""
This code is built based on the following work
CPStools-SSR_analysis.py
Author: Xu wenbo
Org:    China Pharmaceutical University
Email:  xwb7533@163.com
site:   https://github.com/Xwb7533/CPStools
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton,
    QHBoxLayout, QLineEdit, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from Bio import SeqIO
import os
import re

class SSRFindApp(QWidget):
    def __init__(self):
        super().__init__()
        self.type_lengths = [10, 5, 4, 3, 3, 3]  # Default SSR lengths
        self.initUI()
        self.input_files = []
    def initUI(self):
        self.setWindowTitle("SSR Finder")

        layout = QVBoxLayout()
        
        # Title label
        label_title = QLabel('Find SSR')
        label_title.setFont(QFont('Arial', 16))
        layout.addWidget(label_title, alignment=Qt.AlignCenter)  
        
        # Input file selection
        frame_input = QVBoxLayout()
        
        label_input = QLabel("Input Files:")
        frame_input.addWidget(label_input)
        
        self.listbox_files = QListWidget()
        frame_input.addWidget(self.listbox_files)

        button_layout = QHBoxLayout()
        button_add = QPushButton("Add Files")
        button_add.clicked.connect(self.add_files)
        button_layout.addWidget(button_add)

        button_remove = QPushButton("Remove Selected")
        button_remove.clicked.connect(self.remove_file)
        button_layout.addWidget(button_remove)

        button_clear = QPushButton("Clear All")
        button_clear.clicked.connect(self.clear_files)
        button_layout.addWidget(button_clear)

        frame_input.addLayout(button_layout)
        layout.addLayout(frame_input)

        # Output directory selection
        frame_output = QHBoxLayout()
        label_output = QLabel("Output Directory:")
        frame_output.addWidget(label_output)

        self.entry_output = QLineEdit()
        frame_output.addWidget(self.entry_output)

        button_output = QPushButton("Select Output")
        button_output.clicked.connect(self.select_output_directory)
        frame_output.addWidget(button_output)

        layout.addLayout(frame_output)

        # SSR length inputs
        frame_length = QHBoxLayout()
        labels = ["Mononucleotide:", "Dinucleotide:", "Trinucleotide:", "Tetranucleotide:", "Pentanucleotide:", "Hexanucleotide:"]
        self.entry_lengths = []

        for i, label_text in enumerate(labels):
            label_length = QLabel(label_text)
            frame_length.addWidget(label_length)
            entry_length = QLineEdit()
            entry_length.setText(str(self.type_lengths[i]))
            self.entry_lengths.append(entry_length)
            frame_length.addWidget(entry_length)

        layout.addLayout(frame_length)

        # Buttons
        frame_buttons = QHBoxLayout()
        button_run = QPushButton("Run SSR Finder")
        button_run.clicked.connect(self.run_ssr_finder)
        frame_buttons.addWidget(button_run)
        
        button_quit = QPushButton("Quit")
        button_quit.clicked.connect(self.close)
        frame_buttons.addWidget(button_quit)

        layout.addLayout(frame_buttons)

        self.setLayout(layout)

    def add_files(self):
        filenames, _ = QFileDialog.getOpenFileNames(self, "Select Files", "", "GenBank Files (*.gb *.gbk);;All Files (*)")
        if filenames:
            for filename in filenames:
                self.input_files.append(filename)
                self.listbox_files.addItem(filename)

    def remove_file(self):
        selected_items = self.listbox_files.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            self.input_files.remove(item.text())
            self.listbox_files.takeItem(self.listbox_files.row(item))

    def clear_files(self):
        self.listbox_files.clear()
        self.input_files.clear()

    def select_output_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.entry_output.setText(directory)

    def run_ssr_finder(self):
        output_directory = self.entry_output.text()

        if not self.input_files:
            QMessageBox.critical(self, "Error", "Please select input files.")
            return

        try:
            # Retrieve SSR lengths from input fields
            self.type_lengths = [int(entry.text()) for entry in self.entry_lengths]

            for input_file in self.input_files:
                file_path = os.path.abspath(input_file)
                check_results = self.check_files(file_path)

                if check_results:
                    self.find_SSRs(file_path, *self.type_lengths)
                    self.IGS_extract(file_path)

            QMessageBox.information(self, "Success", "Batch SSRs extraction completed successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error running SSR Finder: {str(e)}")

    def check_files(self, input_file):
        try:
            if input_file.endswith('.fasta') or input_file.endswith('.fa'):
                for rec in SeqIO.parse(input_file, 'fasta'):
                    print("Please input Genbank format file")
            if input_file.endswith('.gb') or input_file.endswith('.gbk'):
                for rec in SeqIO.parse(input_file, 'genbank'):
                    return str(rec.seq)
            raise ValueError(f"Unsupported file format for '{input_file}'. "
                             f"Please use FASTA (.fasta or .fa) or GenBank (.gb or .gbk) files.")
        except Exception as e:
            if isinstance(e, FileNotFoundError):
                raise  # Reraise the FileNotFoundError
            elif os.path.exists(input_file):
                raise ValueError(f"Error processing file '{input_file}': {e}")
            else:
                raise FileNotFoundError(f"No such file: {input_file}")

    def find_SSRs(self, input_file, *length):
        type_length = []
        if len(length) == 0:
            type_length = [10, 5, 4, 3, 3, 3]
        elif len(length) == 6:
            type_length = length
        else:
            print("Please input type length equal 6 or 0")
            return []
        k1, k2, k3, k4, k5, k6 = type_length

        print(f"The parameter is set as:\n"
              f"Mononucleotide:{k1}\n"
              f"Dinucleotide:{k2}\n"
              f"Trinucleotide:{k3}\n"
              f"Tetranucleotide:{k4}\n"
              f"Pentanucleotide:{k5}\n"
              f"Hexanucleotide:{k6}\n")
        my_seq = self.check_files(input_file)
        matches = {
            'match1': re.finditer(r'([ATCG])\1{{{0},}}'.format(k1 - 1), my_seq),
            'match2': re.finditer(r'(((?!AA|TT|CC|GG)[ATCG]){{2}})\1{{{0},}}'.format(k2 - 1), my_seq),
            'match3': re.finditer(r'(((?!AAA|TTT|CCC|GGG)[ATCG]){{3}})\1{{{0},}}'.format(k3 - 1), my_seq),
            'match4': re.finditer(r'(?!(\w)(\w)\1\2)(((?!AAAA|TTTT|CCCC|GGGG)[ATCG]){{4}})\3{{{0},}}'.format(k4 - 1),
                                  my_seq),
            'match5': re.finditer(r'(((?!AAAAA|TTTTT|CCCCC|GGGGG)[ATCG]){{5}})\1{{{0},}}'.format(k5 - 1), my_seq),
            'match6': re.finditer(
                r'(?!(\w)(\w)(\w)\1\2\3)(((?!AAAAAA|TTTTTT|CCCCCC|GGGGGG)[ATCG]){{6}})\4{{{0},}}'.format(k6 - 1), my_seq)
        }
        all_matches = []
        for index_ in range(1, 7):
            group_name = 'match' + str(index_)
            for m in matches[group_name]:
                start = m.start() + 1
                if not any(start == int(match.split('\t')[2]) for match in all_matches):
                    character = m.group()[:index_]
                    length = len(m.group()) // index_
                    end = m.end()
                    output = f"{character}\t{length}\t{start}\t{end}"

                    all_matches.append(output)

        all_matches_sorted = sorted(all_matches, key=lambda x: int(x.split('\t')[2]))
        file_name = os.path.basename(input_file).split('.')[0]
        save_name = file_name + "."
        output_directory = self.entry_output.text()       
        file_save = os.path.join(output_directory, save_name)
        with open(file_save, 'w') as ff:
            ff.write("type\tlength\tstart\tend\n")
            for SSRs_ in all_matches_sorted:
                ff.write(f"{SSRs_}\n")
        print(f"results:\ttotal {len(all_matches)} SSRs were detected!\n{'-' * 80}")

    def IGS_extract(self, input_file):
        for rec in SeqIO.parse(input_file, format='genbank'):
            genome_length = [[int(part.end)] for part in rec.features[0].location.parts][0][0]
            my_seq = rec.seq
            all_feature = []
            all_info = []
            for feature in rec.features:
                if feature.type == 'CDS' or feature.type == 'tRNA' or feature.type == 'rRNA':
                    all_feature.append(feature)
            for i in range(len(all_feature)):
                gene_name = all_feature[i].qualifiers['gene'][0]
                gene_location = all_feature[i].location.parts
                gene1_exon_info = [[int(part.start), int(part.end), part.strand] for part in gene_location]
                exon_number = len(gene_location)
                if exon_number == 1:
                    all_info.append(f"{gene_name}\t{gene1_exon_info[0][0]}\t{gene1_exon_info[0][1]}\t{gene1_exon_info[0][2]}")
                    all_info.append(f"{gene_name}\t{gene1_exon_info[0][0]}\t{gene1_exon_info[0][1]}\t{gene1_exon_info[0][2]}")
                if exon_number == 2:
                    if gene1_exon_info[0][1] == genome_length:
                        all_info.append(f"{gene_name}\t{gene1_exon_info[0][0]}\t{gene1_exon_info[0][1]}\t{gene1_exon_info[1][0]}\t{gene1_exon_info[1][1]}\t{gene1_exon_info[0][2]}")
                    else:
                        all_info.append(f"{gene_name}_1\t{gene1_exon_info[0][0]}\t{gene1_exon_info[0][1]}\t{gene1_exon_info[0][2]}")
                        all_info.append(f"{gene_name}_2\t{gene1_exon_info[1][0]}\t{gene1_exon_info[1][1]}\t{gene1_exon_info[1][2]}")
                if exon_number == 3:
                    all_info.append(f"{gene_name}_1\t{gene1_exon_info[0][0]}\t{gene1_exon_info[0][1]}\t{gene1_exon_info[0][2]}")
                    all_info.append(f"{gene_name}_2\t{gene1_exon_info[1][0]}\t{gene1_exon_info[1][1]}\t{gene1_exon_info[1][2]}")
                    all_info.append(f"{gene_name}_3\t{gene1_exon_info[2][0]}\t{gene1_exon_info[2][1]}\t{gene1_exon_info[2][2]}")
            all_info = list(set(all_info))
            all_info.sort(key=lambda x: int(x.split('\t')[1]))
            save_file = os.path.join(os.path.dirname(input_file), os.path.basename(input_file).split('.')[0] + '_SSRs.txt')
            save_file_w = open(save_file, 'w')
            for i in range(len(all_info)-1):
                info_list = all_info[i].split('\t')
                next_list = all_info[i+1].split('\t')
                save_file_w.write(f"{info_list[0]}\t{info_list[1]}\t{info_list[2]}\tGene\n")
                save_file_w.write(f"{info_list[0]}-{next_list[0]}\t{info_list[-2]}\t{next_list[1]}\tIGS\n")
            save_file_w.write(f"{all_info[-1][:-1]}\tGene\n")
            end_gene_info = all_info[-1].split('\t')
            start_gene_info = all_info[0].split('\t')
            if int(end_gene_info[-2]) < int(start_gene_info[1]):
                save_file_w.write(f"{end_gene_info[0]}-{start_gene_info}[0]\t{end_gene_info[-2]}\t{start_gene_info[1]}"
                                  f"\tGene\n")
            else:
                if int(end_gene_info[2]) < genome_length:
                    save_file_w.write(f"{end_gene_info[0]}-{start_gene_info[0]}\t{end_gene_info[-2]}\t{genome_length}\t0\t\
                    {start_gene_info[1]}\tIGS\n")
                else:
                    pass
            save_file_w.close()

            # change location type 
            output_ = os.path.join(os.path.dirname(input_file), os.path.basename(input_file).split('.')[0] + '_SSRs2.txt')
            change_file = open(save_file, 'r').readlines()
            with open(output_, 'w') as gg:
                for loc2 in change_file:
                    loc_type = loc2.split('\t')[0]
                    if "matK" in loc_type and "trnK-UUU" in loc_type:
                        loc2_list = loc2.split('\t')
                        loc2_list[-1] = "Intron"
                        gg.write('\t'.join(loc_x for loc_x in loc2_list) + '\n')
                    else:
                        if len(loc_type.split('_')) == 3:
                            N1, N3 = loc2.split('_')[0], loc2.split('_')[1]
                            if N1 in N3:
                                loc2_list = loc2.split('\t')
                                loc2_list[-1] = "Intron"
                                gg.write('\t'.join(loc_x for loc_x in loc2_list) + '\n')
                            else:
                                gg.write(loc2)
                        else:
                            gg.write(loc2)

            # get location
            file_name = os.path.basename(input_file).split('.')[0]
            save_name = file_name + "."
            file1 = os.path.join(os.path.dirname(input_file), save_name)
            st_lines = open(output_, 'r').readlines()[1:]
            output_directory = self.entry_output.text()
            final_name = file_name + ".anno"
            final_results = os.path.join(output_directory, final_name)
            data = []
            st_lines2 = open(file1, 'r').readlines()[1:]
            for line in st_lines:
                parts = line.strip().split('\t')
                name, start, end, loc = parts[0], int(parts[1]), int(parts[2]), parts[-1]
                data.append((name, start, end, loc))

            printed_combinations = set()
            # write output results
            with open(final_results, 'w') as ff:
                ff.write("type\tlength\tstart\tend\tloc\tloc_type\n")
                for i in st_lines2:
                    st_list = i.split('\t')
                    st_join = '\t'.join(info.strip() for info in st_list)
                    target_list = list(range(int(st_list[2]), int(st_list[3])))
                    for num in target_list:
                        for name, start, end, loc in data:
                            if start <= num <= end:
                                combination = (tuple(target_list), name)
                                if combination not in printed_combinations:
                                    ff.write(f"{st_join}\t{name}\t{loc}\n")
                                    printed_combinations.add(combination)
                                break
        os.remove(output_)
        os.remove(save_file)
        print(f"The results was written into:\n\t\t{os.path.abspath(final_results)}\n{'-' * 80}")

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication

    app = QApplication([])
    window = SSRFindApp()
    window.show()
    app.exec_()

"""
This code is built based on the following work
CPStools-Pi_1.py
Author: Xu wenbo
Org:    China Pharmaceutical University
Email:  xwb7533@163.com
site:   https://github.com/Xwb7533/CPStools
"""
import os
import sys
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QFileDialog, QTextEdit, QProgressBar
from PyQt5.QtGui import QFont
from Bio import SeqIO

class ExtractionThread(QThread):
    progress = pyqtSignal(int)
    log = pyqtSignal(str)

    def __init__(self, input_files, output_dir):
        super().__init__()
        self.input_files = input_files
        self.output_dir = output_dir

    def run(self):
        try:
            ref_file = self.input_files[0]
            common_gene_extract(os.path.abspath(ref_file), self.output_dir, self.log)
            save_results_dir = os.path.abspath(os.path.join(self.output_dir, "common_gene"))

            fasta_dir = os.path.abspath(os.path.join(self.output_dir, 'IGS'))
            info_dir = os.path.join(self.output_dir, 'info')
            os.makedirs(fasta_dir, exist_ok=True)
            os.makedirs(info_dir, exist_ok=True)
            file_name = ''
            for file_path in self.input_files:
                if file_path.endswith('gb') or file_path.endswith('gbk'):
                    file_name = os.path.join(fasta_dir, os.path.basename(file_path).split('.')[0] + '_IGS.fasta')
                    IGS_extract(file_path, fasta_dir, info_dir, self.log)
                else:
                    self.log.emit(f"Skipping non-GenBank file: {file_path}")

            if file_name:
                common_IGS(file_name, self.log)
                self.log.emit("Extraction completed successfully.")
                self.log.emit(
                    "##### Next step is to do multiple alignment, the command is : ######\n"
                    "\t\t1: 'cd IGS/unalign_common_IGS/ \n"
                    "\t\t2: 'mkdir align_IGS'\n"
                    "\t\t3: 'for i in ./*.fasta; do mafft --auto $i > ./align_IGS/$i ;done'\n"
                )
            else:
                self.log.emit("No valid GenBank files found in the selected files.")

        except Exception as e:
            self.log.emit(f"Error occurred during extraction: {str(e)}")

def IGS_extract(input_file, fasta_dir, info_dir, log_signal):
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
        save_file = os.path.join(info_dir, os.path.basename(input_file).split('.')[0] + '_intergenic_location.txt')
        save_file_w = open(save_file, 'w')
        for i in range(len(all_info)-1):
            info_list = all_info[i].split('\t')
            next_list = all_info[i+1].split('\t')
            save_file_w.write(f"{info_list[0]}-{next_list[0]}\t{info_list[-2]}\t{next_list[1]}\n")
        end_gene_info = all_info[-1].split('\t')
        start_gene_info = all_info[0].split('\t')
        if int(end_gene_info[-2]) < int(start_gene_info[1]):
            save_file_w.write(f"{end_gene_info[0]}-{start_gene_info}[0]\t{end_gene_info[-2]}\t{start_gene_info[1]}\n")
        else:
            if int(end_gene_info[2]) < genome_length:
                save_file_w.write(f"{end_gene_info[0]}-{start_gene_info[0]}\t{end_gene_info[-2]}\t{genome_length}\t0\t\
                {start_gene_info[1]}\n")
            else:
                pass
        save_file_w.close()
        all_fasta_file = os.path.join(fasta_dir, os.path.basename(input_file).split('.')[0] + '_IGS.fasta')
        all_fasta = open(all_fasta_file, 'w')
        save_results = open(save_file, 'r')
        result_line = save_results.readline().strip()
        while result_line:
            result_line_list = result_line.split('\t')
            if len(result_line_list) == 3:
                if int(result_line_list[2]) > int(result_line_list[1]):
                    all_fasta.write(f">{result_line_list[0]}\n{my_seq[int(result_line_list[1]):int(result_line_list[2])]}\n")
                    result_line = save_results.readline().strip()
                else:
                    log_signal.emit(f"{result_line_list[0]} has overlap!")
                    result_line = save_results.readline().strip()

            else:
                all_fasta.write(f">{result_line_list[0]}\n{my_seq[int(result_line_list[1]):int(result_line_list[2])]}\
                {my_seq[int(result_line_list[3]):int(result_line_list[4])]}\n")
                result_line = save_results.readline().strip()
        all_fasta.close()

def common_IGS(input_file, log_signal):
    all_common = []
    for rec in SeqIO.parse(input_file, format='fasta'):
        all_common.append(rec.id)
    work_dir = os.path.dirname(input_file)
    for fasta_file in os.listdir(work_dir):
        if fasta_file:
            single_IGS = []
            if fasta_file.split('.')[1] == 'fasta':
                fasta_path = os.path.join(work_dir, fasta_file)
                log_signal.emit(f"The input intergenic fasta file is {fasta_path}")
                for rec2 in SeqIO.parse(fasta_path, format='fasta'):
                    single_IGS.append(rec2.id)
                for name1_index in range(len(all_common)-1, -1, -1):
                    if all_common[name1_index].lower() not in [single_name.lower() for single_name in single_IGS]:
                        all_common.remove(all_common[name1_index])
    cp_sort_IGS_file = open(os.path.join(work_dir, 'cp_sort_IGS.txt'), 'w')
    for i in all_common:
        cp_sort_IGS_file.write(f"{i}\n")
    cp_sort_IGS_file.close()
    log_signal.emit(f"The intergenic fasta number is {len(all_common)}")
    save_dir = os.path.join(os.path.dirname(input_file), 'unalign_common_IGS')
    os.mkdir(save_dir)
    for common_name in all_common:
        save_file_path = os.path.join(save_dir, common_name + '.fasta')
        save_file = open(save_file_path, 'w')
        for fasta_file in os.listdir(work_dir):
            fasta_path = os.path.join(work_dir, fasta_file)
            if os.path.isfile(fasta_path):
                if fasta_path.split('.')[1] == 'fasta':
                    for rec in SeqIO.parse(fasta_path, format='fasta'):
                        if rec.id == common_name:
                            save_file.write(f">{fasta_file.split('_IGS')[0]}\n{rec.seq}\n")
        save_file.close()

def common_gene_extract(input_file, output_dir, log_signal):
    work_dir = os.path.dirname(input_file)
    all_gene = []
    for rec in SeqIO.parse(input_file, format='genbank'):
        for feature in rec.features:
            if feature.type == 'CDS' or feature.type == 'tRNA' or feature.type == 'rRNA':
                if feature.qualifiers['gene'][0] not in all_gene:
                    all_gene.append(feature.qualifiers['gene'][0])
    log_signal.emit(f"Total gene number in reference file: {len(all_gene)}")
    for files in os.listdir(work_dir):
        if files.endswith('gb') or files.endswith('gbk'):
            single_gene = []
            gb_file = os.path.join(work_dir, files)
            log_signal.emit(f"Processing file: {gb_file}")
            for rec in SeqIO.parse(gb_file, format='genbank'):
                for feature in rec.features:
                    if feature.type == 'CDS' or feature.type == 'tRNA' or feature.type == 'rRNA':
                        if feature.qualifiers['gene'][0] not in single_gene:
                            single_gene.append(feature.qualifiers['gene'][0])
                log_signal.emit(f"Total gene number in file {files}: {len(single_gene)}")
            for gene_index in range(len(all_gene)-1, -1, -1):
                if all_gene[gene_index].lower() not in [y.lower() for y in single_gene]:
                    all_gene.remove(all_gene[gene_index])
    log_signal.emit(f"Total common gene number: {len(all_gene)}")
    gene_name_file = os.path.join(output_dir, 'gene_cp_sort.txt')
    with open(gene_name_file, 'w') as ff:
        for i in all_gene:
            ff.write(f'{i}\n')
    save_dir = os.path.join(output_dir, 'common_gene')
    if os.path.exists(save_dir):
        log_signal.emit(f"The save directory already exists: {os.path.abspath(save_dir)}")
        response = input("Do you want to overwrite it? (y/n): ")
        if response.lower() != 'y':
            log_signal.emit("Operation cancelled by user.")
            return
        else:
            log_signal.emit("Overwriting existing directory.")
    os.makedirs(save_dir, exist_ok=True)
    for gene_name in all_gene:
        file_name = str(gene_name) + '.fasta'
        file_path = os.path.join(save_dir, file_name)
        with open(file_path, 'w') as fasta_file:
            for gb_file in os.listdir(work_dir):
                if gb_file.endswith('gb') or gb_file.endswith('gbk'):
                    gb_file_path = os.path.join(work_dir, gb_file)
                    fasta_file.write(f">{gb_file.split('.')[0]}\n")
                    for rec in SeqIO.parse(gb_file_path, format='genbank'):
                        my_seqs = []
                        for feature in rec.features:
                            if feature.type == 'CDS' or feature.type == 'tRNA' or feature.type == 'rRNA':
                                if feature.qualifiers['gene'][0].lower() == gene_name.lower():
                                    my_seqs.append(feature.extract(rec.seq))
                        if len(my_seqs) == 1:
                            fasta_file.write(f"{my_seqs[0]}\n")
                        if len(my_seqs) == 2:
                            my_seqs.remove(my_seqs[0]) if len(my_seqs[0]) <= len(my_seqs[1]) else my_seqs.remove(my_seqs[1])
                            fasta_file.write(f"{my_seqs[0]}\n")

class commongeneAndIGSExtractApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Common Genes and IGS Extraction')
        self.setGeometry(100, 100, 800, 600)

        # Main widget container
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)

        # Layouts
        main_layout = QVBoxLayout()
        main_widget.setLayout(main_layout)
        
        # Title label
        label_title = QLabel('Extract Common Genes and IGS')
        label_title.setFont(QFont('Arial', 16))
        main_layout.addWidget(label_title, alignment=Qt.AlignCenter)
        
        # Input files selection
        input_files_layout = QHBoxLayout()
        main_layout.addLayout(input_files_layout)
        self.input_files_label = QLabel('Input Files:')
        input_files_layout.addWidget(self.input_files_label)

        self.input_files_lineedit = QLineEdit()
        input_files_layout.addWidget(self.input_files_lineedit)

        self.input_files_button = QPushButton('Browse')
        self.input_files_button.clicked.connect(self.browseInputFiles)
        input_files_layout.addWidget(self.input_files_button)

        # Output directory selection
        output_dir_layout = QHBoxLayout()
        main_layout.addLayout(output_dir_layout)

        self.output_dir_label = QLabel('Output Directory:')
        output_dir_layout.addWidget(self.output_dir_label)

        self.output_dir_lineedit = QLineEdit()
        output_dir_layout.addWidget(self.output_dir_lineedit)

        self.output_dir_button = QPushButton('Browse')
        self.output_dir_button.clicked.connect(self.browseOutputDir)
        output_dir_layout.addWidget(self.output_dir_button)

        # Progress bar
        self.progress_bar = QProgressBar()
        main_layout.addWidget(self.progress_bar)

        # Output logs display
        self.output_logs_label = QLabel('Output Logs:')
        main_layout.addWidget(self.output_logs_label)

        self.output_logs_textedit = QTextEdit()
        main_layout.addWidget(self.output_logs_textedit)

        # Start Extraction Button
        self.start_extraction_button = QPushButton('Start Extraction')
        self.start_extraction_button.clicked.connect(self.startExtraction)
        main_layout.addWidget(self.start_extraction_button)

    def browseInputFiles(self):
        files, _ = QFileDialog.getOpenFileNames(self, 'Select Input Files', '', 'GenBank Files (*.gb *.gbk)')
        if files:
            self.input_files_lineedit.setText(';'.join(files))

    def browseOutputDir(self):
        directory = QFileDialog.getExistingDirectory(self, 'Select Output Directory')
        if directory:
            self.output_dir_lineedit.setText(directory)

    def startExtraction(self):
        input_files = self.input_files_lineedit.text().split(';')
        output_dir = self.output_dir_lineedit.text()

        if not input_files:
            self.output_logs_textedit.append('Please select input files!')
            return
        if not output_dir:
            self.output_logs_textedit.append('Please select an output directory!')
            return

        self.start_extraction_button.setEnabled(False)
        self.progress_bar.setValue(0)

        self.thread = ExtractionThread(input_files, output_dir)
        self.thread.progress.connect(self.progress_bar.setValue)
        self.thread.log.connect(self.output_logs_textedit.append)
        self.thread.finished.connect(self.extractionFinished)
        self.thread.start()

    def extractionFinished(self):
        self.start_extraction_button.setEnabled(True)
        self.progress_bar.setValue(100)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = commongeneAndIGSExtractApp()
    window.show()
    sys.exit(app.exec_())
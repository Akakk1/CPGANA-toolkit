"""
This code is built based on the following work
CPStools-information.py
Author: Xu wenbo
Org:    China Pharmaceutical University
Email:  xwb7533@163.com
site:   https://github.com/Xwb7533/CPStools
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from Bio import SeqIO

class GeneAnalysisApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Information Get")
        self.setGeometry(100, 100, 600, 400)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.ui_manager = UIManager(self.main_layout)
        self.analysis_manager = AnalysisManager()

        self.ui_manager.browse_input_button.clicked.connect(self.browse_genbank_file)
        self.ui_manager.browse_output_button.clicked.connect(self.browse_output_directory)
        self.ui_manager.analyze_button.clicked.connect(self.analyze_genbank_file)

        self.result_text = QTextEdit(self)
        self.result_text.setReadOnly(True)
        self.main_layout.addWidget(self.result_text)

    def browse_genbank_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Select Genbank File", "", "Genbank Files (*.gb *.gbk)")
        if filename:
            self.ui_manager.input_file_entry.setText(filename)

    def browse_output_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if directory:
            self.ui_manager.output_dir_entry.setText(directory)

    def analyze_genbank_file(self):
        input_file = self.ui_manager.input_file_entry.text().strip()
        output_dir = self.ui_manager.output_dir_entry.text().strip()

        if input_file and output_dir:
            try:
                result = self.analysis_manager.run_analysis(input_file, output_dir)
                self.display_results(result)
                QMessageBox.information(self, "Analysis Complete", "Analysis completed successfully!")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

        else:
            QMessageBox.warning(self, "Missing Input", "Please select input file and output directory.")

    def display_results(self, result):
        # Clear existing content
        self.result_text.clear()

        # Initialize the table with headers
        table = "Category\tGene group\tGene name\tCount\n"

        # Append each line from the result to the table
        table += result

        # Set the formatted table as the content of result_text
        self.result_text.setPlainText(table)



class UIManager:
    def __init__(self, layout):
        self.layout = layout
        self.create_widgets()

    def create_widgets(self):
        # Title label
        self.label_title = QLabel('Get Annotation Information from Genbank File')
        self.label_title.setFont(QFont('Arial', 16))
        self.layout.addWidget(self.label_title, alignment=Qt.AlignCenter)

        # File Selection Frame
        self.create_file_selection_frame()

        # Output Entry Frame
        self.create_output_entry_frame()

        # Analyze Button
        self.analyze_button = QPushButton("Analyze")
        self.layout.addWidget(self.analyze_button, alignment=Qt.AlignCenter)

    def create_file_selection_frame(self):
        self.frame_input = QWidget()
        self.frame_layout = QVBoxLayout(self.frame_input)
        self.layout.addWidget(self.frame_input)

        self.input_layout = QHBoxLayout()
        self.input_file_label = QLabel("Select Genbank File:")
        self.input_layout.addWidget(self.input_file_label)

        self.input_file_entry = QLineEdit()
        self.input_layout.addWidget(self.input_file_entry)

        self.browse_input_button = QPushButton("Browse")
        self.input_layout.addWidget(self.browse_input_button)

        self.frame_layout.addLayout(self.input_layout)

    def create_output_entry_frame(self):
        self.frame_output = QWidget()
        self.frame_layout_output = QHBoxLayout(self.frame_output)
        self.layout.addWidget(self.frame_output)

        self.output_dir_label = QLabel("Output Directory:")
        self.frame_layout_output.addWidget(self.output_dir_label)

        self.output_dir_entry = QLineEdit()
        self.frame_layout_output.addWidget(self.output_dir_entry)

        self.browse_output_button = QPushButton("Browse")
        self.frame_layout_output.addWidget(self.browse_output_button)


class AnalysisManager:
    def __init__(self):
        pass

    def run_analysis(self, input_file, output_dir):
        intron_result = self.intron_find(input_file)
        information_table(input_file, output_dir)
        return intron_result

    def intron_find(self, input_file):
        exon_counts = {2: [], 3: [], 'more_than_3': []}

        for record in SeqIO.parse(input_file, 'genbank'):
            for feat in record.features:
                if feat.type in ['CDS', 'tRNA', 'rRNA'] and 'gene' in feat.qualifiers:
                    gene_name = feat.qualifiers['gene'][0]
                    if len(feat.location.parts) == 2:
                        exon_counts[2].append(gene_name)
                    elif len(feat.location.parts) == 3:
                        exon_counts[3].append(gene_name)
                    elif len(feat.location.parts) > 3:
                        exon_counts['more_than_3'].append(gene_name)

        result = f"Two exons: {', '.join(exon_counts[2])}\n\nThree exons: {', '.join(exon_counts[3])}\n\nMore than three exons: {', '.join(exon_counts['more_than_3'])}"
        return result


def information_table(input_file, output_dir):
    input_filename = os.path.basename(input_file)
    input_filename = os.path.splitext(input_filename)[0]
    output_filename = f"{input_filename}_annoinfo.txt"
    output_file = os.path.join(output_dir, output_filename)

    categories = {
        'Photosynthesis': {
            'Subunits of photosystem I': 'psa',
            'Subunits of photosystem II': 'psb',
            'Subunits of NADH dehydrogenase': 'ndh',
            'Subunits of cytochrome b/f complex': 'pet',
            'Subunits of ATP synthase': 'atp',
            'Large subunit of rubisco': 'rbcl'
        },
        'Self-replication': {
            'Proteins of large ribosomal subunit': 'rpl',
            'Proteins of small ribosomal subunit': 'rps',
            'Subunits of RNA polymerase': 'rpo',
            'RrnA gene': 'rrn',
            'TrnA gene': 'trn'
        },
        'Other genes': {
            'Maturase': 'matk',
            'Protease': 'clpp',
            'Envelope membrane protein': 'ce',
            'Acetyl CoA': 'acc',
            'cytochrome synthesis': 'ccs',
            'Translation': 'inf',
            'ORFS': 'orf'
        },
        'Genes of unknown function': {
            'Conserved hypothetical chloroplast ORF': 'ycf'
        }
    }

    gene_counts = {}

    for rec in SeqIO.parse(input_file, 'genbank'):
        for feature in rec.features:
            if feature.type == 'gene' and 'gene' in feature.qualifiers:
                gene_name = feature.qualifiers['gene'][0]
                matched_category = None
                matched_subcategory = None

                for category, subcategories in categories.items():
                    for subcategory, prefix in subcategories.items():
                        if gene_name.lower().startswith(prefix):
                            matched_category = category
                            matched_subcategory = subcategory
                            break
                    if matched_category:
                        break

                if not matched_category:
                    matched_category = 'Other'

                gene_counts.setdefault(matched_category, {}).setdefault(matched_subcategory, {}).setdefault(gene_name, 0)
                gene_counts[matched_category][matched_subcategory][gene_name] += 1

    # Write to the output file in tab-separated format
    with open(output_file, 'w') as ff:
        ff.write('Category\tGene group\tGene name\n')
        for category, subcategories in gene_counts.items():
            for subcategory, genes in subcategories.items():
                gene_list = []
                for gene_name, count in genes.items():
                    if count > 1:
                        gene_list.append(f"{gene_name} ({count})")
                    elif count == 1:
                        gene_list.append(gene_name)
                
                ff.write(f'{category}\t{subcategory}\t{", ".join(gene_list)}\n')

    return output_file  # Return the path to the output file
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = GeneAnalysisApp()
    main_window.show()
    sys.exit(app.exec_())

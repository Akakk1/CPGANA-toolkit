import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QTextEdit, QFileDialog, QLabel, QLineEdit, QMessageBox
from PyQt5.QtGui import QFont
from Bio import SeqIO

class AcExtractApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('GenBank File Species and Accession Extractor')
        self.setGeometry(100, 100, 800, 600)

        # Title label
        title_label = QLabel('Extract Accession Numbers From GBFiles')
        title_label.setFont(QFont('Arial', 16))

        # Input and result labels
        input_label = QLabel('Input Files:')
        result_label = QLabel('Results:')

        # Text boxes
        self.input_text = QTextEdit()
        self.input_text.setReadOnly(True)
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)

        # Open files button
        self.btn_open = QPushButton('Open GenBank Files')
        self.btn_open.clicked.connect(self.open_files)

        # Process and extract button
        self.btn_process = QPushButton('Extract')
        self.btn_process.clicked.connect(self.process_gb_files)

        # Output directory selection
        self.output_dir_label = QLabel('Output Directory:')
        self.output_dir_text = QLineEdit()
        self.output_dir_text.setReadOnly(True)
        self.btn_output_dir = QPushButton('Select Output Directory')
        self.btn_output_dir.clicked.connect(self.select_output_directory)

        # Save button
        self.btn_save = QPushButton('Save')
        self.btn_save.clicked.connect(self.save_file)

        # Layouts
        layout = QVBoxLayout()
        layout.addWidget(title_label)

        input_result_layout = QHBoxLayout()
        input_result_layout.addWidget(input_label)
        input_result_layout.addWidget(result_label)
        layout.addLayout(input_result_layout)

        text_layout = QHBoxLayout()
        text_layout.addWidget(self.input_text)
        text_layout.addWidget(self.result_text)
        layout.addLayout(text_layout)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.btn_open)
        buttons_layout.addWidget(self.btn_process)
        layout.addLayout(buttons_layout)

        output_dir_layout = QHBoxLayout()
        output_dir_layout.addWidget(self.output_dir_label)
        output_dir_layout.addWidget(self.output_dir_text)
        output_dir_layout.addWidget(self.btn_output_dir)
        layout.addLayout(output_dir_layout)

        layout.addWidget(self.btn_save)

        self.setLayout(layout)

    def open_files(self):
        options = QFileDialog.Options()
        file_names, _ = QFileDialog.getOpenFileNames(self, 'Open GenBank Files', '', 'GenBank Files (*.gb *.gbk);;All Files (*)', options=options)
        if file_names:
            self.file_paths = file_names
            self.input_text.clear()
            self.input_text.append('Selected files:')
            for file_path in self.file_paths:
                self.input_text.append(file_path)

    def select_output_directory(self):
        options = QFileDialog.Options()
        directory = QFileDialog.getExistingDirectory(self, 'Select Output Directory', options=options)
        if directory:
            self.output_directory = directory
            self.output_dir_text.setText(directory)

    def process_gb_files(self):
        try:
            gb_files = self.file_paths
        except AttributeError:
            self.result_text.append('Please select GenBank files first.')
            return

        self.result_text.clear()
        self.extracted_data = []

        try:
            self.result_text.append('File Name\tSpecies Name\tAccession Number')
            for gb_file in gb_files:
                file_name = gb_file.split('/')[-1]  # Extract file name from path
                for record in SeqIO.parse(gb_file, 'genbank'):
                    species_name = record.annotations.get('organism', 'Unknown')
                    accession = record.annotations['accessions'][0]
                    self.extracted_data.append((file_name, species_name, accession))
                    self.result_text.append(f'{file_name}\t{species_name}\t{accession}')
        except Exception as e:
            self.result_text.append(f'Error processing files: {str(e)}')

    def save_file(self):
        try:
            output_file = self.output_directory + '/species_accession_files.txt'
            with open(output_file, 'w') as out_file:
                out_file.write('File Name\tSpecies Name\tAccession Number\n')
                for data in self.extracted_data:
                    out_file.write(f'{data[0]}\t{data[1]}\t{data[2]}\n')

            QMessageBox.information(self, 'File Saved', f'Species names, accession numbers, and file names saved to {output_file}')
        except AttributeError:
            self.result_text.append('Please select an output directory first.')
        except Exception as e:
            self.result_text.append(f'Error saving file: {str(e)}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = AcExtractApp()
    window.show()
    sys.exit(app.exec_())

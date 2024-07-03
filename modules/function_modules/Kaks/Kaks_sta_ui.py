import os
import sys
import pandas as pd
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QPushButton, QVBoxLayout, QWidget, QLabel, QMessageBox, QPlainTextEdit
from PyQt5.QtGui import QFont

class KaksStaApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Kaks Analyzer')
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        title_label = QLabel('KaKs Result Statistics', self)
        title_label.setFont(QFont('Arial', 16))
        layout.addWidget(title_label)

        self.file_text = QPlainTextEdit(self)
        self.file_text.setReadOnly(True)
        layout.addWidget(QLabel('Selected Files:', self))
        layout.addWidget(self.file_text)

        self.select_files_button = QPushButton('Select Kaks Files', self)
        self.select_files_button.clicked.connect(self.select_files)
        layout.addWidget(self.select_files_button)

        self.output_text = QPlainTextEdit(self)
        self.output_text.setReadOnly(True)
        layout.addWidget(QLabel('Output Directory:', self))
        layout.addWidget(self.output_text)

        self.select_output_button = QPushButton('Select Output Directory', self)
        self.select_output_button.clicked.connect(self.select_output)
        layout.addWidget(self.select_output_button)

        self.process_button = QPushButton('Process Files', self)
        self.process_button.clicked.connect(self.process_files)
        layout.addWidget(self.process_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def select_files(self):
        self.file_paths, _ = QFileDialog.getOpenFileNames(self, 'Select Kaks Files', '', 'Kaks Files (*.kaks)')
        if self.file_paths:
            self.file_text.setPlainText('\n'.join(self.file_paths))

    def select_output(self):
        self.output_dir = QFileDialog.getExistingDirectory(self, 'Select Output Directory', '')
        if self.output_dir:
            self.output_text.setPlainText(self.output_dir)

    def process_files(self):
        if not hasattr(self, 'file_paths') or not hasattr(self, 'output_dir'):
            QMessageBox.warning(self, 'Warning', 'Please select files and output directory first.')
            return

        data = {}
        for file_path in self.file_paths:
            species_name = self.extract_species_name(file_path)
            df = pd.read_csv(file_path, sep='\t')
            if 'Sequence' in df.columns and 'Ka/Ks' in df.columns:
                data[species_name] = df[['Sequence', 'Ka/Ks']]
            else:
                QMessageBox.warning(self, 'Warning', f'File {file_path} does not contain required columns.')
                return

        output_df = pd.DataFrame(columns=['Sequence'])
        for species, df in data.items():
            output_df[species] = df['Ka/Ks']
            output_df['Sequence'] = df['Sequence']

        output_path = os.path.join(self.output_dir, 'kaks_output.xlsx')
        output_df.to_excel(output_path, index=False, na_rep='NA')
        QMessageBox.information(self, 'Success', f'Data has been saved to {output_path}')

    def extract_species_name(self, file_path):
        file_name = os.path.basename(file_path)
        parts = file_name.split('_')
        species_name = '_'.join(parts[1:parts.index('and')])
        return species_name

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        ex = KaksStaApp()
        ex.show()
        sys.exit(app.exec_())
    except Exception as e:
        self.console_output.appendPlainText(f"Failed: {str(e)}")
        logging.error(f"Failed: {str(e)}")    
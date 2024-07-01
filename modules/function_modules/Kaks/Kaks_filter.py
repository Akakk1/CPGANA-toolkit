import sys
import os
import pandas as pd
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox, QComboBox, QCheckBox, QSpinBox
from PyQt5.QtGui import QFont

class KaKsValueProcessor(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('KaKs Value Processor')
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        # Title Label
        title_label = QLabel('KaKs Value Process')
        title_label.setFont(QFont('Arial', 16))
        layout.addWidget(title_label)

        # Input File Selection
        self.input_file_path = QLineEdit()
        self.input_file_path.setPlaceholderText('Enter input file path or select from dialog')
        select_button = QPushButton('Select')
        select_button.clicked.connect(self.select_input_file)
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_file_path)
        input_layout.addWidget(select_button)
        layout.addLayout(input_layout)

        # Output Directory Selection
        self.output_dir_path = QLineEdit()
        self.output_dir_path.setPlaceholderText('Enter output directory path or select from dialog')
        browse_button = QPushButton('Browse')
        browse_button.clicked.connect(self.select_output_dir)
        output_layout = QHBoxLayout()
        output_layout.addWidget(self.output_dir_path)
        output_layout.addWidget(browse_button)
        layout.addLayout(output_layout)

        # NA Value Handling Options
        self.filter_na_checkbox = QCheckBox('Filter NA values')
        self.filter_na_threshold = QSpinBox()
        self.filter_na_threshold.setRange(0, 100)
        self.filter_na_threshold.setValue(50)
        self.filter_na_threshold.setSuffix('%')
        self.filter_na_checkbox.stateChanged.connect(self.toggle_filter_na_threshold)
        filter_na_layout = QHBoxLayout()
        filter_na_layout.addWidget(self.filter_na_checkbox)
        filter_na_layout.addWidget(self.filter_na_threshold)
        layout.addLayout(filter_na_layout)

        self.fill_na_checkbox = QCheckBox('Fill NA values')
        self.fill_na_method = QComboBox()
        self.fill_na_method.addItems(['Mean', 'Median', 'Mode'])
        self.fill_na_checkbox.stateChanged.connect(self.toggle_fill_na_method)
        fill_na_layout = QHBoxLayout()
        fill_na_layout.addWidget(self.fill_na_checkbox)
        fill_na_layout.addWidget(self.fill_na_method)
        layout.addLayout(fill_na_layout)

        # Process Button
        process_button = QPushButton('Process')
        process_button.clicked.connect(self.process_file)
        layout.addWidget(process_button)

        self.setLayout(layout)

    def select_input_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select Input File', '', 'Excel Files (*.xlsx)')
        if file_path:
            self.input_file_path.setText(file_path)

    def select_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, 'Select Output Directory')
        if dir_path:
            self.output_dir_path.setText(dir_path)

    def toggle_filter_na_threshold(self, state):
        self.filter_na_threshold.setEnabled(state == 2)

    def toggle_fill_na_method(self, state):
        self.fill_na_method.setEnabled(state == 2)

    def process_file(self):
        input_file = self.input_file_path.text()
        output_dir = self.output_dir_path.text()

        if not input_file or not output_dir:
            QMessageBox.warning(self, 'Input Error', 'Please select input file and output directory.')
            return

        try:
            df = pd.read_excel(input_file, header=0, index_col=0)
        except Exception as e:
            QMessageBox.critical(self, 'File Error', f'Failed to read input file: {str(e)}')
            return

        if self.filter_na_checkbox.isChecked():
            threshold = self.filter_na_threshold.value() / 100.0
            df = df.dropna(thresh=int(len(df.columns) * threshold), axis=0).dropna(thresh=int(len(df) * threshold), axis=1)

        if self.fill_na_checkbox.isChecked():
            method = self.fill_na_method.currentText()
            if method == 'Mean':
                df = df.fillna(df.mean())
            elif method == 'Median':
                df = df.fillna(df.median())
            elif method == 'Mode':
                df = df.fillna(df.mode().iloc[0])

        output_file = os.path.join(output_dir, 'processed_KaKs_values.xlsx')
        try:
            df.to_excel(output_file)
            QMessageBox.information(self, 'Success', f'File processed successfully and saved to {output_file}')
        except Exception as e:
            QMessageBox.critical(self, 'Save Error', f'Failed to save output file: {str(e)}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = KaKsValueProcessor()
    ex.show()
    sys.exit(app.exec_())
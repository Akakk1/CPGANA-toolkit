import sys
import pandas as pd
import os
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QTableWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtCore import Qt
from scipy.stats import ttest_1samp, shapiro, mannwhitneyu, t
import numpy as np

class KaKsSigCalculatorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout()

        # Title Label
        titleLabel = QLabel("Calculate Significance For KaKs Ratio", self)
        titleLabel.setAlignment(Qt.AlignCenter)
        titleLabel.setStyleSheet("font-size: 16px; font-family: Arial;")
        layout.addWidget(titleLabel)
        
        # Input File Selection
        self.inputLabel = QLabel("Input File:", self)
        self.inputLineEdit = QLineEdit(self)
        self.inputButton = QPushButton("Select File", self)
        self.inputButton.clicked.connect(self.select_input_file)
        
        inputLayout = QHBoxLayout()
        inputLayout.addWidget(self.inputLabel)
        inputLayout.addWidget(self.inputLineEdit)
        inputLayout.addWidget(self.inputButton)
        
        layout.addLayout(inputLayout)
        
        # Display Input File Info and Calculate Button
        self.inputInfoTable = QTableWidget(self)
        self.calculateButton = QPushButton("Calculate", self)
        self.calculateButton.clicked.connect(self.calculate)

        # Display Calculation Results
        self.resultTable = QTableWidget(self)
        
        tableLayout = QHBoxLayout()
        tableLayout.addWidget(self.inputInfoTable)
        tableLayout.addWidget(self.resultTable)
        
        layout.addLayout(tableLayout)
        layout.addWidget(self.calculateButton)
        
        # Output Directory Selection and Save Button
        self.outputDirLineEdit = QLineEdit(self)
        self.outputDirButton = QPushButton("Select Output Directory", self)
        self.outputDirButton.clicked.connect(self.select_output_directory)
        self.saveButton = QPushButton("Save Results", self)
        self.saveButton.clicked.connect(self.save_results)
        
        outputLayout = QHBoxLayout()
        outputLayout.addWidget(QLabel("Output Directory:", self))
        outputLayout.addWidget(self.outputDirLineEdit)
        outputLayout.addWidget(self.outputDirButton)
        outputLayout.addWidget(self.saveButton)
        
        layout.addLayout(outputLayout)
        
        self.setLayout(layout)
        self.setWindowTitle('Ka/Ks Analyzer')
        self.setGeometry(300, 300, 800, 600)

    def select_input_file(self):
        try:
            options = QFileDialog.Options()
            file, _ = QFileDialog.getOpenFileName(self, "Select Input File", "", "Excel Files (*.xlsx);;All Files (*)", options=options)
            if file:
                self.inputLineEdit.setText(file)
                self.load_input_file(file)
        except Exception as e:
            self.show_error_message(str(e))

    def load_input_file(self, file):
        try:
            df = pd.read_excel(file)
            self.inputInfoTable.setColumnCount(len(df.columns))
            self.inputInfoTable.setHorizontalHeaderLabels(df.columns)
            self.inputInfoTable.setRowCount(len(df.index))

            for i in range(len(df.index)):
                for j in range(len(df.columns)):
                    self.inputInfoTable.setItem(i, j, QTableWidgetItem(str(df.iat[i, j])))
        except Exception as e:
            self.show_error_message(str(e))

    def select_output_directory(self):
        try:
            options = QFileDialog.Options()
            directory = QFileDialog.getExistingDirectory(self, "Select Output Directory", "", options=options)
            if directory:
                self.outputDirLineEdit.setText(directory)
        except Exception as e:
            self.show_error_message(str(e))
    
    def save_results(self):
        try:
            output_directory = self.outputDirLineEdit.text()
            if output_directory:
                output_file = os.path.join(output_directory, 'analysis_results.xlsx')
                self.result_df.to_excel(output_file, index=False)
        except Exception as e:
            self.show_error_message(str(e))

    def calculate_confidence_interval(self, data, confidence=0.95):
        n = len(data)
        mean = np.mean(data)
        se = np.std(data, ddof=1) / np.sqrt(n)
        h = se * t.ppf((1 + confidence) / 2., n - 1)
        return mean - h, mean + h

    def calculate(self):
        try:
            file = self.inputLineEdit.text()
            if not file:
                raise ValueError("Please select an input file.")
            
            df = pd.read_excel(file, index_col=0)
            result_df = pd.DataFrame(columns=['CDS', 'Ka/Ks Mean', 'Selection', 'p-value', 'Significant', 'Normality', 'Test', 'Confidence Interval'])

            for gene in df.columns:
                ka_ks_values = df[gene].dropna()
                if len(ka_ks_values) == 0:
                    continue

                stat, p_shapiro = shapiro(ka_ks_values)
                normality = p_shapiro > 0.05

                if normality:
                    t_stat, p_value = ttest_1samp(ka_ks_values, 1)
                    test_used = 't-test'
                    mean_ka_ks = ka_ks_values.mean()
                    conf_int = self.calculate_confidence_interval(ka_ks_values)
                else:
                    u_stat, p_value = mannwhitneyu(ka_ks_values, [1]*len(ka_ks_values), alternative='two-sided')
                    test_used = 'Mann-Whitney U'
                    mean_ka_ks = ka_ks_values.mean()
                    conf_int = (np.percentile(ka_ks_values, 25), np.percentile(ka_ks_values, 75))

                significant = p_value < 0.05

                if (test_used == 't-test' and t_stat > 0 and significant) or (test_used == 'Mann-Whitney U' and mean_ka_ks > 1 and significant):
                    selection = 'positive selection'
                elif (test_used == 't-test' and t_stat < 0 and significant) or (test_used == 'Mann-Whitney U' and mean_ka_ks < 1 and significant):
                    selection = 'purifying selection'
                else:
                    selection = 'none'

                result_df = pd.concat([result_df, pd.DataFrame([{
                    'CDS': gene,
                    'Ka/Ks Mean': mean_ka_ks,
                    'Selection': selection,
                    'p-value': p_value,
                    'Significant': significant,
                    'Normality': normality,
                    'Test': test_used,
                    'Confidence Interval': conf_int
                }])], ignore_index=True)

            self.result_df = result_df
            self.resultTable.setColumnCount(len(result_df.columns))
            self.resultTable.setHorizontalHeaderLabels(result_df.columns)
            self.resultTable.setRowCount(len(result_df.index))

            for i in range(len(result_df.index)):
                for j in range(len(result_df.columns)):
                    self.resultTable.setItem(i, j, QTableWidgetItem(str(result_df.iat[i, j])))

        except Exception as e:
            self.show_error_message(str(e))
    
    def show_error_message(self, message):
        error_dialog = QMessageBox(self)
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setText("An error occurred")
        error_dialog.setInformativeText(message)
        error_dialog.setWindowTitle("Error")
        error_dialog.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = KaKsSigCalculatorApp()
    ex.show()
    sys.exit(app.exec_())

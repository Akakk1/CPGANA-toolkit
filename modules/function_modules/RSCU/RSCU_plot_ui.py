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
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QLineEdit, 
                             QPushButton, QFileDialog, QVBoxLayout, QMessageBox, QWidget, QTextEdit, QSpinBox, QHBoxLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

class RSCUVisualizeApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("RSCU Plotter")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Title label
        label_title = QLabel('Plot Stacked Diagram of RSCU Values')
        label_title.setFont(QFont('Arial', 16))
        layout.addWidget(label_title, alignment=Qt.AlignCenter) 
        
        self.path_text = QTextEdit(self)
        self.path_text.setMaximumHeight(30)
        layout.addWidget(self.path_text)
        
        # Load file button
        self.load_button = QPushButton("File Directory", self)
        self.load_button.clicked.connect(self.load_file)
        layout.addWidget(self.load_button)

        # Output directory selection and DPI selection
        options_layout = QHBoxLayout()
        
        self.output_dir_label = QLabel("Output Directory:")
        options_layout.addWidget(self.output_dir_label)

        self.output_dir_text = QLineEdit(self)
        self.output_dir_text.setReadOnly(True)
        options_layout.addWidget(self.output_dir_text)

        self.output_dir_button = QPushButton("Select Output Directory", self)
        self.output_dir_button.clicked.connect(self.select_output_directory)
        options_layout.addWidget(self.output_dir_button)

        self.dpi_label = QLabel("Select DPI:")
        options_layout.addWidget(self.dpi_label)

        self.dpi_spinbox = QSpinBox()
        self.dpi_spinbox.setMinimum(50)
        self.dpi_spinbox.setMaximum(600)
        self.dpi_spinbox.setValue(300)
        options_layout.addWidget(self.dpi_spinbox)

        layout.addLayout(options_layout)

        # Plot button
        self.plot_button = QPushButton("Plot Diagram", self)
        self.plot_button.clicked.connect(self.plot_data)
        layout.addWidget(self.plot_button)
        
        self.file_path = None
        self.data = None
        self.output_dir = None

    def load_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_path, _ = QFileDialog.getOpenFileName(self, "Select RSCU Data File", "", "Text Files (*.txt);;All Files (*)", options=options)
        if file_path:
            self.file_path = file_path
            self.path_text.setText(self.file_path)

    def select_output_directory(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory", options=options)
        if directory:
            self.output_dir = directory
            self.output_dir_text.setText(self.output_dir)

    def plot_data(self):
        if self.file_path:
            self.data = load_data(self.file_path)
            self.plot_rscu_diagram()

    def plot_rscu_diagram(self):
        if self.data is None:
            return

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), gridspec_kw={'height_ratios': [2, 1]})

        plot_rscu(self.data, ax1)
        amino_acids = list(self.data.groupby('AminoAcid').groups.keys())
        plot_rscu_heatmap(self.data, ax2, amino_acids)

        plt.subplots_adjust(hspace=0)
        plt.tight_layout()

        # Save the plot
        if self.output_dir:
            file_name = os.path.basename(self.file_path)
            save_path = os.path.join(self.output_dir, f"{file_name}_plot.png")
            plt.savefig(save_path, dpi=self.dpi_spinbox.value())
            QMessageBox.information(self, "Success", f"Plot saved successfully as {save_path}")
        else:
            QMessageBox.critical(self, "Error", "Please select an output directory.")

        plt.show()

def load_data(file_path):
    data = pd.read_csv(file_path, sep='\t', header=None)
    data.columns = ['AminoAcid', 'Codon', 'Number', 'RSCU']
    return data

def plot_rscu(data, ax):
    grouped_data = data.groupby('AminoAcid')
    amino_acids = list(grouped_data.groups.keys())
    x = np.arange(len(amino_acids))

    for i, (amino_acid, group) in enumerate(grouped_data):
        bottom = 0
        color_index = 0
        for _, row in group.iterrows():
            colors = ['#8ECFC9', '#FFBE7A', '#FA7F6F', '#82B0D2', '#8EB8DC', '#E7DAD2']
            color = colors[color_index % len(colors)]
            color_index += 1

            ax.bar(
                x[i], row['RSCU'], bottom=bottom, color=color,
                width=0.6, linewidth=1, edgecolor='black',
                label=row['Codon'] if i == 0 else ""
            )

            height = bottom + row['RSCU']
            ax.text(
                x[i], height - row['RSCU'] / 2, f'{row["RSCU"]:.2f}', ha='center', va='center',
                fontsize=8, color='black', fontweight='bold', fontstyle='italic'
            )
            bottom = height

    ax.set_ylabel('RSCU')
    ax.set_xticks(x)
    ax.set_xticklabels(amino_acids, rotation=0, fontweight='bold', fontstyle='italic', color='black')

def plot_rscu_heatmap(data, ax, amino_acids):
    grouped_data = data.groupby('AminoAcid')
    bar_height = 0.3
    bar_width = 0.8
    x_ticks = []

    for i, (amino_acid, group) in enumerate(grouped_data):
        x_ticks.append(i)
        sorted_group = group.sort_values(by='RSCU', ascending=False)
        y_start = 0
        for j, (_, row) in enumerate(sorted_group.iterrows()):
            colors = ['#8ECFC9', '#FFBE7A', '#FA7F6F', '#82B0D2', '#8EB8DC', '#E7DAD2']
            color = colors[j % len(colors)]
            ax.bar(i, height=bar_height, width=bar_width, bottom=y_start, color=color, edgecolor='black')
            label = f'{row["Codon"]}'
            ax.text(i, y_start + 0.5 * bar_height, label, 
                ha='center', va='center', fontsize=8, 
                color='black', fontweight='bold', fontstyle='italic'
            )
            y_start += bar_height

    ax.set_xticks(x_ticks)
    ax.set_xticklabels(amino_acids)
    ax.set_xlabel('Amino Acids')
    ax.set_ylim(-0.1, y_start + 2 * bar_height)
    ax.set_xlim(-0.5, len(amino_acids) - 0.5)
    ax.set_aspect('equal')
    ax.axis('off')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = RSCUVisualizeApp()
    main_window.show()
    sys.exit(app.exec_())

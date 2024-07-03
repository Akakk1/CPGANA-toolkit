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

import sys
import pandas as pd
import numpy as np
import os
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog,
                             QMessageBox, QApplication, QComboBox, QHBoxLayout, QSpinBox, QCheckBox)


class SSRStatisticsPlotter_length(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("SSSR Barplot Generator - Length")

        layout = QVBoxLayout()
        
        # Title label
        label_title = QLabel('Plot SSR Barplot - Length')
        label_title.setFont(QFont('Arial', 16))
        layout.addWidget(label_title, alignment=Qt.AlignCenter)  
        
        # File selection
        file_layout = QHBoxLayout()

        file_label = QLabel("Select file:")
        file_layout.addWidget(file_label)

        self.file_entry = QLineEdit()
        file_layout.addWidget(self.file_entry)

        file_btn = QPushButton("Browse...")
        file_btn.clicked.connect(self.select_file)
        file_layout.addWidget(file_btn)

        layout.addLayout(file_layout)

        # Directory selection
        dir_layout = QHBoxLayout()

        dir_label = QLabel("Select output directory:")
        dir_layout.addWidget(dir_label)

        self.dir_entry = QLineEdit()
        self.dir_entry.setReadOnly(True)
        dir_layout.addWidget(self.dir_entry)

        dir_btn = QPushButton("Select Directory")
        dir_btn.clicked.connect(self.select_directory)
        dir_layout.addWidget(dir_btn)

        layout.addLayout(dir_layout)

        # DPI selection
        dpi_layout = QHBoxLayout()

        dpi_label = QLabel("Select DPI:")
        dpi_layout.addWidget(dpi_label)

        self.dpi_spinbox = QSpinBox()
        self.dpi_spinbox.setMinimum(50)
        self.dpi_spinbox.setMaximum(600)
        self.dpi_spinbox.setValue(300)
        dpi_layout.addWidget(self.dpi_spinbox)

        layout.addLayout(dpi_layout)

        # Color scheme selection
        color_layout = QHBoxLayout()

        color_label = QLabel("Select color scheme:")
        color_layout.addWidget(color_label)

        self.color_var = QComboBox()
        color_schemes = ['tab10', 'Set1', 'Set2', 'Set3', 'Pastel1', 'Pastel2', 'Paired', 'Accent', 'viridis', 'plasma']
        self.color_var.addItems(color_schemes)
        color_layout.addWidget(self.color_var)

        layout.addLayout(color_layout)

        # Font selection
        font_layout = QHBoxLayout()

        font_label = QLabel("Select font:")
        font_layout.addWidget(font_label)

        self.font_var = QComboBox()
        fonts = ['Times New Roman', 'Arial', 'Courier New', 'Calibri', 'Verdana']
        self.font_var.addItems(fonts)
        font_layout.addWidget(self.font_var)

        font_size_label = QLabel("Font size:")
        font_layout.addWidget(font_size_label)

        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setMinimum(8)
        self.font_size_spinbox.setMaximum(30)
        self.font_size_spinbox.setValue(10)
        font_layout.addWidget(self.font_size_spinbox)

        self.bold_checkbox = QCheckBox("Bold")
        font_layout.addWidget(self.bold_checkbox)

        self.italic_checkbox = QCheckBox("Italic")
        font_layout.addWidget(self.italic_checkbox)

        layout.addLayout(font_layout)

        # Plot button
        plot_btn = QPushButton("Plot Graph")
        plot_btn.clicked.connect(self.plot_graph)
        layout.addWidget(plot_btn)

        self.setLayout(layout)

    def select_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "Statistics Files (*.statistics);;All Files (*)", options=options)
        if file_path:
            self.file_entry.setText(file_path)
            self.file_path = file_path

    def select_directory(self):
        options = QFileDialog.Options()
        directory = QFileDialog.getExistingDirectory(self, "Select Directory", options=options)
        if directory:
            self.dir_entry.setText(directory)
            self.output_dir = directory

    def plot_graph(self):
        file_path = self.file_entry.text()
        if not file_path:
            QMessageBox.critical(self, "Error", "Please select a file first.")
            return

        try:
            # Read data from file
            df = pd.read_csv(file_path, sep='\t')
            df = pd.read_csv(file_path, sep='\t', usecols=lambda column: column != df.columns[-1])

            # Extract species and SSR categories
            species = df.iloc[:, 0].apply(lambda x: '\n'.join(x.split(' ')))
            categories = df.columns[1:]  # SSR types

            # Plotting parameters
            x = np.arange(len(species))
            width = 0.12

            # Color mapping
            cmap = plt.cm.get_cmap(self.color_var.currentText(), len(categories))

            # Plotting
            plt.rcParams['font.family'] = self.font_var.currentText()
            plt.rcParams['font.size'] = self.font_size_spinbox.value()
            plt.rcParams['font.weight'] = 'bold' if self.bold_checkbox.isChecked() else 'normal'
            plt.rcParams['font.style'] = 'italic' if self.italic_checkbox.isChecked() else 'normal'

            plt.figure(figsize=(16, 6))
            rects = []
            for i, category in enumerate(categories):
                rects.append(plt.bar(x - 3*width + i*width, df[category].tolist(), width=width, label=category, color=cmap(i), edgecolor='black'))
                for j, rect in enumerate(rects[i]):
                    height = rect.get_height()
                    plt.text(rect.get_x() + rect.get_width()/2., height, f'{int(height)}', ha='center', va='bottom', fontsize=8)

            plt.xticks(x, species, rotation=0)
            plt.title('Counts of Different SSR Types for Each Species')
            plt.legend(fontsize=10)
            plt.tight_layout()

            # Save the plot
            if hasattr(self, 'output_dir'):
                save_path = os.path.join(self.output_dir, "plot.png")
                plt.savefig(save_path, dpi=self.dpi_spinbox.value())
                QMessageBox.information(self, "Success", f"Plot saved successfully as {save_path}")
            else:
                QMessageBox.critical(self, "Error", "Please select an output directory first.")

            plt.show()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SSRStatisticsPlotter_length()
    window.show()
    sys.exit(app.exec_())
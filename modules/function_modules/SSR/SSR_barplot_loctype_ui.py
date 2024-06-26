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
import matplotlib.pyplot as plt
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, 
                             QMessageBox, QApplication, QComboBox, QHBoxLayout, QSpinBox)

class SSRStatisticsPlotter_loctype(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("SSR Barplot Generator - LocationType")
        
        layout = QVBoxLayout()
        
        # Title label
        label_title = QLabel('Plot SSR Barplot - LocationType')
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
        
        # Color scheme selection
        color_layout = QHBoxLayout()
        
        color_label = QLabel("Select color scheme:")
        color_layout.addWidget(color_label)
        
        self.color_var = QComboBox()
        color_schemes = ['tab10', 'Set1', 'Set2', 'Set3', 'Pastel1', 'Pastel2', 'Paired', 'Accent', 'viridis', 'plasma']
        self.color_var.addItems(color_schemes)
        color_layout.addWidget(self.color_var)
        
        layout.addLayout(color_layout)
        
        # DPI selection
        dpi_layout = QHBoxLayout()
        
        dpi_label = QLabel("Select DPI:")
        dpi_layout.addWidget(dpi_label)
        
        self.dpi_spinbox = QSpinBox()
        self.dpi_spinbox.setMinimum(50)
        self.dpi_spinbox.setMaximum(1000)
        self.dpi_spinbox.setValue(300)  # Default DPI
        dpi_layout.addWidget(self.dpi_spinbox)
        
        layout.addLayout(dpi_layout)
        
        # Save directory selection
        save_layout = QHBoxLayout()
        
        save_label = QLabel("Select save directory:")
        save_layout.addWidget(save_label)
        
        self.save_entry = QLineEdit()
        save_layout.addWidget(self.save_entry)
        
        save_btn = QPushButton("Select...")
        save_btn.clicked.connect(self.select_save_directory)
        save_layout.addWidget(save_btn)
        
        layout.addLayout(save_layout)
        
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

    def select_save_directory(self):
        options = QFileDialog.Options()
        save_directory = QFileDialog.getExistingDirectory(self, "Select Save Directory", options=options)
        if save_directory:
            self.save_entry.setText(save_directory)
            self.save_directory = save_directory

    def plot_graph(self):
        file_path = self.file_entry.text()
        if not file_path:
            QMessageBox.critical(self, "Error", "Please select a file first.")
            return
        
        save_directory = self.save_entry.text()
        if not save_directory:
            QMessageBox.critical(self, "Error", "Please select a save directory.")
            return
        
        try:
            # Read data from file
            df = pd.read_csv(file_path, sep='\t')
            
            # Extract species and SSR categories
            species = df.iloc[:, 0].apply(lambda x: '\n'.join(x.split(' ')))
            categories = df.columns[1:]  # SSR types
            
            # Get SSR counts
            counts = df.iloc[:, 1:].sum(axis=0).tolist()
            
            # Plotting parameters
            x = np.arange(len(species))
            width = 0.3
            
            # Color mapping
            cmap = plt.cm.get_cmap(self.color_var.currentText(), len(categories))
            
            # Plotting
            plt.rcParams['font.family'] = 'Times New Roman'
            plt.rcParams['font.weight'] = 'bold'
            plt.rcParams['font.style'] = 'italic'        
            plt.rcParams['font.size'] = 10
            
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
            dpi = self.dpi_spinbox.value()
            plt.savefig(f'{save_directory}/SSR_statistics_plot.png', dpi=dpi)
            
            # Show plot
            plt.show()
            
            # Show success message
            QMessageBox.information(self, "Success", f"Plot saved successfully in {save_directory}/SSR_statistics_plot.png")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SSRStatisticsPlotter_loctype()
    window.show()
    sys.exit(app.exec_())

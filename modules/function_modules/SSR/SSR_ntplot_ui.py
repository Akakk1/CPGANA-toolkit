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
import os
import pandas as pd
import numpy as np
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QFileDialog, QMessageBox, QHBoxLayout, QSizePolicy, QComboBox, QSpinBox)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class NightingaleRoseDiagramGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_file = None
        self.save_directory = None
        self.dpi = 300  # Default DPI
        self.color_var = 'viridis'  # Default color scheme
        self.font_size = 10  # Default font size
        self.font_type = 'Times New Roman'  # Default font type
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Nightingale Rose Diagram Generator')

        layout = QVBoxLayout()

        # Title label
        label_title = QLabel('Plot NTroseDiagram of SSRs')
        label_title.setFont(QFont('Arial', 16))
        layout.addWidget(label_title, alignment=Qt.AlignCenter)

        # Frame for file selection
        frame_file = QHBoxLayout()

        label_file = QLabel('Select File:')
        frame_file.addWidget(label_file)

        self.file_entry = QLineEdit()
        self.file_entry.setReadOnly(True)
        frame_file.addWidget(self.file_entry)

        button_browse = QPushButton('Browse')
        button_browse.clicked.connect(self.browse_button_click)
        frame_file.addWidget(button_browse)

        layout.addLayout(frame_file)

        # Frame for color scheme selection
        frame_color = QHBoxLayout()

        label_color = QLabel('Select color scheme:')
        frame_color.addWidget(label_color)

        self.color_menu = QComboBox()
        self.color_menu.addItems(['magma', 'Greys', 'plasma', 'inferno', 'cividis'])
        self.color_menu.currentIndexChanged.connect(self.update_color_scheme)
        frame_color.addWidget(self.color_menu)

        layout.addLayout(frame_color)

        # Frame for save directory selection and DPI input
        frame_save_options = QHBoxLayout()

        label_save_directory = QLabel('Save Directory:')
        frame_save_options.addWidget(label_save_directory)

        self.save_directory_entry = QLineEdit()
        self.save_directory_entry.setReadOnly(True)
        frame_save_options.addWidget(self.save_directory_entry)

        button_browse_directory = QPushButton('Browse')
        button_browse_directory.clicked.connect(self.browse_directory_button_click)
        frame_save_options.addWidget(button_browse_directory)

        label_dpi = QLabel('DPI:')
        frame_save_options.addWidget(label_dpi)

        self.dpi_spinbox = QSpinBox()
        self.dpi_spinbox.setMinimum(50)
        self.dpi_spinbox.setMaximum(1000)
        self.dpi_spinbox.setValue(self.dpi)
        frame_save_options.addWidget(self.dpi_spinbox)

        layout.addLayout(frame_save_options)

        # Frame for font size selection
        frame_font_size = QHBoxLayout()

        label_font_size = QLabel('Font Size:')
        frame_font_size.addWidget(label_font_size)

        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setMinimum(6)
        self.font_size_spinbox.setMaximum(30)
        self.font_size_spinbox.setValue(self.font_size)
        frame_font_size.addWidget(self.font_size_spinbox)

        layout.addLayout(frame_font_size)

        # Frame for font type selection
        frame_font_type = QHBoxLayout()

        label_font_type = QLabel('Font Type:')
        frame_font_type.addWidget(label_font_type)

        self.font_type_combobox = QComboBox()
        self.font_type_combobox.addItems(['Arial', 'Times New Roman', 'Helvetica', 'Courier', 'Verdana'])
        self.font_type_combobox.setCurrentText(self.font_type)
        frame_font_type.addWidget(self.font_type_combobox)

        layout.addLayout(frame_font_type)

        # Plot button
        button_plot = QPushButton('Plot Diagram')
        button_plot.clicked.connect(self.plot_button_click)
        layout.addWidget(button_plot, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def update_color_scheme(self, index):
        self.color_var = ['magma', 'Greys', 'plasma', 'inferno', 'cividis'][index]

    def plot_nightingale_rose_diagram(self, file_path):
        # Read the statistics file
        data = pd.read_csv(file_path, sep='\t')

        # Ensure the necessary columns exist
        if 'Species' not in data.columns or 'Total' not in data.columns:
            QMessageBox.critical(self, 'Error', 'Input file must contain "Species" and "Total" columns.')
            return

        # Sort by Total descending
        data = data.sort_values(by='Total', ascending=False).reset_index(drop=True)

        # Calculate angles for each species
        total = data['Total'].sum()
        angles = np.linspace(0, 2 * np.pi, len(data), endpoint=False).tolist()

        # Define colors dynamically based on selected color map
        colors = plt.get_cmap(self.color_var)(np.linspace(0, 1, len(data)))

        # Plot the Nightingale rose diagram
        fig, ax = plt.subplots(figsize=(8, 8), dpi=self.dpi, subplot_kw={'polar': True})

        for i, (species, total) in enumerate(zip(data['Species'], data['Total'])):
            bar = ax.bar(angles[i], total, width=angles[1] - angles[0], bottom=0.0, label=species, color=colors[i], edgecolor='black')
            # Add data label inside the bar
            ax.text(angles[i], total / 1.5, f'{total}', ha='center', va='center',
                    fontname=self.font_type, fontsize=self.font_size, fontweight='bold',
                    bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))

        # Add labels and title
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        ax.set_xticks(angles)
        ax.set_xticklabels(data['Species'], fontsize=self.font_size, fontname=self.font_type, fontweight='bold', fontstyle='italic')
        ax.set_title('', fontsize=self.font_size, fontname=self.font_type, fontweight='bold')

        # Save the plot to the output file
        if self.save_directory:
            output_file = os.path.join(self.save_directory, 'SSR_ntplot.png')
        else:
            QMessageBox.warning(self, 'Warning', 'Please select a save directory.')
            return
            
        # Adjust layout
        fig.tight_layout()
        
        fig.savefig(output_file, dpi=self.dpi)
        QMessageBox.information(self, 'Success', f'Output file has been created: {output_file}')

        # Show plot
        plt.show()

    def browse_button_click(self):
        self.selected_file, _ = QFileDialog.getOpenFileName(self, 'Select File', '', 'Statistics files (*.statistics)')
        if self.selected_file:
            self.file_entry.setText(self.selected_file)
        else:
            QMessageBox.warning(self, 'Warning', 'No file selected.')

    def browse_directory_button_click(self):
        directory = QFileDialog.getExistingDirectory(self, 'Select Directory')
        if directory:
            self.save_directory = directory
            self.save_directory_entry.setText(directory)

    def plot_button_click(self):
        if self.selected_file:
            self.dpi = self.dpi_spinbox.value()
            self.font_size = self.font_size_spinbox.value()
            self.font_type = self.font_type_combobox.currentText()
            self.plot_nightingale_rose_diagram(self.selected_file)
        else:
            QMessageBox.warning(self, 'Warning', 'Please select a file first.')


def main():
    app = QApplication(sys.argv)
    window = NightingaleRoseDiagramGUI()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

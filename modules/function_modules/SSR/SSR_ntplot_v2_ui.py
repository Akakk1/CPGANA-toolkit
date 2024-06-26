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
import pandas as pd
import numpy as np
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, \
    QPushButton, QLineEdit, QFileDialog, QMessageBox, QSpinBox
import matplotlib.pyplot as plt


class NightingaleRoseDiagramGUI_V2(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Nightingale Rose Diagram Generator V2 - Stacked')
        self.selected_file = None
        self.save_directory = None
        self.dpi = 300  # Default DPI

        # Create central widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Title label
        label_title = QLabel('Plot Stacked NTroseDiagram of SSRs')
        label_title.setFont(QFont('Arial', 16))
        layout.addWidget(label_title, alignment=Qt.AlignCenter)
        
        # File selection widgets
        file_layout = QHBoxLayout()
        file_label = QLabel('Select File:')
        file_layout.addWidget(file_label)
        self.file_entry = QLineEdit()
        self.file_entry.setReadOnly(True)
        file_layout.addWidget(self.file_entry)
        browse_button = QPushButton('Browse')
        browse_button.clicked.connect(self.browse_button_click)
        file_layout.addWidget(browse_button)
        layout.addLayout(file_layout)

        # Color scheme selection widgets
        color_layout = QHBoxLayout()
        color_label = QLabel('Select color scheme:')
        color_layout.addWidget(color_label)
        self.color_var = QComboBox()
        self.color_var.addItems(['Set1', 'Set2', 'Set3', 'tab10', 'Pastel1', 'Pastel2',
                                 'Paired', 'Accent', 'Greys', 'viridis', 'cividis', 'plasma', 'magma', 'inferno'])
        self.color_var.setCurrentText('viridis')
        color_layout.addWidget(self.color_var)
        layout.addLayout(color_layout)

        # DPI selection widgets
        dpi_layout = QHBoxLayout()
        dpi_label = QLabel('DPI:')
        dpi_layout.addWidget(dpi_label)
        self.dpi_spinbox = QSpinBox()
        self.dpi_spinbox.setMinimum(50)
        self.dpi_spinbox.setMaximum(1000)
        self.dpi_spinbox.setValue(self.dpi)
        dpi_layout.addWidget(self.dpi_spinbox)
        layout.addLayout(dpi_layout)

        # Font size selection widgets
        font_size_layout = QHBoxLayout()
        font_size_label = QLabel('Font Size:')
        font_size_layout.addWidget(font_size_label)
        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setMinimum(6)
        self.font_size_spinbox.setMaximum(30)
        self.font_size_spinbox.setValue(10)  # Default font size
        font_size_layout.addWidget(self.font_size_spinbox)
        layout.addLayout(font_size_layout)

        # Font type selection widgets
        font_type_layout = QHBoxLayout()
        font_type_label = QLabel('Font Type:')
        font_type_layout.addWidget(font_type_label)
        self.font_type_combobox = QComboBox()
        self.font_type_combobox.addItems(['Arial', 'Times New Roman', 'Helvetica', 'Courier', 'Verdana'])
        self.font_type_combobox.setCurrentText('Times New Roman')  # Default font type
        font_type_layout.addWidget(self.font_type_combobox)
        layout.addLayout(font_type_layout)

        # Save directory selection widgets
        save_layout = QHBoxLayout()
        save_label = QLabel('Select Save Directory:')
        save_layout.addWidget(save_label)
        self.save_entry = QLineEdit()
        self.save_entry.setReadOnly(True)
        save_layout.addWidget(self.save_entry)
        save_button = QPushButton('Select')
        save_button.clicked.connect(self.select_save_directory)
        save_layout.addWidget(save_button)
        layout.addLayout(save_layout)

        # Plot button
        plot_button = QPushButton('Plot Diagram')
        plot_button.clicked.connect(self.plot_button_click)
        layout.addWidget(plot_button)

    def plot_nightingale_rose_diagram(self, file_path, color_scheme, save_directory, dpi, font_size, font_type):
        # Read the statistics file
        data = pd.read_csv(file_path, sep='\t')

        # Ensure the necessary columns exist
        if 'Species' not in data.columns or 'Total' not in data.columns:
            QMessageBox.critical(self, 'Error', 'Input file must contain "Species" and "Total" columns.')
            return

        # Extract SSR types (columns between 'Species' and 'Total')
        ssr_types = data.columns[1:-1]

        # Sort by Total descending
        data = data.sort_values(by='Total', ascending=False).reset_index(drop=True)

        # Calculate angles for each species
        angles = np.linspace(0, 2 * np.pi, len(data), endpoint=False).tolist()

        # Define colors dynamically based on selected color map
        colors = plt.get_cmap(color_scheme)(np.linspace(0, 1, len(ssr_types)))

        # Plot the Nightingale rose diagram
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

        # Stack bars for each SSR type
        bottom = np.zeros(len(data))
        for i, ssr_type in enumerate(ssr_types):
            values = data[ssr_type].values
            bars = ax.bar(angles, values, width=2 * np.pi / len(data), bottom=bottom, label=ssr_type,
                          color=colors[i], edgecolor='black')
            bottom += values

        # Calculate dynamic offset for labels
        max_height = ax.get_ylim()[1]  # Get the maximum height of the bars
        offset = max_height * 0.02  # Set an offset (adjust as needed)

        # Set dynamic ylim based on max_total
        max_total = data['Total'].max()  # Get the maximum total value
        ax.set_ylim(0, max_total * 1.2)  # Adjust ylim to accommodate the maximum total

        # Add total labels for each species
        for angle, total in zip(angles, data['Total']):
            x = angle
            y = total / 1.5
            ax.text(x, y, f'{total}', ha='center', va='center', color='black',
                    fontsize=font_size, fontweight='bold', fontname=font_type,
                    bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3'))

        # Add labels and title
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        ax.set_xticks(angles)
        ax.set_xticklabels(data['Species'], fontsize=font_size, fontname=font_type, fontweight='bold',
                           fontstyle='italic')

        # Add a legend
        ax.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1))

        # Add a white background frame
        ax.set_facecolor('white')
        ax.set_frame_on(True)
        ax.patch.set_edgecolor('black')
        ax.patch.set_linewidth('1')
        # Adjust layout
        fig.tight_layout()
        # Save the plot to the output file
        output_file = os.path.join(save_directory, 'SSR_ntplot_v2.png')
        fig.savefig(output_file, dpi=dpi)
        
        QMessageBox.information(self, 'Success', f'Output file has been created: {output_file}')
        
        # Show plot
        plt.show()

    def browse_button_click(self):
        self.selected_file, _ = QFileDialog.getOpenFileName(self, 'Select File', '', 'Statistics files (*.statistics)')
        if self.selected_file:
            self.file_entry.setText(self.selected_file)
        else:
            QMessageBox.warning(self, 'Warning', 'No file selected.')

    def select_save_directory(self):
        self.save_directory = QFileDialog.getExistingDirectory(self, 'Select Save Directory')
        if self.save_directory:
            self.save_entry.setText(self.save_directory)
        else:
            QMessageBox.warning(self, 'Warning', 'No save directory selected.')

    def plot_button_click(self):
        color_scheme = self.color_var.currentText()
        dpi = self.dpi_spinbox.value()
        font_size = self.font_size_spinbox.value()
        font_type = self.font_type_combobox.currentText()

        if self.selected_file and self.save_directory:
            self.plot_nightingale_rose_diagram(self.selected_file, color_scheme, self.save_directory, dpi, font_size, font_type)
        else:
            QMessageBox.warning(self, 'Warning', 'Please select a file and save directory first.')


def main():
    app = QApplication(sys.argv)
    window = NightingaleRoseDiagramGUI_V2()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

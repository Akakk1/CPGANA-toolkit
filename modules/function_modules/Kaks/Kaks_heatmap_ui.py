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
import matplotlib.pyplot as plt
import numpy as np
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget, QFileDialog, QMessageBox, QLineEdit, QSpinBox, QHBoxLayout, QComboBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from matplotlib.colors import Normalize

class MidpointNormalize(Normalize):
    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y))

class HeatmapVisualizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Heatmap Visualizer")

        # Initialize variables
        self.file_path = None
        self.df = None
        self.output_dir = None
        self.dpi_value = 300
        self.colormap = 'coolwarm'

        self.create_widgets()

    def create_widgets(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Title label
        title_label = QLabel('Heatmap Visualizer')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont('Arial', 16))
        layout.addWidget(title_label)

        # Path text edit
        self.path_text = QLineEdit()
        self.path_text.setMaximumHeight(30)
        layout.addWidget(self.path_text)

        # Load file button
        load_button = QPushButton('Select Excel File', clicked=self.browse_file)
        layout.addWidget(load_button)

        # Options layout (directory, DPI, colormap, and plot button)
        options_layout = QHBoxLayout()

        # Directory selection
        dir_label = QLabel('Output Directory:')
        options_layout.addWidget(dir_label)

        self.dir_text = QLineEdit()
        self.dir_text.setReadOnly(True)
        options_layout.addWidget(self.dir_text)

        dir_button = QPushButton('Select Directory', clicked=self.select_directory)
        options_layout.addWidget(dir_button)

        # DPI selection
        dpi_label = QLabel('Select DPI:')
        options_layout.addWidget(dpi_label)

        self.dpi_spinbox = QSpinBox()
        self.dpi_spinbox.setMinimum(50)
        self.dpi_spinbox.setMaximum(600)
        self.dpi_spinbox.setValue(self.dpi_value)
        options_layout.addWidget(self.dpi_spinbox)

        # Colormap selection
        colormap_label = QLabel('Select Colormap:')
        options_layout.addWidget(colormap_label)

        self.colormap_combo = QComboBox()
        self.colormap_combo.addItems(['coolwarm', 'viridis', 'plasma', 'inferno', 'magma'])
        self.colormap_combo.currentTextChanged.connect(self.set_colormap)
        options_layout.addWidget(self.colormap_combo)

        # Add options layout to main layout
        layout.addLayout(options_layout)

        # Plot button
        self.plot_button = QPushButton('Plot Heatmap', clicked=self.plot_heatmap)
        self.plot_button.setEnabled(False)
        layout.addWidget(self.plot_button)

    def browse_file(self):
        options = QFileDialog.Options()
        self.file_path, _ = QFileDialog.getOpenFileName(self, "Choose Excel File", "", "Excel Files (*.xlsx *.xls)", options=options)
        if self.file_path:
            self.path_text.setText(self.file_path)
            self.enable_plot_button()

    def select_directory(self):
        options = QFileDialog.Options()
        self.output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory", options=options)
        if self.output_dir:
            self.dir_text.setText(self.output_dir)
            self.enable_plot_button()

    def enable_plot_button(self):
        if self.file_path and self.output_dir:
            self.plot_button.setEnabled(True)

    def set_colormap(self, colormap):
        self.colormap = colormap

    def plot_heatmap(self):
        if self.file_path:
            try:
                # Read Excel file
                self.df = pd.read_excel(self.file_path, index_col=0)
                df_transposed = self.df.transpose()

                # Create figure and axis
                fig, ax = plt.subplots(figsize=(30, 10))

                # Define symmetric normalization around 1
                vmin = df_transposed.min().min()
                vmax = df_transposed.max().max()
                norm = MidpointNormalize(vmin=vmin, vmax=vmax, midpoint=1)

                # Plot heatmap using pcolormesh
                mesh = ax.pcolormesh(df_transposed, cmap=self.colormap, norm=norm, edgecolors='black', linewidth=0.5)

                # Add colorbar
                plt.colorbar(mesh, ax=ax, fraction=0.03, pad=0.04)

                # Set ticks and labels
                ax.set_xticks(np.arange(len(df_transposed.columns)), minor=False)
                ax.set_yticks(np.arange(len(df_transposed.index)), minor=False)
                ax.set_xticklabels(df_transposed.columns, fontsize=16, fontweight='bold', fontname='Times New Roman', rotation=45)
                ax.set_yticklabels(df_transposed.index, fontsize=20, fontweight='bold', fontstyle='italic', fontname='Times New Roman')

                # Add gridlines
                ax.grid(which='major', color='black', linestyle='-', linewidth=1)

                # Adjust layout
                plt.tight_layout()

                # Save heatmap as PNG file with selected DPI
                if self.output_dir:
                    save_path = os.path.join(self.output_dir, 'heatmap_output.png')
                    plt.savefig(save_path, dpi=self.dpi_spinbox.value())
                    QMessageBox.information(self, "Success", f"Heatmap saved successfully as {save_path}")

                # Display plot
                plt.show()

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to plot heatmap: {str(e)}")


# Main program
if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = HeatmapVisualizerApp()
    mainWindow.show()
    sys.exit(app.exec_())

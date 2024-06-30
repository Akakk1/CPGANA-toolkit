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
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QFileDialog, QMessageBox, QSpinBox, QHBoxLayout, QComboBox
from PyQt5.QtCore import Qt
import os
from matplotlib.colors import Normalize

class MidpointNormalize(Normalize):
    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
        return np.ma.masked_array(np.interp(value, x, y))

class CHeatmapVisualizerApp(QMainWindow):
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
        title_label = QLabel('Cluster Heatmap Visualizer')
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont('Arial', 16))
        layout.addWidget(title_label)

        # Path text edit
        self.path_text = QLineEdit()
        self.path_text.setFixedHeight(30)
        layout.addWidget(self.path_text)

        # Load file button
        self.load_button = QPushButton('Choose Excel File', clicked=self.load_file)
        layout.addWidget(self.load_button)

        # Output directory selection
        output_dir_layout = QHBoxLayout()
        output_dir_label = QLabel('Output Directory:')
        output_dir_layout.addWidget(output_dir_label)

        self.dir_text = QLineEdit()
        self.dir_text.setReadOnly(True)
        output_dir_layout.addWidget(self.dir_text)

        dir_button = QPushButton('Select Directory', clicked=self.select_directory)
        output_dir_layout.addWidget(dir_button)
        layout.addLayout(output_dir_layout)

        # DPI selection
        dpi_layout = QHBoxLayout()
        dpi_label = QLabel('Select DPI:')
        dpi_layout.addWidget(dpi_label)

        self.dpi_spinbox = QSpinBox()
        self.dpi_spinbox.setMinimum(50)
        self.dpi_spinbox.setMaximum(600)
        self.dpi_spinbox.setValue(self.dpi_value)
        dpi_layout.addWidget(self.dpi_spinbox)
        layout.addLayout(dpi_layout)

        # Colormap selection
        colormap_layout = QHBoxLayout()
        colormap_label = QLabel('Select Colormap:')
        colormap_layout.addWidget(colormap_label)

        self.colormap_combo = QComboBox()
        self.colormap_combo.addItems(['coolwarm', 'viridis', 'plasma', 'inferno', 'magma'])
        self.colormap_combo.currentTextChanged.connect(self.set_colormap)
        colormap_layout.addWidget(self.colormap_combo)
        layout.addLayout(colormap_layout)

        # Plot button (initially disabled)
        self.plot_button = QPushButton('Plot Heatmap', clicked=self.plot_heatmap)
        self.plot_button.setEnabled(False)
        layout.addWidget(self.plot_button)

    def load_file(self):
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

                # Set font style
                sns.set(font='Times New Roman')
                sns.set_style('ticks')

                # Define symmetric normalization around 1
                vmin = df_transposed.min().min()
                vmax = df_transposed.max().max()
                norm = MidpointNormalize(vmin=vmin, vmax=vmax, midpoint=1)

                # Create clustermap
                cluster = sns.clustermap(df_transposed, cmap=self.colormap, norm=norm, figsize=(36, 12), linewidths=0.5, linecolor='black')

                # Adjust tick labels
                for tick_label in cluster.ax_heatmap.get_yticklabels():
                    tick_label.set_fontsize(20)
                    tick_label.set_fontname('Times New Roman')
                    tick_label.set_fontstyle('italic')
                    tick_label.set_weight('bold')
                for tick_label in cluster.ax_heatmap.get_xticklabels():
                    tick_label.set_fontsize(16)
                    tick_label.set_fontname('Times New Roman')
                    tick_label.set_weight('bold')
                    tick_label.set_rotation(45)

                # Add black spines
                for spine in cluster.ax_heatmap.spines.values():
                    spine.set_visible(True)
                    spine.set_color('black')
                    spine.set_linewidth(1)

                # Adjust layout
                plt.tight_layout()

                # Save heatmap as PNG with selected DPI
                if self.output_dir:
                    save_path = os.path.join(self.output_dir, 'cluster_heatmap_output.png')
                    plt.savefig(save_path, dpi=self.dpi_spinbox.value())
                    QMessageBox.information(self, "Success", f"Heatmap saved successfully as {save_path}")

                # Display plot
                plt.show()

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to plot heatmap: {str(e)}")

# Main program
if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = CHeatmapVisualizerApp()
    mainWindow.show()
    sys.exit(app.exec_())

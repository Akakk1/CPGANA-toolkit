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
import numpy as np
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QColorDialog, QFontDialog, QFormLayout, QComboBox, QSpinBox, QCheckBox, QLineEdit
from PyQt5.QtGui import QFont, QFontDatabase
import matplotlib.pyplot as plt

class PiplotApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Pi Plotter - Window')
        self.setGeometry(100, 100, 800, 600)

        # Default font
        self.default_font = QFont('Times New Roman', 8)
        self.default_font.setBold(True)
        self.default_font.setItalic(True)

        # Default color
        self.default_color = 'black'
        self.selected_dpi = 200  # Default DPI

        self.initUI()

    def initUI(self):
        # Widgets for selecting data file
        self.file_label = QLabel('Select Data File:')
        self.file_path_edit = QLineEdit('File: Not selected')
        self.file_button = QPushButton('Browse')
        self.file_button.clicked.connect(self.selectFile)

        # Widgets for selecting output directory
        self.output_label = QLabel('Select Output Directory:')
        self.output_dir_edit = QLineEdit('Output Directory: Not selected')
        self.output_button = QPushButton('Browse')
        self.output_button.clicked.connect(self.selectOutputDir)

        # Widgets for selecting color
        self.color_edit = QLineEdit(f'Color: {self.default_color}')
        self.color_button = QPushButton('Select Color')
        self.color_button.clicked.connect(self.selectColor)

        # Widgets for selecting font
        self.font_edit = QLineEdit(f'Font: {self.default_font.family()}, Size: {self.default_font.pointSize()}, Style: {"Bold Italic"}')
        self.font_button = QPushButton('Select Font')
        self.font_button.clicked.connect(self.selectFont)

        # Widgets for selecting chart type and DPI
        self.chart_type_label = QLabel('Select Chart Type:')
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItem('Line Chart')
        self.chart_type_combo.addItem('Bar Chart')

        # Widgets for selecting y-axis data
        self.yaxis_data_label = QLabel('Select Y-axis Data:')
        self.yaxis_data_combo = QComboBox()
        self.yaxis_data_combo.addItem('Pi')
        self.yaxis_data_combo.addItem('S')

        # Widgets for standard line
        self.standard_line_label = QLabel('Standard Line (y-axis):')
        self.standard_line_edit = QLineEdit()

        # Checkbox for default color and font
        self.default_color_checkbox = QCheckBox('Use Default Color')
        self.default_color_checkbox.setChecked(True)
        self.default_color_checkbox.stateChanged.connect(self.toggleDefaultColor)
        self.default_font_checkbox = QCheckBox('Use Default Font')
        self.default_font_checkbox.setChecked(True)
        self.default_font_checkbox.stateChanged.connect(self.toggleDefaultFont)

        # Widgets for selecting DPI
        self.dpi_label = QLabel('Select DPI:')
        self.dpi_spinbox = QSpinBox()
        self.dpi_spinbox.setMinimum(50)
        self.dpi_spinbox.setMaximum(300)
        self.dpi_spinbox.setValue(self.selected_dpi)
        self.dpi_spinbox.valueChanged.connect(self.selectDPI)
        
        # Widgets for setting figure width and height
        self.fig_width_label = QLabel('Figure Width:')
        self.fig_width_spinbox = QSpinBox()
        self.fig_width_spinbox.setMinimum(4)
        self.fig_width_spinbox.setMaximum(20)
        self.fig_width_spinbox.setValue(10)

        self.fig_height_label = QLabel('Figure Height:')
        self.fig_height_spinbox = QSpinBox()
        self.fig_height_spinbox.setMinimum(4)
        self.fig_height_spinbox.setMaximum(20)
        self.fig_height_spinbox.setValue(6)

        # Widgets for setting marker size and width
        self.marker_size_label = QLabel('Marker Size:')
        self.marker_size_spinbox = QSpinBox()
        self.marker_size_spinbox.setMinimum(1)
        self.marker_size_spinbox.setMaximum(20)
        self.marker_size_spinbox.setValue(6)

        self.marker_width_label = QLabel('Marker Width:')
        self.marker_width_spinbox = QSpinBox()
        self.marker_width_spinbox.setMinimum(1)
        self.marker_width_spinbox.setMaximum(5)
        self.marker_width_spinbox.setValue(1)
        # Button to plot chart
        self.plot_button = QPushButton('Plot Chart')
        self.plot_button.clicked.connect(self.plotChart)

        # Layout
        layout = QVBoxLayout()
        # Title label
        label_title = QLabel('Plot Pi Values by Window')
        label_title.setFont(QFont('Arial', 16))
        layout.addWidget(label_title, alignment=Qt.AlignCenter)
        # Row 1: Select Data File
        row1_layout = QHBoxLayout()
        row1_layout.addWidget(self.file_label)
        row1_layout.addWidget(self.file_path_edit)
        row1_layout.addWidget(self.file_button)
        layout.addLayout(row1_layout)

        # Row 2: Select Output Directory
        row2_layout = QHBoxLayout()
        row2_layout.addWidget(self.output_label)
        row2_layout.addWidget(self.output_dir_edit)
        row2_layout.addWidget(self.output_button)
        layout.addLayout(row2_layout)

        # Row 3: Select Color and Font
        row3_layout = QHBoxLayout()
        row3_layout.addWidget(self.color_edit)
        row3_layout.addWidget(self.color_button)
        row3_layout.addWidget(self.font_edit)
        row3_layout.addWidget(self.font_button)
        layout.addLayout(row3_layout)

        # Row 4: Select Chart Type and Y-axis Data
        row4_layout = QHBoxLayout()
        row4_layout.addWidget(self.chart_type_label)
        row4_layout.addWidget(self.chart_type_combo)
        row4_layout.addWidget(self.yaxis_data_label)
        row4_layout.addWidget(self.yaxis_data_combo)
        layout.addLayout(row4_layout)

        # Row 5: Select DPI
        row5_layout = QHBoxLayout()
        row5_layout.addWidget(self.dpi_label)
        row5_layout.addWidget(self.dpi_spinbox)
        layout.addLayout(row5_layout)

        # Row 6: Standard Line
        row6_layout = QHBoxLayout()
        row6_layout.addWidget(self.standard_line_label)
        row6_layout.addWidget(self.standard_line_edit)
        layout.addLayout(row6_layout)

        # Row 7: Default Color and Font Checkbox
        row7_layout = QHBoxLayout()
        row7_layout.addWidget(self.default_color_checkbox)
        row7_layout.addWidget(self.default_font_checkbox)
        layout.addLayout(row7_layout)

        # Row 8: Plot Chart Button
        row8_layout = QHBoxLayout()
        row8_layout.addWidget(self.plot_button)
        layout.addLayout(row8_layout)

        # Row 9: Figure Width and Height
        row9_layout = QHBoxLayout()
        row9_layout.addWidget(self.fig_width_label)
        row9_layout.addWidget(self.fig_width_spinbox)
        row9_layout.addWidget(self.fig_height_label)
        row9_layout.addWidget(self.fig_height_spinbox)
        layout.addLayout(row9_layout)

        # Main widget
        main_widget = QWidget()
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

    def selectFile(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Select Data File", "", "Text Files (*.txt)", options=options)
        if fileName:
            self.data_file = fileName
            self.file_path_edit.setText(f'File: {fileName}')

    def selectOutputDir(self):
        options = QFileDialog.Options()
        directory = QFileDialog.getExistingDirectory(self, "Select Output Directory", "", options=options)
        if directory:
            self.output_dir = directory
            self.output_dir_edit.setText(f'Output Directory: {directory}')

    def selectColor(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.selected_color = color.name()
            self.color_edit.setText(f'Color: {color.name()}')

    def selectFont(self):
        font, ok = QFontDialog.getFont(self.default_font)
        if ok:
            self.selected_font = font
            self.font_edit.setText(f'Font: {font.family()}, Size: {font.pointSize()}, Style: {self.getFontStyleString(font)}')

    def getFontStyleString(self, font):
        style = []
        if font.bold():
            style.append('Bold')
        if font.italic():
            style.append('Italic')
        return ' '.join(style)

    def toggleDefaultColor(self, state):
        if state == 2:  # Checked state
            self.color_edit.setText(f'Color: {self.default_color}')
        else:
            self.color_edit.setText('Color: Selecting...')

    def toggleDefaultFont(self, state):
        if state == 2:  # Checked state
            self.font_edit.setText(f'Font: {self.default_font.family()}, Size: {self.default_font.pointSize()}, Style: {"Bold Italic"}')
        else:
            self.font_edit.setText('Font: Selecting...')

    def selectDPI(self):
        self.selected_dpi = self.dpi_spinbox.value()

    def plotChart(self):
        try:
            data = np.genfromtxt(self.data_file, delimiter='\t', dtype=None, names=True)
            midpoints = data['Midpoint']
            y_data = data['Pi'] if self.yaxis_data_combo.currentText() == 'Pi' else data['S']

            fig_width = self.fig_width_spinbox.value()
            fig_height = self.fig_height_spinbox.value()
            marker_size = self.marker_size_spinbox.value()
            marker_width = self.marker_width_spinbox.value()

            # Create figure with specified DPI and size
            fig, ax = plt.subplots(figsize=(fig_width, fig_height), dpi=self.selected_dpi)

            if self.chart_type_combo.currentText() == 'Line Chart':
                color = self.selected_color if hasattr(self, 'selected_color') and not self.default_color_checkbox.isChecked() else self.default_color
                ax.plot(midpoints, y_data, marker='o', color=color, markersize=marker_size, markeredgewidth=marker_width)
            elif self.chart_type_combo.currentText() == 'Bar Chart':
                color = self.selected_color if hasattr(self, 'selected_color') and not self.default_color_checkbox.isChecked() else self.default_color
                ax.bar(midpoints, y_data, color=color, edgecolor='gray')

            # Add standard line if specified
            try:
                standard_line_value = float(self.standard_line_edit.text())
                ax.axhline(y=standard_line_value, color='r', linestyle='--', label=f'Standard Line: {standard_line_value}')
                ax.legend()

                # Mark points above the standard line
                above_standard = y_data > standard_line_value
                for midpoint, value in zip(midpoints[above_standard], y_data[above_standard]):
                    ax.text(midpoint, value, f'({midpoint}, {value:.5f})', ha='center', va='bottom', fontsize=4)

            except ValueError:
                pass  # No valid standard line provided

            # Customize plot
            font = self.selected_font if not self.default_font_checkbox.isChecked() else self.default_font

            # Set x-axis label
            ax.set_xlabel('Midpoints', fontsize=font.pointSize(), fontname=font.family(),
                          fontweight='bold' if font.bold() else 'normal',
                          fontstyle='italic' if font.italic() else 'normal')

            # Set y-axis label
            y_label = 'Pi Values' if self.yaxis_data_combo.currentText() == 'Pi' else 'S Values'
            ax.set_ylabel(y_label, fontsize=font.pointSize(), fontname=font.family(),
                          fontweight='bold' if font.bold() else 'normal',
                          fontstyle='italic' if font.italic() else 'normal')

            # Set x-axis tick parameters
            ax.tick_params(axis='x', labelsize=font.pointSize() - 2, rotation=0)
            for tick in ax.get_xticklabels():
                tick.set_fontsize(font.pointSize() - 2)
                tick.set_fontname(font.family())
                tick.set_fontweight('bold' if font.bold() else 'normal')
                tick.set_fontstyle('italic' if font.italic() else 'normal')

            # Set y-axis tick parameters
            ax.tick_params(axis='y', labelsize=font.pointSize() - 2)
            for tick in ax.get_yticklabels():
                tick.set_fontsize(font.pointSize() - 2)
                tick.set_fontname(font.family())
                tick.set_fontweight('bold' if font.bold() else 'normal')
                tick.set_fontstyle('italic' if font.italic() else 'normal')

            # Remove excessive whitespace from x-axis
            ax.set_xlim(midpoints[0], midpoints[-1])

            plt.grid(color='grey', linestyle='--', linewidth=0.5, axis='y')

            # Show plot
            plt.tight_layout()
            # Save plot to output directory
            if hasattr(self, 'output_dir'):
                output_file = os.path.join(self.output_dir, 'Piplot.png')
                fig.savefig(output_file, dpi=self.selected_dpi)
                QMessageBox.information(self, 'Success', f'Chart saved to:\n{output_file}')            
            plt.show()



        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Error plotting chart:\n{str(e)}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = PiplotApp()
    mainWindow.show()
    sys.exit(app.exec_())

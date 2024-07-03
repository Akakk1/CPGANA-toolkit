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
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTabWidget, QScrollArea, QSizePolicy,
                             QFileDialog, QMessageBox, QHBoxLayout, QCheckBox, QComboBox, QSpinBox, QFontDialog)
from PyQt5.QtCore import Qt                             
from PyQt5.QtGui import QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.colors import ListedColormap

class PlotSettings:
    def __init__(self):
        self.font_family = 'Arial'
        self.font_size = 12
        self.font_weight = 'normal'
        self.font_style = 'italic'
        self.color_scheme = 'tab10'
        self.show_data_labels = False
        self.data_label_font_size = 10
        self.dpi = 300
        self.width = 10
        self.height = 6
        self.legend_rows = 1
        self.legend_cols = 10
        self.legend_font_size = 8
        self.legend_position = 'upper center'
        self.switch_axis = False
        self.save_directory = ""

class SSRStatisticsStackedPlotter(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_file = None
        self.settings = PlotSettings()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("SSRCounter - Plot SSR Data")

        layout = QVBoxLayout()

        tabs = QTabWidget()
        tabs.setMinimumSize(10, 10)
        size_policy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        tabs.setSizePolicy(size_policy)        
        
        # File Tab
        file_tab = QWidget()
        file_layout = QVBoxLayout()
        frame_file = QHBoxLayout()
        label_file = QLabel("Selected File:")
        frame_file.addWidget(label_file)
        self.entry_file = QLineEdit()
        frame_file.addWidget(self.entry_file)
        button_select = QPushButton("Browse")
        button_select.clicked.connect(self.select_file)
        frame_file.addWidget(button_select)
        file_layout.addLayout(frame_file)
        file_tab.setLayout(file_layout)
        tabs.addTab(file_tab, "File")

        # Appearance Tab
        appearance_tab = QWidget()
        appearance_layout = QVBoxLayout()
        frame_font_color = QHBoxLayout()
        frame_font = QHBoxLayout()
        label_font = QLabel("Font:")
        frame_font.addWidget(label_font)
        self.display_font = QLineEdit()
        self.display_font.setReadOnly(True)
        frame_font.addWidget(self.display_font)
        button_font = QPushButton("Select")
        button_font.clicked.connect(self.select_font)
        frame_font.addWidget(button_font)
        frame_font_color.addLayout(frame_font)
        frame_combo = QHBoxLayout()
        label_combo = QLabel("Color Scheme:")
        frame_combo.addWidget(label_combo)
        self.combo_color = QComboBox()
        self.combo_color.addItems(['tab10', 'tab20', 'tab20b', 'tab20c'])
        self.combo_color.setCurrentText(self.settings.color_scheme)
        self.combo_color.currentTextChanged.connect(self.update_color_scheme)
        frame_combo.addWidget(self.combo_color)
        frame_font_color.addLayout(frame_combo)
        appearance_layout.addLayout(frame_font_color)
        appearance_tab.setLayout(appearance_layout)
        tabs.addTab(appearance_tab, "Appearance")

        # Data Labels Tab
        data_labels_tab = QWidget()
        data_labels_layout = QVBoxLayout()
        frame_switch_data_labels = QHBoxLayout()
        self.checkbox_switch_axis = QCheckBox("Switch Axis")
        self.checkbox_switch_axis.stateChanged.connect(self.update_switch_axis)
        frame_switch_data_labels.addWidget(self.checkbox_switch_axis)
        self.checkbox_data_labels = QCheckBox("Show Data Labels")
        self.checkbox_data_labels.stateChanged.connect(self.update_data_labels)
        frame_switch_data_labels.addWidget(self.checkbox_data_labels)
        label_data_label_font_size = QLabel("Data Label Font Size:")
        frame_switch_data_labels.addWidget(label_data_label_font_size)
        self.spinbox_data_label_font_size = QSpinBox()
        self.spinbox_data_label_font_size.setRange(1, 20)
        self.spinbox_data_label_font_size.setValue(self.settings.data_label_font_size)
        self.spinbox_data_label_font_size.valueChanged.connect(self.update_data_label_font_size)
        frame_switch_data_labels.addWidget(self.spinbox_data_label_font_size)
        data_labels_layout.addLayout(frame_switch_data_labels)
        data_labels_tab.setLayout(data_labels_layout)
        tabs.addTab(data_labels_tab, "Data Labels")

        # Legend Tab
        legend_tab = QWidget()
        legend_layout = QVBoxLayout()
        frame_legend = QHBoxLayout()
        label_legend_rows = QLabel("Legend Rows:")
        frame_legend.addWidget(label_legend_rows)
        self.spinbox_legend_rows = QSpinBox()
        self.spinbox_legend_rows.setRange(1, 20)
        self.spinbox_legend_rows.setValue(self.settings.legend_rows)
        self.spinbox_legend_rows.valueChanged.connect(self.update_legend_rows)
        frame_legend.addWidget(self.spinbox_legend_rows)
        label_legend_cols = QLabel("Legend Columns:")
        frame_legend.addWidget(label_legend_cols)
        self.spinbox_legend_cols = QSpinBox()
        self.spinbox_legend_cols.setRange(1, 20)
        self.spinbox_legend_cols.setValue(self.settings.legend_cols)
        self.spinbox_legend_cols.valueChanged.connect(self.update_legend_cols)
        frame_legend.addWidget(self.spinbox_legend_cols)
        label_legend_font_size = QLabel("Legend Font Size:")
        frame_legend.addWidget(label_legend_font_size)
        self.spinbox_legend_font_size = QSpinBox()
        self.spinbox_legend_font_size.setRange(1, 20)
        self.spinbox_legend_font_size.setValue(self.settings.legend_font_size)
        self.spinbox_legend_font_size.valueChanged.connect(self.update_legend_font_size)
        frame_legend.addWidget(self.spinbox_legend_font_size)
        label_legend_position = QLabel("Legend Position:")
        frame_legend.addWidget(label_legend_position)
        self.combo_legend_position = QComboBox()
        self.combo_legend_position.addItems(['upper right', 'upper left', 'lower left', 'lower right', 'upper center', 'lower center'])
        self.combo_legend_position.setCurrentText(self.settings.legend_position)
        self.combo_legend_position.currentTextChanged.connect(self.update_legend_position)
        frame_legend.addWidget(self.combo_legend_position)
        legend_layout.addLayout(frame_legend)
        legend_tab.setLayout(legend_layout)
        tabs.addTab(legend_tab, "Legend")

        # Dimensions Tab
        dimensions_tab = QWidget()
        dimensions_layout = QVBoxLayout()
        frame_dimensions = QHBoxLayout()
        label_width = QLabel("Width:")
        frame_dimensions.addWidget(label_width)
        self.spinbox_width = QSpinBox()
        self.spinbox_width.setRange(1, 2000)
        self.spinbox_width.setValue(self.settings.width)
        self.spinbox_width.valueChanged.connect(self.update_width)
        frame_dimensions.addWidget(self.spinbox_width)
        label_height = QLabel("Height:")
        frame_dimensions.addWidget(label_height)
        self.spinbox_height = QSpinBox()
        self.spinbox_height.setRange(1, 600)
        self.spinbox_height.setValue(self.settings.height)
        self.spinbox_height.valueChanged.connect(self.update_height)
        frame_dimensions.addWidget(self.spinbox_height)
        dimensions_layout.addLayout(frame_dimensions)
        dimensions_tab.setLayout(dimensions_layout)
        tabs.addTab(dimensions_tab, "Dimensions")

        # Save Directory Tab
        save_dir_tab = QWidget()
        save_dir_layout = QVBoxLayout()
        frame_save_dir = QHBoxLayout()
        self.entry_save_dir = QLineEdit()
        self.entry_save_dir.setReadOnly(True)
        frame_save_dir.addWidget(self.entry_save_dir)
        button_save_dir = QPushButton("Select Save Directory")
        button_save_dir.clicked.connect(self.select_save_directory)
        frame_save_dir.addWidget(button_save_dir)
        save_dir_layout.addLayout(frame_save_dir)
        save_dir_tab.setLayout(save_dir_layout)
        tabs.addTab(save_dir_tab, "Save Directory")

        layout.addWidget(tabs)

        # Plot Button
        button_plot = QPushButton("Plot")
        button_plot.clicked.connect(self.plot_and_save)
        layout.addWidget(button_plot)

        # Scroll Area for Image
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.canvas = FigureCanvas(plt.Figure(figsize=(self.settings.width, self.settings.height), dpi=self.settings.dpi/2))        
        self.scroll_area.setWidget(self.canvas)
        layout.addWidget(self.scroll_area)

        #Canvas Area



        self.setLayout(layout)


    def select_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Select File", "", "Text Files (*.statistics);;All Files (*)")
        if file:
            self.selected_file = file
            self.entry_file.setText(file)
            self.plot()

    def select_font(self):
        font, ok = QFontDialog.getFont()
        if ok:
            self.settings.font_family = font.family()
            self.settings.font_size = font.pointSize()
            self.settings.font_weight = 'bold' if font.bold() else 'normal'
            self.display_font.setText(f"{self.settings.font_family}, {self.settings.font_size}pt")
            self.plot()

    def update_color_scheme(self, text):
        self.settings.color_scheme = text
        self.plot()

    def update_data_labels(self, state):
        self.settings.show_data_labels = state == Qt.Checked
        self.plot()

    def update_data_label_font_size(self, value):
        self.settings.data_label_font_size = value
        self.plot()

    def update_legend_rows(self, value):
        self.settings.legend_rows = value
        self.plot()

    def update_legend_cols(self, value):
        self.settings.legend_cols = value
        self.plot()

    def update_legend_font_size(self, value):
        self.settings.legend_font_size = value
        self.plot()

    def update_legend_position(self, text):
        self.settings.legend_position = text
        self.plot()

    def update_switch_axis(self, state):
        self.settings.switch_axis = state == Qt.Checked
        self.plot()

    def update_width(self, value):
        self.settings.width = value
        self.plot()

    def update_height(self, value):
        self.settings.height = value
        self.plot()

    def select_save_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.settings.save_directory = directory
            self.entry_save_dir.setText(directory)

    def plot(self):
        if not self.selected_file:
            QMessageBox.warning(self, "Warning", "Please select a file first.")
            return

        try:
            df = pd.read_csv(self.selected_file, sep='\t', index_col=0).iloc[:, :-1]
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to read file:\n{str(e)}")
            return

        species = df.index
        columns = df.columns

        fig = self.canvas.figure
        fig.clear()

        ax_main = fig.add_subplot(111)

        cmap = plt.get_cmap(self.settings.color_scheme)
        if len(columns) > cmap.N:
            colors = [cmap(i % cmap.N) for i in range(len(columns))]
        else:
            colors = [cmap(i) for i in range(len(columns))]

        lefts = [0] * len(species)

        for i, col in enumerate(columns):
            if self.settings.switch_axis:
                ax_main.bar(species, df[col], bottom=lefts, label=col, color=colors[i], edgecolor='black')
            else:
                ax_main.barh(species, df[col], left=lefts, label=col, color=colors[i], edgecolor='black')
                
            if self.settings.show_data_labels:
                for j, value in enumerate(df[col]):
                    if value > 0:
                        if self.settings.switch_axis:
                            ax_main.text(j, lefts[j] + value / 2, str(value), ha='center', va='center', fontsize=self.settings.data_label_font_size)
                        else:
                            ax_main.text(lefts[j] + value / 2, j, str(value), ha='center', va='center', fontsize=self.settings.data_label_font_size)
                            
            lefts = [lefts[j] + df.iloc[j, df.columns.get_loc(col)] for j in range(len(species))]

        if self.settings.switch_axis:
            ax_main.set_ylabel('SSR Counts')
            ax_main.set_xlabel('Species')
            ax_main.tick_params(axis='x', rotation=20)
        else:
            ax_main.set_xlabel('SSR Counts')
            ax_main.set_ylabel('Species')
            ax_main.tick_params(axis='x')            

        font_properties = {'family': self.settings.font_family,
                           'size': self.settings.font_size,
                           'weight': self.settings.font_weight,
                           'style': self.settings.font_style}
        
        for item in ([ax_main.title, ax_main.xaxis.label, ax_main.yaxis.label] + ax_main.get_xticklabels() + ax_main.get_yticklabels()):
            plt.setp(item, **font_properties)

        ax_main.legend(loc=self.settings.legend_position, 
                       bbox_to_anchor=(0.5, 1.1), 
                       bbox_transform=ax_main.transAxes, 
                       ncol=self.settings.legend_cols, 
                       prop={'size': self.settings.legend_font_size})

        plt.tight_layout()
        self.canvas.draw()

    def plot_and_save(self):
        self.plot()

        if self.settings.save_directory:
            save_path = f"{self.settings.save_directory}/ssr_plot.png"
            self.canvas.figure.savefig(save_path, dpi=500)
            QMessageBox.information(self, "Info", f"Plot saved to {save_path}")
        else:
            QMessageBox.warning(self, "Warning", "Please select a save directory first.")

def main():
    app = QApplication(sys.argv)
    window = SSRStatisticsStackedPlotter()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
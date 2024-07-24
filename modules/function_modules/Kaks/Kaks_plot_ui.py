import sys
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QPushButton, QFileDialog, QFontDialog, QLabel, QLineEdit, QComboBox, QGridLayout, QSpinBox, QCheckBox)
import pyqtgraph as pg

class KaKsPlotterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.df = None
        self.output_dir = None

    def initUI(self):
        self.setWindowTitle('Ka/Ks Visualization Tool')
        self.setGeometry(100, 100, 100, 100)
        
        layout = QVBoxLayout()
        
        self.tabs = QTabWidget()
        self.tab_box = QWidget()
        self.tab_bar = QWidget()
        self.tab_scatter = QWidget()
        self.tab_volcano = QWidget()
        
        self.tabs.addTab(self.tab_box, "Box Plot")
        self.tabs.addTab(self.tab_bar, "Bar Plot")
        self.tabs.addTab(self.tab_scatter, "Scatter Plot")
        self.tabs.addTab(self.tab_volcano, "Volcano Plot")
        
        self.createTab(self.tab_box, self.box_plot)
        self.createTab(self.tab_bar, self.bar_plot)
        self.createTab(self.tab_scatter, self.scatter_plot)
        self.createTab(self.tab_volcano, self.volcano_plot)
        
        layout.addWidget(self.tabs)
        
        # File Loading Section
        file_layout = QHBoxLayout()
        btn_load = QPushButton('Load Data', self)
        btn_load.clicked.connect(self.loadData)
        self.file_path_display = QLineEdit(self)
        self.file_path_display.setReadOnly(True)
        file_layout.addWidget(self.file_path_display)
        file_layout.addWidget(btn_load)
        
        layout.addLayout(file_layout)

        # Plot Controls and Output Section
        control_layout = QHBoxLayout()
        
        btn_font = QPushButton('Set Global Font', self)
        btn_font.clicked.connect(self.setFont)
        control_layout.addWidget(btn_font)
        
        btn_output_dir = QPushButton('Set Output Directory', self)
        btn_output_dir.clicked.connect(self.setOutputDir)
        self.output_dir_display = QLineEdit(self)
        self.output_dir_display.setReadOnly(True)
        control_layout.addWidget(self.output_dir_display)
        control_layout.addWidget(btn_output_dir)
        
        btn_save = QPushButton('Save Plot', self)
        btn_save.clicked.connect(self.savePlot)
        control_layout.addWidget(btn_save)
        
        layout.addLayout(control_layout)
        
        self.setLayout(layout)    

    def createTab(self, tab, plot_func):
        layout = QGridLayout()

        style_label = QLabel('Style:')
        style_combo = QComboBox(self)
        style_combo.addItems(['ticks', 'white', 'whitegrid', 'dark', 'darkgrid'])
        layout.addWidget(style_label, 0, 0)
        layout.addWidget(style_combo, 0, 1)

        dpi_label = QLabel('DPI:', self)
        dpi_spinbox = QSpinBox(self)
        dpi_spinbox.setRange(72, 600)
        dpi_spinbox.setValue(100)
        layout.addWidget(dpi_label, 1, 0)
        layout.addWidget(dpi_spinbox, 1, 1)

        width_label = QLabel('Width:', self)
        width_spinbox = QSpinBox(self)
        width_spinbox.setRange(100, 2000)
        width_spinbox.setValue(800)
        layout.addWidget(width_label, 2, 0)
        layout.addWidget(width_spinbox, 2, 1)

        height_label = QLabel('Height:', self)
        height_spinbox = QSpinBox(self)
        height_spinbox.setRange(100, 2000)
        height_spinbox.setValue(600)
        layout.addWidget(height_label, 3, 0)
        layout.addWidget(height_spinbox, 3, 1)

        std_line_checkbox = QCheckBox('Show Standard Line', self)
        std_line_spinbox = QSpinBox(self)
        std_line_spinbox.setRange(0, 100)
        std_line_spinbox.setValue(1)
        layout.addWidget(std_line_checkbox, 4, 0)
        layout.addWidget(std_line_spinbox, 4, 1)

        btn_plot = QPushButton('Plot', self)
        btn_plot.clicked.connect(lambda: plot_func(style_combo.currentText(), dpi_spinbox.value(), width_spinbox.value(), height_spinbox.value(), std_line_checkbox.isChecked(), std_line_spinbox.value()))
        layout.addWidget(btn_plot, 5, 0, 1, 2)

        tab.setLayout(layout)
    
    def loadData(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Excel File", "", "Excel Files (*.xlsx);;All Files (*)", options=options)
        if fileName:
            self.df = pd.read_excel(fileName)
            self.file_path_display.setText(fileName)
    
    def setFont(self):
        font, ok = QFontDialog.getFont()
        if ok:
            plt.rcParams['font.family'] = font.family()
            plt.rcParams['font.size'] = font.pointSize()

    def setOutputDir(self):
        options = QFileDialog.Options()
        dirName = QFileDialog.getExistingDirectory(self, "Select Output Directory", options=options)
        if dirName:
            self.output_dir = dirName
            self.output_dir_display.setText(dirName)

    def savePlot(self):
        if self.output_dir:
            output_path = QFileDialog.getSaveFileName(self, "Save Plot", self.output_dir, "PNG Files (*.png);;All Files (*)")[0]
            if output_path:
                plt.savefig(output_path, pad_inches=0.1)

    def box_plot(self, style, dpi, width, height, show_std_line, std_line_value):
        if self.df is not None:
            plt.figure(figsize=(width / 100, height / 100), dpi=dpi)
            sns.set_style(style)
            sns.boxplot(x='Selection', y='Ka/Ks Mean', data=self.df)
            plt.title('Ka/Ks Ratio Distribution by Selection')
            plt.xlabel('Selection Type')
            plt.ylabel('Ka/Ks Ratio')
            plt.xticks(rotation=0)
            if show_std_line:
                plt.axhline(y=std_line_value, color='red', linestyle='--')

    def bar_plot(self, style, dpi, width, height, show_std_line, std_line_value):
        if self.df is not None:
            plt.figure(figsize=(width / 100, height / 100), dpi=dpi)
            sns.set_style(style)
            sns.barplot(x='CDS', y='Ka/Ks Mean', hue='Selection', data=self.df, edgecolor='black')
            plt.title('Ka/Ks Ratio by Gene')
            plt.xlabel('CDS')
            plt.ylabel('Ka/Ks Ratio')
            plt.xticks(rotation=90)
            if show_std_line:
                plt.axhline(y=std_line_value, color='red', linestyle='--')

    def scatter_plot(self, style, dpi, width, height, show_std_line, std_line_value):
        if self.df is not None:
            plt.figure(figsize=(width / 100, height / 100), dpi=dpi)
            sns.set_style(style)
            sns.scatterplot(x='CDS', y='Ka/Ks Mean', hue='Selection', data=self.df, style='Significant', edgecolor='black')
            plt.title('Ka/Ks Ratio by Gene')
            plt.xlabel('CDS')
            plt.ylabel('Ka/Ks Ratio')
            plt.xticks(rotation=90)
            if show_std_line:
                plt.axhline(y=std_line_value, color='red', linestyle='--')

    def volcano_plot(self, style, dpi, width, height, show_std_line, std_line_value):
        if self.df is not None:
            plt.figure(figsize=(width / 100, height / 100), dpi=dpi)
            sns.set_style(style)
            self.df['-log10(p-value)'] = -np.log10(self.df['p-value'])
            sns.scatterplot(x='Ka/Ks Mean', y='-log10(p-value)', hue='Selection', data=self.df, style='Significant', edgecolor='black')
            plt.title('Volcano Plot of Ka/Ks Ratios')
            plt.xlabel('Ka/Ks Ratio Mean')
            plt.ylabel('-log10(p-value)')
            plt.axhline(y=-np.log10(0.05), color='red', linestyle='--')
            if show_std_line:
                plt.axhline(y=std_line_value, color='red', linestyle='--')

def main():
    app = QApplication(sys.argv)
    ex = KaKsPlotterApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
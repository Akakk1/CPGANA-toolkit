import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog

def load_data(file_path):
    data = pd.read_csv(file_path, sep='\t', header=None)
    data.columns = ['AminoAcid', 'Codon', 'Number', 'RSCU']
    return data

def plot_rscu(data, ax):
    grouped_data = data.groupby('AminoAcid')
    amino_acids = list(grouped_data.groups.keys())
    x = np.arange(len(amino_acids))

    colors = ['#8ECFC9', '#FFBE7A', '#FA7F6F', '#82B0D2', '#8EB8DC', '#E7DAD2']
    color_index = 0

    for i, (amino_acid, group) in enumerate(grouped_data):
        bottom = 0
        for _, row in group.iterrows():
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
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))

def plot_rscu_heatmap(data, ax, amino_acids):
    grouped_data = data.groupby('AminoAcid')
    bar_height = 0.3
    bar_width = 0.8
    x_ticks = []

    colors = ['#8ECFC9', '#FFBE7A', '#FA7F6F', '#82B0D2', '#8EB8DC', '#E7DAD2']
    color_index = 0

    for i, (amino_acid, group) in enumerate(grouped_data):
        x_ticks.append(i)
        sorted_group = group.sort_values(by='RSCU', ascending=False)
        y_start = 0
        for j, (_, row) in enumerate(sorted_group.iterrows()):
            color = colors[color_index % len(colors)]
            color_index += 1
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

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("RSCU Visualization")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.load_button = QPushButton("Load RSCU Data")
        self.load_button.clicked.connect(self.load_data)
        self.layout.addWidget(self.load_button)

    def load_data(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open RSCU Data File", "", "Text Files (*.txt)")
        if file_path:
            data = load_data(file_path)
            self.plot_data(data)

    def plot_data(self, data):
        fig, axes = plt.subplots(2, 1, figsize=(12, 12))

        plot_rscu(data, axes[0])
        plot_rscu_heatmap(data, axes[1], data['AminoAcid'].unique())

        plt.tight_layout()
        plt.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
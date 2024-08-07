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
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QProgressBar, QMessageBox, QTextEdit
from PyQt5.QtCore import Qt, QThread, pyqtSignal

class AlignmentWorker(QThread):
    progressUpdate = pyqtSignal(int)
    message = pyqtSignal(str)

    def __init__(self, input_file, output_directory, parent=None):
        super().__init__(parent)
        self.input_file = input_file
        self.output_directory = output_directory

    def run(self):
        sequences = self.read_sequences_from_file(self.input_file)
        total_sequences = len(sequences)
        for idx, (title, seq1, seq2) in enumerate(sequences, start=1):
            aligned_seq1, aligned_seq2 = self.global_alignment(seq1, seq2)
            output_filename = f"align_{os.path.splitext(os.path.basename(self.input_file))[0]}.axt"
            output_file = os.path.join(self.output_directory, output_filename)
            self.write_alignment_to_file(title, aligned_seq1, aligned_seq2, output_file)
            progress = int((idx / total_sequences) * 100)
            self.progressUpdate.emit(progress)
        self.message.emit(f'Alignment written to {self.output_directory}')

    def global_alignment(self, seq1, seq2, match_score=1, mismatch_penalty=-1, gap_penalty=-1):
        m = len(seq1)
        n = len(seq2)

        score = [[0] * (n + 1) for _ in range(m + 1)]
        traceback = [[None] * (n + 1) for _ in range(m + 1)]

        for i in range(1, m + 1):
            score[i][0] = score[i-1][0] + gap_penalty
            traceback[i][0] = 'up'
        for j in range(1, n + 1):
            score[0][j] = score[0][j-1] + gap_penalty
            traceback[0][j] = 'left'

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i - 1] == seq2[j - 1]:
                    diagonal_score = score[i-1][j-1] + match_score
                else:
                    diagonal_score = score[i-1][j-1] + mismatch_penalty

                up_score = score[i-1][j] + gap_penalty
                left_score = score[i][j-1] + gap_penalty

                max_score = max(diagonal_score, up_score, left_score)
                score[i][j] = max_score

                if max_score == diagonal_score:
                    traceback[i][j] = 'diagonal'
                elif max_score == up_score:
                    traceback[i][j] = 'up'
                else:
                    traceback[i][j] = 'left'

        aligned_seq1 = []
        aligned_seq2 = []
        i, j = m, n

        while i > 0 or j > 0:
            if traceback[i][j] == 'diagonal':
                aligned_seq1.append(seq1[i-1])
                aligned_seq2.append(seq2[j-1])
                i -= 1
                j -= 1
            elif traceback[i][j] == 'up':
                aligned_seq1.append(seq1[i-1])
                aligned_seq2.append('-')
                i -= 1
            else:
                aligned_seq1.append('-')
                aligned_seq2.append(seq2[j-1])
                j -= 1

        aligned_seq1.reverse()
        aligned_seq2.reverse()

        return ''.join(aligned_seq1), ''.join(aligned_seq2)

    def read_sequences_from_file(self, filename):
        sequences = []
        with open(filename, 'r') as f:
            lines = f.readlines()
            i = 0
            while i < len(lines):
                title = lines[i].strip()
                if title.startswith('>'):
                    seq1 = lines[i+1].strip()
                    seq2 = lines[i+2].strip()
                    sequences.append((title, seq1, seq2))
                    i += 3
                else:
                    i += 1
        return sequences

    def write_alignment_to_file(self, title, aligned_seq1, aligned_seq2, output_file):
        with open(output_file, 'a') as f:  # Use 'a' (append) mode instead of 'w' (write)
            f.write(f"{title}\n")
            f.write(f"{aligned_seq1}\n")
            f.write(f"{aligned_seq2}\n\n")


class SimplePairwiseAlignmentApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.selectFileBtn = QPushButton('Select Sequence File', self)
        self.selectFileBtn.clicked.connect(self.selectFile)
        layout.addWidget(self.selectFileBtn)

        self.selectedFileLabel = QLabel('No file selected', self)
        layout.addWidget(self.selectedFileLabel)

        self.selectOutputBtn = QPushButton('Select Output Directory', self)
        self.selectOutputBtn.clicked.connect(self.selectOutputDirectory)
        layout.addWidget(self.selectOutputBtn)

        self.selectedOutputLabel = QLabel('No output directory selected', self)
        layout.addWidget(self.selectedOutputLabel)

        self.progressBar = QProgressBar(self)
        self.progressBar.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.progressBar)

        self.runBtn = QPushButton('Run Alignment', self)
        self.runBtn.clicked.connect(self.runAlignment)
        layout.addWidget(self.runBtn)

        self.outputTextEdit = QTextEdit(self)
        layout.addWidget(self.outputTextEdit)

        self.setLayout(layout)
        self.setWindowTitle('Sequence Aligner')
        self.setGeometry(300, 300, 600, 400)

    def selectFile(self):
        file, _ = QFileDialog.getOpenFileName(self, 'Select Sequence File', '', 'FASTA Files (*.fasta)')
        if file:
            self.selectedFile = file
            self.selectedFileLabel.setText(f'Selected: {os.path.basename(file)}')
        else:
            self.selectedFile = None
            self.selectedFileLabel.setText('No file selected')

    def selectOutputDirectory(self):
        directory = QFileDialog.getExistingDirectory(self, 'Select Output Directory')
        if directory:
            self.outputDirectory = directory
            self.selectedOutputLabel.setText(f'Output Directory: {directory}')
        else:
            self.outputDirectory = None
            self.selectedOutputLabel.setText('No output directory selected')

    def runAlignment(self):
        if not hasattr(self, 'selectedFile') or not self.selectedFile:
            QMessageBox.warning(self, 'Warning', 'Please select a sequence file')
            return
        if not hasattr(self, 'outputDirectory') or not self.outputDirectory:
            QMessageBox.warning(self, 'Warning', 'Please select output directory')
            return

        self.progressBar.setValue(0)

        # Create an instance of the worker thread
        self.worker = AlignmentWorker(self.selectedFile, self.outputDirectory, self)
        self.worker.progressUpdate.connect(self.progressBar.setValue)
        self.worker.message.connect(lambda msg: self.outputTextEdit.append(msg))

        # Start the worker thread
        self.worker.start()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SimplePairwiseAlignmentApp()
    ex.show()
    sys.exit(app.exec_())

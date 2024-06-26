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
from PyQt5.QtWidgets import QApplication, QPlainTextEdit
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt

class ConsoleOutput(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setStyleSheet("background-color: #2e2e2e; color: white;")
        font = QFont()
        font.setFamily("Courier")
        font.setPointSize(10)
        self.setFont(font)
        sys.stdout = self
        sys.stderr = self

    def write(self, message):
        self.appendPlainText(str(message))

    def flush(self):
        pass  # Override method to handle flushing of the output

if __name__ == "__main__":
    app = QApplication(sys.argv)
    console = ConsoleOutput()
    console.show()
    sys.exit(app.exec_())

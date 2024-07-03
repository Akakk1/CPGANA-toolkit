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

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QSlider, QLabel, QFileDialog, QComboBox, QApplication, QStyleFactory
from PyQt5.QtCore import Qt, QDir

class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(300, 250)

        layout = QVBoxLayout(self)

        # Choose Background Image
        self.choose_bg_button = QPushButton("Choose Background Image")
        self.choose_bg_button.clicked.connect(self.choose_background_image)
        layout.addWidget(self.choose_bg_button)

        # Adjust Opacity
        self.opacity_slider = QSlider(Qt.Horizontal)
        self.opacity_slider.setMinimum(0)
        self.opacity_slider.setMaximum(100)
        self.opacity_slider.setValue(int(parent.windowOpacity() * 100))
        self.opacity_slider.valueChanged.connect(self.change_opacity)
        layout.addWidget(self.opacity_slider)

        self.opacity_label = QLabel(f"Window Opacity: {self.opacity_slider.value() / 100:.2f}")
        layout.addWidget(self.opacity_label)

        # Select Theme
        self.theme_combobox = QComboBox()
        self.theme_combobox.addItem("Fusion")
        self.theme_combobox.addItem("Windows")
        self.theme_combobox.addItem("WindowsVista")
       #self.theme_combobox.addItem("WindowsXP")
       #self.theme_combobox.addItem("Macintosh")
       #self.theme_combobox.addItem("Plastique")        
        self.theme_combobox.currentIndexChanged.connect(self.change_theme)
        layout.addWidget(self.theme_combobox)

    def choose_background_image(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Choose Background Image", QDir.homePath(), "Images (*.png *.jpg *.jpeg *.bmp *.gif)", options=options)
        if file_name:
            self.parent().setMdiAreaBackground(file_name)

    def change_opacity(self, value):
        opacity = value / 100.0
        self.parent().setWindowOpacity(opacity)
        self.opacity_label.setText(f"Window Opacity: {opacity:.2f}")

    def change_theme(self, index):
        theme_name = self.theme_combobox.currentText()
        QApplication.instance().setStyle(QStyleFactory.create(theme_name))


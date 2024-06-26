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

from PyQt5.QtWidgets import QMdiSubWindow, QVBoxLayout, QWidget, QLineEdit, QPushButton, QHBoxLayout, QFileDialog, QMessageBox
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineDownloadItem
from PyQt5.QtCore import QUrl, Qt
import logging

class EmbeddedBrowser(QMdiSubWindow):
    def __init__(self, url):
        super().__init__()
        self.setWindowTitle(url)

        # Create the QWebEngineView
        self.web_view = QWebEngineView()
        self.web_view.setUrl(QUrl(url)) 

        # Create widgets
        self.address_bar = QLineEdit()
        self.back_button = QPushButton("Back")
        self.forward_button = QPushButton("Forward")
        self.refresh_button = QPushButton("Refresh")
        self.go_button = QPushButton("Go")  # Add "Go" button

        # Set initial URL
        self.address_bar.setText(url)

        # Connect signals
        self.address_bar.returnPressed.connect(self.navigate_to_url)
        self.go_button.clicked.connect(self.navigate_to_url)  # Connect "Go" button
        self.back_button.clicked.connect(self.web_view.back)
        self.forward_button.clicked.connect(self.web_view.forward)
        self.refresh_button.clicked.connect(self.web_view.reload)
        self.web_view.page().profile().downloadRequested.connect(self.on_download_requested)

        # Create layout for buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.back_button)
        button_layout.addWidget(self.forward_button)
        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.go_button)  # Add "Go" button
        button_layout.addStretch()

        # Create container widget
        container_widget = QWidget()
        self.setWidget(container_widget)

        # Create main layout
        layout = QVBoxLayout(container_widget)
        layout.addWidget(self.address_bar)
        layout.addLayout(button_layout)
        layout.addWidget(self.web_view)

        # Set the layout
        container_widget.setLayout(layout)

        # Enable JavaScript
        settings = self.web_view.settings()
        settings.setAttribute(settings.JavascriptEnabled, True)
        settings.setAttribute(settings.JavascriptCanOpenWindows, True)
        settings.setAttribute(settings.JavascriptCanAccessClipboard, True)

    def navigate_to_url(self):
        url = self.address_bar.text()
        self.web_view.setUrl(QUrl(url))

    def on_download_requested(self, download):
        logging.info(f"Download requested: {download.url().toString()}")

        # Show file dialog to select download directory
        options = QFileDialog.Options()
        download_path, _ = QFileDialog.getSaveFileName(self, "Save File", download.path(), options=options)

        if download_path:
            download.setPath(download_path)
            download.accept()
            logging.info(f"Download accepted: {download_path}")
            QMessageBox.information(self, "Download Started", f"Download started: {download_path}")

            # Connect to the download finished signal
            download.finished.connect(lambda: self.on_download_finished(download))
        else:
            logging.info("Download cancelled")

    def on_download_finished(self, download):
        if download.state() == QWebEngineDownloadItem.DownloadCompleted:
            QMessageBox.information(self, "Download Completed", f"Download completed: {download.path()}")
            logging.info(f"Download completed: {download.path()}")
        else:
            QMessageBox.warning(self, "Download Failed", f"Download failed: {download.path()}")
            logging.error(f"Download failed: {download.path()}")

# 在你的主程序中创建和显示 EmbeddedBrowser 的实例
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    try:
        app = QApplication(sys.argv)
        browser = EmbeddedBrowser("https://www.ncbi.nlm.nih.gov/")
        browser.show()
        app.exec_()
    except Exception as e:
        logging.critical("An unhandled exception occurred", exc_info=True)

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

from PyQt5.QtWidgets import (
    QDockWidget, QTreeView, QFileSystemModel, QAction, QMenu, QApplication,
    QMainWindow, QToolBar, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout,
    QWidget, QFileDialog, QMessageBox, QInputDialog
)
from PyQt5.QtCore import QDir, Qt, QUrl, QFileInfo, QFile
from PyQt5.QtGui import QDesktopServices
import sys
import shutil
import os


class FileExplorer(QDockWidget):
    def __init__(self, parent=None):
        super().__init__("File Explorer", parent)
        self.initUI()

    def initUI(self):
        # 初始化地址栏和工具栏
        self.path_edit = QLineEdit()
        self.path_edit.setPlaceholderText("Enter path or click browse")
        self.path_edit.returnPressed.connect(self.changeDirectory)

        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browseDirectory)

        self.up_button = QPushButton("Up")
        self.up_button.clicked.connect(self.goUpDirectory)

        toolbar = QToolBar()
        toolbar.addWidget(self.path_edit)
        toolbar.addWidget(self.browse_button)
        toolbar.addWidget(self.up_button)

        # 初始化文件浏览器视图
        self.tree_view = QTreeView()
        self.model = QFileSystemModel()
        self.model.setRootPath(QDir.rootPath())
        self.tree_view.setModel(self.model)
        self.tree_view.setRootIndex(self.model.index(QDir.rootPath()))
        self.tree_view.setSelectionMode(QTreeView.ExtendedSelection)  # 允许多选

        layout = QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.tree_view)

        container = QWidget()
        container.setLayout(layout)
        self.setWidget(container)

        # 设置 DockWidget 的属性
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        # 添加右键菜单
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.showContextMenu)

        # 创建右键菜单的动作
        self.open_action = QAction("Open", self)
        self.open_action.triggered.connect(self.openFile)

        self.rename_action = QAction("Rename", self)
        self.rename_action.triggered.connect(self.renameFile)   

        self.new_folder_action = QAction("New Folder", self)
        self.new_folder_action.triggered.connect(self.createNewFolder)

        self.copy_action = QAction("Copy", self)
        self.copy_action.triggered.connect(self.copyFile)

        self.cut_action = QAction("Cut", self)
        self.cut_action.triggered.connect(self.cutFile)

        self.paste_action = QAction("Paste", self)
        self.paste_action.triggered.connect(self.pasteFile)

        self.delete_action = QAction("Delete", self)
        self.delete_action.triggered.connect(self.deleteFile)

        self.selected_indexes = []
        self.cut_mode = False

    def showContextMenu(self, pos):
        index = self.tree_view.indexAt(pos)
        if index.isValid():
            menu = QMenu()
            menu.addAction(self.open_action)
            menu.addAction(self.rename_action)            
            menu.addAction(self.new_folder_action)
            menu.addAction(self.copy_action)
            menu.addAction(self.cut_action)
            menu.addAction(self.paste_action)  # 添加粘贴功能到右键菜单
            menu.addAction(self.delete_action)            
            menu.exec_(self.tree_view.viewport().mapToGlobal(pos))

    def openFile(self):
        try:
            indexes = self.tree_view.selectedIndexes()
            file_paths = set()

            for index in indexes:
                file_path = self.model.filePath(index)
                if QDir(file_path).exists():  # 如果是文件夹，展开文件夹
                    self.tree_view.setExpanded(index, not self.tree_view.isExpanded(index))
                else:
                    file_paths.add(file_path)

            for file_path in file_paths:
                QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
        except Exception as e:
            print(f"An error occurred: {e}")

    def deleteFile(self):
        indexes = self.tree_view.selectedIndexes()
        if not indexes:
            return
        
        reply = QMessageBox.question(self, 'Delete Files', 
                                     'Are you sure you want to delete the selected file(s) or folder(s)?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            for index in indexes:
                file_path = self.model.filePath(index)
                self.model.remove(index)
                QDir().remove(file_path)

    def createNewFolder(self):
        index = self.tree_view.currentIndex()
        if not index.isValid():
            return

        dir_path = self.model.filePath(index)
        new_folder_name, ok = QInputDialog.getText(self, 'New Folder', 
                                                   'Enter new folder name:')
        if ok and new_folder_name:
            new_folder_path = QDir(dir_path).filePath(new_folder_name)
            if QDir().mkdir(new_folder_path):
                self.model.setRootPath(QDir.rootPath())  # Refresh model
            else:
                QMessageBox.warning(self, 'Error', 
                                    f'Failed to create folder {new_folder_name}')

    def copyFile(self):
        self.selected_indexes = self.tree_view.selectedIndexes()
        self.cut_mode = False

    def cutFile(self):
        self.selected_indexes = self.tree_view.selectedIndexes()
        self.cut_mode = True
    
    def renameFile(self):
        try:
            index = self.tree_view.currentIndex()
            if not index.isValid():
                QMessageBox.warning(self, "No Selection", "Please select a file or folder to rename.")
                return

            file_path = self.model.filePath(index)
            file_info = QFileInfo(file_path)

            old_name = file_info.fileName()
            new_name, ok = QInputDialog.getText(self, "Rename", f"Enter new name for {old_name}:")
            if ok and new_name:
                new_file_path = file_info.dir().filePath(new_name)
                if file_info.isDir():
                    if QDir().rename(file_path, new_file_path):
                        QMessageBox.information(self, "Success", f"Folder renamed to {new_name}.")
                        self.model.setRootPath(self.model.rootPath())  # Refresh model
                    else:
                        QMessageBox.warning(self, "Error", "Folder could not be renamed.")
                else:
                    if QFile.rename(file_path, new_file_path):
                        QMessageBox.information(self, "Success", f"File renamed to {new_name}.")
                        self.model.setRootPath(self.model.rootPath())  # Refresh model
                    else:
                        QMessageBox.warning(self, "Error", "File could not be renamed.")
        except Exception as e:
            print(f"An error occurred in renameFile: {e}")

    def pasteFile(self):
        try:
            index = self.tree_view.currentIndex()
            if not index.isValid():
                return
            
            destination_dir = self.model.filePath(index)
            for src_index in self.selected_indexes:
                src_path = self.model.filePath(src_index)
                if self.cut_mode:
                    shutil.move(src_path, destination_dir)
                else:
                    if os.path.isdir(src_path):
                        shutil.copytree(src_path, os.path.join(destination_dir, os.path.basename(src_path)))
                    else:
                        shutil.copy(src_path, destination_dir)
            
            self.model.setRootPath(QDir.rootPath())  # Refresh model after paste
        except Exception as e:
            print(f"An error occurred in renameFile: {e}")            
    def changeDirectory(self):
        new_path = self.path_edit.text().strip()
        if QDir(new_path).exists():
            self.model.setRootPath(new_path)
            self.tree_view.setRootIndex(self.model.index(new_path))
        else:
            QMessageBox.warning(self, 'Error', 
                                f'Path {new_path} does not exist.')

    def browseDirectory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.path_edit.setText(directory)
            self.changeDirectory()

    def goUpDirectory(self):
        current_path = self.model.rootPath()
        parent_path = QDir(current_path).absolutePath()
        if parent_path != current_path:
            self.model.setRootPath(parent_path)
            self.tree_view.setRootIndex(self.model.index(parent_path))

    def toggleVisibility(self, visible):
        self.setVisible(visible)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = QMainWindow()
    dock = FileExplorer(window)
    window.addDockWidget(Qt.LeftDockWidgetArea, dock)
    window.setWindowTitle("File Explorer Demo")

    # 在主程序中添加按钮来控制文件浏览器的显示和隐藏
    toggle_button = QPushButton("Toggle File Explorer")
    toggle_button.clicked.connect(lambda: dock.toggleVisibility(not dock.isVisible()))
    window.addToolBar(Qt.TopToolBarArea, QToolBar())  # 将按钮添加到顶部工具栏

    window.show()
    sys.exit(app.exec_())

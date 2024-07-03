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

from PyQt5.QtWidgets import QMdiSubWindow

class StyledMdiSubWindow(QMdiSubWindow):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QMdiSubWindow {
                background-color: #f0f0f0;  /* Background color */
                border: 5px solid rgb(175, 175, 175);  /* Border */
                border-radius: 10px;  /* Rounded corners */
            }
            QHeaderView{
                background-color: rgba(255, 255, 255, 150);  /* Background color */
                border: 0px solid #fff;  /* Border */
                border-radius: 10px;  /* Rounded corners */
            }            
            QMdiSubWindow::close-button {
                /*icon: url(close.png); */  /* Replace 'close.png' with your close button icon */
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 16px;
                height: 16px;
                margin: 4px;
            }
            QMdiSubWindow::close-button:hover {
                background-color: #f44336;  /* Close button hover background color */
            }
            QMdiSubWindow::maximize-button {
                /*icon: url(maximize.png); */ /* Replace 'maximize.png' with your maximize button icon */
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 16px;
                height: 16px;
                margin: 4px;
            }
            QMdiSubWindow::maximize-button:hover {
                /*background-color: #2196F3; */ /* Maximize button hover background color */
            }
            QMdiSubWindow::minimize-button {
                /*icon: url(minimize.png); */ /* Replace 'minimize.png' with your minimize button icon */
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 16px;
                height: 16px;
                margin: 4px;
            }
            QMdiSubWindow::minimize-button:hover {
                background-color: #ffc107;  /* Minimize button hover background color */
            }
        """)
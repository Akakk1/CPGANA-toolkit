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

'''
BE CAREFUL! THIS PROJECT INCLUDES IMPROVED THIRD-PARTY CODE!
SEE THE BEGINNING DECLARATION OF EACH PROGRAM！
'''

import os
import sys
import logging
import threading
import subprocess
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QAction, QVBoxLayout, QWidget, QMdiArea,
    QFileDialog, QSlider, QLabel, QDialog, QPushButton, QStyleFactory, QMdiSubWindow,
    QPlainTextEdit, QDockWidget, QTreeView, QFileSystemModel, QMessageBox
)
from PyQt5.QtGui import QPixmap, QBrush
from PyQt5.QtCore import Qt, QDir, QModelIndex, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView  # Import QWebEngineView

# 创建日志文件夹
if not os.path.exists("logs"):
    os.makedirs("logs")

# 生成新的日志文件名
log_filename = os.path.join("logs", f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

# 设置日志配置
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    handlers=[logging.FileHandler(log_filename),
                              logging.StreamHandler()])

# Import your UI classes

from modules.ui_modules.FileExplorer import FileExplorer
from modules.ui_modules.SettingsDialog import SettingsDialog
from modules.ui_modules.StyledMdiSubWindow import StyledMdiSubWindow
from modules.ui_modules.ConsoleOutput import ConsoleOutput
from modules.ui_modules.EmbeddedBrowser import EmbeddedBrowser

from modules.function_modules.Sequence.Information_ui import GeneAnalysisApp
from modules.function_modules.Sequence.Region_finder_ui import RepeatFinderGUI
from modules.function_modules.Sequence.Seq_adj_ui import SequenceAdjustApp
from modules.function_modules.Sequence.Seq_reversecomplement_ui import RegionReverseApp
from modules.function_modules.Sequence.Seq_converse_ui import FileFormatConvertApp

from modules.function_modules.Align.Simple_palign_ui import SimplePairwiseAlignmentApp
from modules.function_modules.Align.Simple_palign_codon_ui import SimplePairwiseAilgnment_codon_App

from modules.function_modules.RSCU.RSCU_analysis_ui import RSCUCalculateApp
from modules.function_modules.RSCU.RSCU_plot_ui import RSCUVisualizeApp

from modules.function_modules.Extract.Extract_cgene_IGS import commongeneAndIGSExtractApp
from modules.function_modules.Extract.Extract_ccds import commoncdsExtractApp
from modules.function_modules.Extract.Extract_ac import AcExtractApp

from modules.function_modules.SSR.SSR_analysis_ui_s import SSRFindApp
from modules.function_modules.SSR.SSR_length_sta_ui import SSRCounter_lengthApp
from modules.function_modules.SSR.SSR_type_sta_ui import SSRCounter_typeApp
from modules.function_modules.SSR.SSR_loctype_sta_ui import SSRCounter_loctypeApp
from modules.function_modules.SSR.SSR_barplot_length_ui import SSRStatisticsPlotter_length
from modules.function_modules.SSR.SSR_barplot_loctype_ui import SSRStatisticsPlotter_loctype
from modules.function_modules.SSR.SSR_stackedbarplot_ui import SSRStatisticsStackedPlotter
from modules.function_modules.SSR.SSR_ntplot_ui import NightingaleRoseDiagramGUI
from modules.function_modules.SSR.SSR_ntplot_v2_ui import NightingaleRoseDiagramGUI_V2


from modules.function_modules.Pi.Pi_cal_ui import PiCalculateApp
from modules.function_modules.Pi.Pi_cal_v2_ui import PiCalculateApp_V2
from modules.function_modules.Pi.Pi_plot_ui import PiplotApp
from modules.function_modules.Pi.Pi_plot_v2_ui import PiplotApp_V2

from modules.function_modules.Kaks.Transform_ui import KaksTransformApp
from modules.function_modules.Kaks.Kaks_sta_ui import KaksStaApp
from modules.function_modules.Kaks.Kaks_filter import KaKsValueProcessor
from modules.function_modules.Kaks.Kaks_C_heatmap_ui import CHeatmapVisualizerApp
from modules.function_modules.Kaks.Kaks_heatmap_ui import HeatmapVisualizerApp

class CPGANAToolbar(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CPGANA-toolkit")

        self.background_image_path = "background.png"
        self.setupUI()
        logging.info("CPGANAToolbar initialized")

    def setupUI(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.mdi_area = QMdiArea()
        self.layout.addWidget(self.mdi_area)

        self.setMdiAreaBackground()

        self.menu_items = {
            "Sequence": {
                "Information Get": GeneAnalysisApp,
                "Region Find": RepeatFinderGUI,
                "Sequence Adjustment": SequenceAdjustApp,
                "Region Reverse Complement": RegionReverseApp,
                "Sequence Format Conversion": FileFormatConvertApp
            },
            "Extract": {
                "Extract Accession": AcExtractApp,
                "Extract Common CDS": commoncdsExtractApp,
                "Extract Common Gene and IGS": commongeneAndIGSExtractApp,
            },
#                "Align":{
#                    "PairwiseAlign": SimplePairwiseAlignmentApp,
#                    "PairwiseAlign through condon": SimplePairwiseAilgnment_codon_App
#                },    
            "SSR": {
                "SSR Finder": SSRFindApp,
                    "SSR Counter":{
                        "SSRCounter - Length": SSRCounter_lengthApp,
                        "SSRCounter - Type": SSRCounter_typeApp,                    
                        "SSRCounter - LocationType": SSRCounter_loctypeApp,
#                        "SSRCounter - Region": SSRCounter_lengthApp,
                    },
                "SSR Plotter":{
                    "SSR NTroseDiagram Generator": NightingaleRoseDiagramGUI,
                    "SSR NTroseDiagram Generator V2 - Stacked": NightingaleRoseDiagramGUI_V2,
                    "SSR Barplot Generator - Length": SSRStatisticsPlotter_length,
                    "SSR Barplot Generator - LocationType": SSRStatisticsPlotter_loctype,
                    "SSR Stacked Barplot Generator":SSRStatisticsStackedPlotter
                    }
            },
            "RSCU": {
                "RSCU Calculator": RSCUCalculateApp,
                "RSCU Plotter": RSCUVisualizeApp
            },
            "Pi": {
                "Pi Calculator":{
                    "Pi Calculator - Window": PiCalculateApp,            
                    "Pi Calculator - IGS/Gene": PiCalculateApp_V2,
                },
                "Pi Plotter":{
                    "Pi Plotter - Window": PiplotApp,                
                    "Pi Plotter - IGS/Gene": PiplotApp_V2
                }
            },
            "KaKs": {
                "Data Preprocessing":{
                    "1.Extract Common CDS": commoncdsExtractApp,
                    "2.Transform ccds to pairwise sequence": KaksTransformApp,
                    "3.PairwiseAlign through codon": SimplePairwiseAilgnment_codon_App,
                },
                "4.KaKs Calculator": "open_kaks_calculator",
                "5.KaKs Result Statistics": KaksStaApp,
                "6.KaKs Result Filter": KaKsValueProcessor,
                "KaKs Plotter":{
                    "KaKs Heatmap Plot": HeatmapVisualizerApp,
                    "KaKs Cluster Heatmap Plot": CHeatmapVisualizerApp
                }
            },
#           "Tree": {
#               "0": ModelFinder,
#               "1": Build,
#               "2": TreeAnnotate
#            },           
            "Others": {
                "NCBI": "https://www.ncbi.nlm.nih.gov/",
                "OGDraw": "https://chlorobox.mpimp-golm.mpg.de/OGDraw.html",
                "MISA": "https://webblast.ipk-gatersleben.de/misa/",
                "RePuter": "https://bibiserv.cebitec.uni-bielefeld.de/reputer",
                "IRscope": "https://irscope.shinyapps.io/irapp/",
                "MVISTA": "https://genome.lbl.gov/vista/mvista/submit.shtml",
                "iTOL": "https://itol.emblinside.de/"
            }
        }

        self._build_menus()

        # 设置初始透明度
        self.setWindowOpacity(1.0)  # 设置不透明度

        # 添加控制台窗口
        self.console_dock = QDockWidget("Console", self)
        self.console_output = ConsoleOutput()
        self.console_dock.setWidget(self.console_output)
        self.console_dock.setFloating(False)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.console_dock)

        # 添加文件浏览器
        self.file_explorer = FileExplorer(self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.file_explorer)

    def setMdiAreaBackground(self, image_path=None):
        if image_path:
            self.background_image_path = image_path

        mdi_background_image = QPixmap(self.background_image_path)
        self.mdi_area.setBackground(QBrush(mdi_background_image.scaled(self.mdi_area.size(), Qt.KeepAspectRatioByExpanding)))

    def resizeEvent(self, event):
        self.setMdiAreaBackground()

    def _build_menus(self):
        system_menu = self.menuBar().addMenu("System")

        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.open_settings_dialog)
        system_menu.addAction(settings_action)

        toggle_file_explorer_action = QAction("Toggle File Explorer", self)
        toggle_file_explorer_action.setCheckable(True)
        toggle_file_explorer_action.setChecked(True)  # 默认显示
        toggle_file_explorer_action.triggered.connect(lambda checked: self.file_explorer.toggleVisibility(checked))
        system_menu.addAction(toggle_file_explorer_action)

        toggle_console_action = QAction("Toggle Console", self)
        toggle_console_action.setCheckable(True)
        toggle_console_action.setChecked(True)  # 控制台默认显示
        toggle_console_action.triggered.connect(self.toggle_console_visibility)
        system_menu.addAction(toggle_console_action)

        close_all_action = QAction("Close All Windows", self)
        close_all_action.triggered.connect(self.close_all_sub_windows)
        system_menu.addAction(close_all_action)

        for menu_name, menu_items in self.menu_items.items():
            menu = self.menuBar().addMenu(menu_name)
            self._add_menu_items(menu, menu_items)


    def open_settings_dialog(self):
        dialog = SettingsDialog(self)
        dialog.exec_()

    def _add_menu_items(self, parent_menu, items):
        for label, target in items.items():
            if isinstance(target, dict):  # 如果目标是字典，则创建子菜单
                sub_menu = parent_menu.addMenu(label)
                self._add_menu_items(sub_menu, target)
            else:
                self._add_menu_item(parent_menu, label, target)

    def _add_menu_item(self, menu, label, target):
        action = QAction(label, self)
        if isinstance(target, str):
            if target.startswith("http"):
                action.triggered.connect(lambda: self.open_external_link_in_mdi(target))
            else:
                action.triggered.connect(lambda: self.open_subprogram(target))
        else:
            action.triggered.connect(lambda: self.open_subprogram(target))
        menu.addAction(action)

    def open_subprogram(self, script_name):
        try:
            if isinstance(script_name, str):
                if script_name.startswith("http"):
                    webbrowser.open(script_name)
                    return

                if script_name == "open_kaks_calculator":
                    exe_path = 'kaks_calculator.exe'  # 替换为实际的 .exe 文件路径
                    self.run_external_exe(exe_path)
                    return

                # 否则，根据字符串找到对应的窗口类并打开
                widget_class = self.get_widget_class(script_name)
                widget_instance = widget_class()
            else:
                widget_instance = script_name()

            sub_window = StyledMdiSubWindow()  # 使用自定义风格的子窗口
            sub_window.setWidget(widget_instance)
            sub_window.resize(200, 100)  # 设置子窗口的初始大小
            self.mdi_area.addSubWindow(sub_window)
            sub_window.show()
            logging.info(f"Opened subprogram: {script_name}")

        except Exception as e:
            self.console_output.appendPlainText(f"Failed to open script: {script_name}\n{str(e)}")
            logging.error(f"Failed to open script: {script_name}\n{str(e)}")

    def get_widget_class(self, class_name):
        return getattr(sys.modules[__name__], class_name)

    def open_external_link_in_mdi(self, url):
        try:
            browser_window = EmbeddedBrowser(url)
            self.mdi_area.addSubWindow(browser_window)
            browser_window.show()
            logging.info(f"Opened external link in MDI: {url}")
        except Exception as e:
            self.console_output.appendPlainText(f"Failed to open link: {url}\n{str(e)}")
            logging.error(f"Failed to open link: {url}\n{str(e)}")                    
            
    def open_external_exe(self):
        exe_path = 'path_to_your_external_exe.exe'  # 替换为你的外部 .exe 文件路径

        # 定义一个新线程来执行外部程序的操作
        thread = threading.Thread(target=self.run_external_exe, args=(exe_path,))
        thread.start()

    def run_external_exe(self, exe_path):
        try:
            subprocess.Popen(exe_path)
        except FileNotFoundError:
            logging.error(f"File not found: {exe_path}")
        except Exception as e:
            logging.error(f"Error running external exe: {str(e)}")

    def close_all_sub_windows(self):
        for sub_window in self.mdi_area.subWindowList():
            sub_window.close()
        logging.info("Closed all sub windows")

    def toggle_console_visibility(self, checked):
        if checked:
            self.console_dock.show()
        else:
            self.console_dock.hide()
        logging.info(f"Console visibility toggled: {'shown' if checked else 'hidden'}")

if __name__ == "__main__":
    app = QApplication([])
    # 设置全局样式，可以选择系统支持的样式之一
    app.setStyle(QStyleFactory.create("Fusion"))  # Fusion风格是Qt的跨平台样式
    mainWindow = CPGANAToolbar()

    try:
        mainWindow.show()
        logging.info("Main window shown")
        sys.exit(app.exec_())
    except Exception as e:
        logging.critical("An unhandled exception occurred", exc_info=True)

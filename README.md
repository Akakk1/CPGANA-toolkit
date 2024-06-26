# ***CPGANA-toolkit***
***Chloroplast Genome Analysis toolkit***
![CPGANA-toolkit-icon](./data/cpgana.png)

注意！本项目包含其他第三方程序！详见third-party文件夹。
Attention! This project includes other third-party programs! Please refer to the third-party folder for details.

## 目录 / Table of Contents
1. [介绍 / Introduction](#介绍--introduction)
2. [特性 / Features](#特性--features)
3. [安装 / Installation](#安装--installation)
    - [要求 / Requirements](#要求--requirements)
    - [安装 / Installation](#安装--installation)
4. [使用指南 / Usage Guide](#使用指南--usage-guide)
5. [联系 / Contact](#联系--contact)
7. [贡献 / Contributing](#贡献--contributing)
8. [许可证 / License](#许可证--license)
9. [版本历史 / Changelog](#版本历史--changelog)

## 介绍 / Introduction
叶绿体基因组学对于理解植物进化和生物多样性至关重要，但用户友好的分析工具稀缺。现有软件往往缺乏集成，阻碍了高效的数据分析和可视化。许多工具依赖于命令行界面，这对习惯于图形界面的研究人员来说是一个挑战。为了解决这些问题，我们开发了CPGANA工具包。该软件集成了叶绿体基因组分析和可视化的必要工具，并具有用户友好的图形界面，提供了一个便利的平台以加速叶绿体基因组学研究。

Chloroplast genomics is crucial for understanding plant evolution and biodiversity, yet user-friendly analysis tools are scarce. Existing software often lacks integration, hindering efficient data analysis and visualization. Many tools rely on command-line interfaces, posing challenges for researchers accustomed to graphical interfaces. To address these issues, we developed the CPGANA toolkit. This software integrates essential tools for chloroplast genome analysis and visualization, while also featuring a user-friendly graphical interface, providing a convenient platform to accelerate chloroplast genomics research.

## 特性 / Features
- 序列分析工具，如注释文件信息提取，四倍区搜索与GC含量统计，序列方向调整和简单格式转换工具。
- 简单重复序列（SSR）分析，包含长度、重复类型和位置类型的统计，支持条形图和南丁格尔玫瑰图等可视化工具。
- 相对同义密码子使用（RSCU）分析，用于计算和可视化密码子使用模式。
- 基于滑动窗口或基因间区的核苷酸多样性（Pi）计算和绘图。
- 选择压力分析工作流程，包括CDS提取、基于密码子单位的简单配对比较工具、格式转换工具和热图生成工具。
- 简单嵌入式浏览器，用于集成外部资源和在线工具，如NCBI、OGDraw和MISA。
- 可停靠的控制台输出和分层文件浏览器，提供实时反馈和便捷的数据管理。
- 用户界面具有主题和墙纸切换功能。


- Sequence analysis tools such as annotation file information extraction, tetrad region search with GC content statistics, sequence orientation adjustment, and a simple format conversion tool.
- Simple Sequence Repeat (SSR) analysis with statistics on length, repeat type, and position type, supporting visualization tools like bar charts and Nightingale rose diagrams.
- Relative Synonymous Codon Usage (RSCU) analysis for calculating and visualizing codon usage patterns.
- Nucleotide diversity (Pi) calculation and plotting based on sliding windows or intergenic regions.
- Workflow for selection pressure analysis including CDS extraction, simple pairwise comparison tool based on codon units, format conversion utilities, and heatmap generation tools.
- Simple embedded browser for integrating external resources and online tools such as NCBI, OGDraw, and MISA.
- Dockable console output and hierarchical file browser for real-time feedback and convenient data management.
- User interface with theme and wallpaper switching capabilities.

## 安装 / Installation

### 要求 / Requirements
如果你直接使用Python代码，你需要安装以下依赖：
If you are directly using Python code, you need to install the following dependencies:
- pyqt5==5.15.10
- matplotlib == 3.5.0
- seaborn==0.13.2
- Bio==1.6.2
- numpy==1.22.4
- PyQtWebEngine==5.15.6 

### 安装 / Installation
我们提供了一个release包，你可以直接下载。对于windows用户，我们还提供了exe可执行文件，使用msi进行打包安装。

We provide a release package that you can download directly. For Windows users, we also offer an executable (.exe) file packaged with MSI for installation.

## 使用指南 / Usage Guide
CPGANA-toolkit 简单易懂，不需要额外的说明，具体可以参考示例文件。
CPGANA-toolkit are straightforward and easy to understand, requiring no additional explanation. For specifics, please refer to the example files.

## 联系 / Contact
如果需要帮助，或者本项目侵犯了您的合法权益，请通过以下方式联系我们：  
If you need assistance or believe this project infringes on your legal rights, please contact us through the following channels:
- 电子邮件 / Email: `lajbaj149@gmail.com`

## 贡献 / Contributing
如果你想贡献代码或报告问题，请在 GitHub 上直接报告。  
If you want to contribute code or report issues, please report them directly on GitHub.

## 许可证 / License
该软件根据以下许可证分发：  
This software is distributed under the following license:
- [Apache License Version 2.0, January 2004](LICENSE.md)

## 版本历史 / Changelog
### 版本1.0.0 / Version 1.0.0
- 初始版本 / Initial release.

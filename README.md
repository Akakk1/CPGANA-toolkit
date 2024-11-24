# _**CPGANA-toolkit**_
###### _**Chloroplast Genome Analysis toolkit**_
![CPGANA-toolkit-icon](./data/cpgana.png)
[Read this in Chinese.](README_ZH.md)
# NOTE! This project includes third-party programs! See the third-party folder for details.
## Table of Contents
1. [Introduction](#introduction)
2. [Features](#features)
3. [Installation](#installation)
    - [Requirements](#requirements)
    - [Download and Installation](#download-and-installation)
4. [Usage Guide](#usage-guide)
5. [Contributing](#contributing)
6. [Contact](#contact)
7. [License](#license)
8. [ChangeLog](#version-history)

## Introduction
Chloroplast genomics is crucial for understanding plant evolution and biodiversity, but user-friendly analysis tools are scarce. Existing software often lacks integration, hindering efficient data analysis and visualization. Many tools rely on command-line interfaces, which can be a challenge for researchers accustomed to graphical interfaces. To address these issues, we developed the CPGANA toolkit. This software integrates essential tools for chloroplast genome analysis and visualization, offering a convenient platform to accelerate chloroplast genomics research with a user-friendly graphical interface.

## Features
- Sequence analysis tools, such as annotation file information extraction, quadruplex region search and GC content statistics, sequence orientation adjustment, and simple format conversion tools.
- Simple Sequence Repeats (SSR) analysis, including statistics on length, repeat type, and positional type, with visualization tools such as bar charts and Nightingale rose diagrams.
- Relative Synonymous Codon Usage (RSCU) analysis for calculating and visualizing codon usage patterns.
- Nucleotide diversity (Pi) calculation and plotting based on sliding windows or intergenic regions.
- A selection pressure analysis workflow, including common CDS extraction, a simple alignment tool based on codon units with multithreading, format conversion tools, and heatmap generation tools.
- A simple embedded browser for integrating external resources and online tools such as NCBI, OGDraw, and MISA.
- Dockable console output and hierarchical file browser for real-time feedback and convenient data management.
- User interface with theme and wallpaper switching functionality.

## Installation
On a "typical" desktop computer, installing the CPGANA toolkit usually takes 10-20 minutes, depending on internet speed and computer performance.

CPGANA-toolkit does not require any non-standard hardware.
### Requirements
1. **System Requirements**: Ensure your computer runs Windows 7 or later, or Ubuntu 22.04.
2. **Dependencies**: If you use Python code directly, you need to install the following dependencies:
- pyqt5==5.15.10
- matplotlib==3.5.0
- seaborn==0.13.2
- Bio==1.6.2
- numpy==1.22.4
- PyQtWebEngine==5.15.6

### Download and Installation
1. **(Recommended) Using the Windows executable (.exe)**: We use Pyinstaller to package the Python code into an .exe program and package it into an .msi for easy installation. Go to the Release page(https://github.com/Akakk1/CPGANA-toolkit/releases/tag/v1.1), download the latest version of the .msi file, which comes with a clear installation process.

_If the Release page is inaccessible or you encounter issues running the MSI file, preventing further progress, a ZIP archive containing the same files has been provided. Extract the archive and run the `CPGANAtoolkit.exe` file to start the program. Due to GitHub repository limitations, we have provided a cloud drive link._

- https://drive.google.com/file/d/1GuhE2Bn4WEcvPHdTK0PQqRkgyt61TUIb/view?usp=sharing (drive.google.com)
- https://pan.baidu.com/s/1yVgWOF1voGx4bL4ZvBLfjg?pwd=r3be (pan.baidu.com)

2. **(Not recommended) Using Python code**: Download the CPGANA toolkit code from GitHub and run it.
```bash
git clone https://github.com/Akakk1/CPGANA-toolkit.git
cd CPGANA-toolkit
```
- If using Windows:
 - Install Python 3.9.6 or a newer version.
 - Use pip to install dependencies:
	```bash
	pip install -r requirements.txt
	```
- If using Ubuntu:
 - Install Python 3.9.6 or a newer version:
	```bash
	sudo apt update
	sudo apt install python3.9
	```
 - Use pip to install dependencies:
	```bash
	pip install -r requirements.txt
    ```
- Run the software: After installation, start the CPGANA-toolkit with the following command:
```bash
python main.py
```

## Usage Guide
On a "typical" desktop computer, running a full demonstration usually takes 30 minutes, depending on the dataset size and computer performance.

This is based on a thorough reading of the user manual.

- Prepare demonstration data: Download or prepare a sample dataset ensuring its format meets CPGANA's requirements. You can use the sample data already provided in the repository.
- Run: Follow the user manual for usage.
- View results: After the demonstration runs, you can view the analysis results in the output directory.
- [User Manual](UserManual_EN.pdf)

## Contributing
If you wish to contribute code or report issues, please report directly on GitHub or contact via email.

When reporting issues, please specify at which step the problem occurred, which helps us locate the error.

## Contact
If you need help or if this project infringes on your legal rights, please contact us via:

- Email: `lajbaj149@gmail.com`

## License
This software is distributed under the following license:  
- [Apache License Version 2.0, January 2004](LICENSE.md)

## Version History
### Version 1.0.0 - 2024.6.26
- Initial release

### Version 1.1.0 - 2024.7.3
- Fixes
 - Fixed an error in calculating common gene Pi values.
- Optimizations
 - Optimized Ka/Ks plotting functionality. Added a simple linear interpolation normalization algorithm and added color scheme selection functionality.
 - Optimized Pi plotting functionality. Now can adjust the DPI value of the output image and set the length and width of the figure.
 - Optimized SSR plotting functionality. Fixed the misalignment of the bar chart and the horizontal axis. Also optimized the color mapping and interface of the stacked chart, using tabs to organize different parameters.
 - Optimized sequence alignment in the Ka/Ks workflow, using multithreading to speed up.
- Added Features
 - Added statistics and filtering functionality for KaKs results.

# Installation Guide

Follow this guide to set up and run BUMP (Basic Uptime Monitoring Program) on your system.

---

## System Requirements

Before setting up BUMP, ensure your system meets the following requirements:

- **Python Version**: 3.11 or later   
    \*This application was developed and tested exclusively with Python 3.11.9. Compatibility with other versions has not been tested and cannot be guaranteed.
- **Operating System**: Windows.    
  While BUMP may work on macOS or Linux, it was designed and tested exclusively under Windows. Functionality on other platforms is unverified and unsupported.
- **Dependencies**: All required libraries and packages are listed in `requirements.txt`. These will be installed automatically during the setup process.

---

## Installation Steps

### 1. Clone the Repository
Download the project from GitHub:
```bash
git clone https://github.com/JeanMariePrevost/bump.git
```

### 2. Set Up a Virtual Environment
Create and activate a virtual environment to manage dependencies:
```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

### 3. Install Dependencies
Install the required packages from `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 4. Verify the Setup
Run the application to verify the installation:
```bash
python src/app.py
```

You should see the BUMP interface open and an icon in your system tray.

![Dashboard](images/dashboard-empty.png){ width="600" }

---

## Pre-Bundled Executable (Optional)
If you don’t want to manage dependencies, download the pre-bundled executable version created with PyInstaller:

1. Visit the [Releases Page](https://github.com/JeanMariePrevost/bump/releases).
2. Download the executable file for your platform.
3. Run the executable to start the application.

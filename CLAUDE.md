# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This repository contains a PCB Vision Sorter application that appears to implement computer vision-based functionality for PCB board inspection and sorting. From the repository name, we can infer that the application likely includes:

- Image processing capabilities
- Automated sorting logic
- PCB defect detection features
- Material handling system integration

## Basic Setup and Operation

### Creating Virtual Environment
```bash
python -m venv .venv
```

### Activating Virtual Environment
On Windows:
```bash
.\\.venv\\Scripts\\activate
```
On macOS/Linux:
```bash
source .venv/bin/activate
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Running the Application
```bash
python main.py  # Replace 'main.py' with your entry point file
```

## Project Structure

(Please add actual file structure details when known)

Expected structure suggestions:
```
PCB_Vision_Sorter/
├── vision/            # Computer vision modules
│   ├── detection.py      # Defect detection algorithms
│   ├── processing.py     # Image preprocessing functions
│   └── classification.py # Component classification
├── hardware/          # Hardware interface modules
│   ├── io.py             # Input/output control
│   └── controller.py     # Device controller
├── config.py          # Configuration settings
├── main.py            # Main application entry point
└── requirements.txt   # Python dependencies
```

## Development Notes

### Recommended Practices
- Place all Python source code in the main directory or dedicated modules
- Use virtual environments (.venv) for dependency management
- Document hardware interfaces in hardware/ modules
- Add test images to an images/ directory for development

### Testing Guidance
To enable effective testing:
1. Create a test_images/ directory with sample PCB images
2. Add unit tests using a testing framework like pytest
3. Document testing procedures in a TESTING.md file
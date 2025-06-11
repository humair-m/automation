# automation
## OCR Automation Tools

**Current Date: 2025-06-11 13:38:13 UTC**  
**Author: [@humair-m](https://github.com/humair-m)**

## Overview

This repository contains a collection of OCR (Optical Character Recognition) automation tools that help convert PDF documents to text. The suite includes both command-line and GUI-based solutions implemented in Bash and Python.

## Tools

### 1. GUI Applications

#### OCR Studio (Python)
A modern, user-friendly GUI application for PDF to text conversion using OCR.

**Features:**
- Modern, intuitive interface
- PDF to text conversion with OCR
- Multiple language support
- Real-time progress tracking
- Configurable cleanup options
- Detailed logging system

#### Tesseract OCR GUI (Bash)
A shell-based GUI implementation using zenity for OCR processing.

**Features:**
- File selection dialogs
- Progress indicators
- Language selection
- Cleanup options
- Log file management

### 2. Command-Line Tools

#### OCR Script
A command-line tool for batch processing PDF documents.

**Features:**
- PDF to image conversion
- Multi-language OCR support
- Progress visualization
- Temporary file management
- Detailed logging

## Requirements

### Dependencies
- `tesseract-ocr`
- `poppler-utils` (for pdftoppm)
- `zenity` (for GUI shell script)
- Python 3.x (for Python GUI)
- tkinter (for Python GUI)

### Supported Languages
- English (eng)
- German (deu)
- French (fra)
- Spanish (spa)
- Italian (ita)
- Portuguese (por)
- Russian (rus)
- Chinese Simplified (chi_sim)
- Japanese (jpn)
- Korean (kor)
- Arabic (ara)
- Hindi (hin)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/humair-m/automation.git
cd automation
```

2. Install required dependencies:

For Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr poppler-utils zenity python3-tk
```

For CentOS/RHEL:
```bash
sudo yum install tesseract poppler-utils zenity python3-tkinter
```

## Usage

### Python GUI Application
```bash
python3 ocr_python.py
```

### Bash GUI Application
```bash
./tesseract_ocr_gui.sh
```

### Command Line Tool
```bash
./ocr.sh <PDF_PATH> <IMG_DIR> <OUTPUT_TEXT> [OPTIONS]
```

Options:
- `--lang=<LANG>`: Set OCR language (default: eng)
- `--cleanup`: Remove temporary images after processing
- `--log=<FILE>`: Specify log file (default: ocr_log.txt)
- `--help`: Display help message

## Logging

All tools maintain detailed logs with UTC timestamps in the format:  
`YYYY-MM-DD HH:MM:SS`

Log files contain:
- Processing steps
- Success/failure status
- Error messages
- Warning notifications

## License

This project is released under the MIT License. See the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Contact

Humair Munir - [@humair-m](https://github.com/humair-m) - humairmunirawan@gmail.com

Repository: [https://github.com/humair-m/automation](https://github.com/humair-m/automation)

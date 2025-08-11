# Semgrep CLI PDF Generator

A Python tool that generates professional PDF security reports from Semgrep CLI scan results. This tool automatically categorizes vulnerabilities by severity level and presents them in a clean, formatted PDF document.

## Features

- 🔍 **Automated Scanning**: Uses Semgrep CLI to scan your codebase for security vulnerabilities
- 📊 **Severity Classification**: Automatically categorizes findings into High, Medium, and Low severity levels
- 📄 **Professional PDF Reports**: Generates clean, formatted PDF reports with detailed vulnerability information
- 🎨 **Color-coded Severity**: Visual severity indicators in the PDF output
- ⚡ **Progress Tracking**: Real-time progress indicators during scanning

## Prerequisites

### Semgrep CLI
This tool requires Semgrep CLI to be installed on your system. Follow the official installation guide:

**macOS:**
```bash
brew install semgrep
```

**Ubuntu/Debian:**
```bash
python3 -m pip install semgrep
```

**Windows:**
```bash
pip install semgrep
```

For more installation options, visit: https://semgrep.dev/docs/getting-started/quickstart

### Python Environment
This tool has been tested on Ubuntu, macOS, and Windows. It's recommended to use a Python virtual environment:

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

## Installation

1. **Clone or download this repository**
2. **Install Python dependencies:**
   ```bash
   pip install -r requirement.txt
   ```

## Usage

### Basic Usage
```bash
python generate.py [PATH/TO/CODE] [OUTPUT_FILENAME]
```

### Examples

**Scan a JavaScript project:**
```bash
python generate.py ./my-js-project javascript-security-report.pdf
```

**Scan a Python project:**
```bash
python generate.py ./my-python-app python-vulnerabilities.pdf
```

**Scan a specific file:**
```bash
python generate.py ./src/main.py single-file-report.pdf
```

### Output

The tool generates a PDF report containing:
- **Executive Summary**: Overview of findings
- **High Severity Vulnerabilities**: Critical security issues (red-coded)
- **Medium Severity Vulnerabilities**: Important security issues (yellow-coded)
- **Low Severity Vulnerabilities**: Minor security issues (green-coded)

Each vulnerability includes:
- Category/Type
- Description
- Severity Level
- Reference information
- Affected code lines

## Sample Reports

Check the `Sample Report/` directory for example PDF outputs:
- `javascript.pdf` - Sample JavaScript security report
- `python.pdf` - Sample Python security report

## Sample Vulnerabilities

The `Sample Vulnerability/` directory contains example vulnerable code files for testing:
- `javascript.js` - JavaScript vulnerabilities
- `vuln.js` - Additional JavaScript examples
- `vuln.py` - Python vulnerabilities

## Dependencies

- **rich**: For progress indicators and enhanced terminal output
- **fpdf**: For PDF generation and formatting
- **semgrep**: For static code analysis (external dependency)

## Troubleshooting

### Common Issues

**"semgrep: command not found"**
- Ensure Semgrep CLI is properly installed and in your PATH
- Try reinstalling Semgrep CLI following the official documentation

**Permission errors**
- Make sure you have read permissions for the target directory
- On Windows, try running as administrator if needed

**PDF generation errors**
- Ensure the output directory is writable
- Check that the filename doesn't contain invalid characters

### Getting Help

If you encounter issues:
1. Verify Semgrep CLI is installed: `semgrep --version`
2. Check Python dependencies: `pip list | grep -E "(rich|fpdf)"`
3. Ensure you have proper permissions for the target directory

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## License

This project is open source. See the LICENSE file for details.

---

**Note**: This tool is designed to assist with security analysis but should not replace comprehensive security testing. Always review findings manually and consider the context of your specific application.

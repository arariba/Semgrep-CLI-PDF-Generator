# Semgrep CLI PDF Generator

A professional PDF report generator for Semgrep security scans that creates comprehensive, well-formatted security assessment reports with automatic project detection and intelligent content organization.

## 🚀 Features

### **Professional PDF Reports**
- **Executive Summary** with findings statistics
- **Color-coded severity sections** (High, Medium, Low)
- **Smart text wrapping** with optimized space utilization
- **Automatic page breaks** to prevent content splitting
- **Professional styling** with consistent typography and colors

### **Intelligent Content Handling**
- **Smart text summaries** for extremely long descriptions
- **Category optimization** to prevent unnecessary line breaks
- **Code snippet handling** with proper overflow prevention
- **Hyphen-aware text wrapping** for technical terms

### **Automatic Project Detection**
- **Project name extraction** from directory paths
- **Personalized report content** with project-specific information
- **Automatic output organization** in structured directories
- **Timestamped filenames** for version tracking

### **User Experience**
- **Optional output filenames** with smart defaults
- **Progress indicators** during scanning
- **Clear error messages** and usage instructions
- **Cross-platform compatibility**

## 📋 Requirements

- Python 3.7+
- Semgrep CLI installed and accessible
- Required Python packages (see `requirements.txt`)

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd Semgrep-CLI-PDF-Generator
   ```

2. **Create virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify Semgrep CLI:**
   ```bash
   semgrep --version
   ```

## 🎯 Usage

### **Basic Usage (Recommended)**
```bash
# Generate report with automatic filename and organization
python3 generate.py /path/to/your/project/

# Example
python3 generate.py /Users/username/projects/my-app/
```

### **Custom Output Filename**
```bash
# Specify custom output filename
python3 generate.py /path/to/your/project/ custom-report.pdf

# Example
python3 generate.py /Users/username/projects/my-app/ security-audit.pdf
```

### **Output Structure**
When using automatic filenames, reports are organized as:
```
report/
├── my-app/
│   ├── my-app-202412151430.pdf
│   ├── my-app-202412151445.pdf
│   └── my-app-202412151500.pdf
├── another-project/
│   └── another-project-202412151435.pdf
```

## 📊 Report Structure

### **1. Header Section**
- Company/Project branding
- Generation timestamp
- Professional styling

### **2. Executive Summary**
- Project name and scan statistics
- Total findings count
- Breakdown by severity level
- Professional summary table

### **3. Scan Summary**
- Project-specific scan information
- Scan results overview

### **4. Findings Sections**
- **High Severity** (Red accent)
- **Medium Severity** (Orange accent)
- **Low Severity** (Green accent)

### **5. Conclusion & Recommendations**
- Priority-based action items
- Security best practices
- Next steps for remediation

## 🔧 Advanced Features

### **Smart Text Handling**
- **Long descriptions**: Automatically summarized for readability
- **Category fields**: Optimized to prevent line breaks at hyphens
- **Code snippets**: Limited to prevent cell overflow
- **Text wrapping**: Intelligent line breaks with 85-95% space utilization

### **Layout Optimization**
- **Page break prevention**: Content never splits across pages
- **Dynamic cell heights**: Automatically adjusts to content
- **Professional margins**: Consistent spacing and boundaries
- **Color-coded sections**: Visual severity indicators

### **Project Intelligence**
- **Automatic naming**: Extracts project name from path
- **Path normalization**: Handles trailing slashes automatically
- **Relative paths**: Shows clean file paths in reports
- **Timestamp tracking**: Unique filenames for each scan

## 📁 File Structure

```
Semgrep-CLI-PDF-Generator/
├── generate.py              # Main script
├── requirements.txt         # Python dependencies
├── README.md               # This file
├── LICENSE                 # License information
├── report/                 # Generated reports (auto-created)
│   ├── project1/
│   └── project2/
└── Sample Vulnerability/   # Example files for testing
    ├── javascript.js
    ├── vuln.js
    └── vuln.py
```

## 🎨 Customization

### **Modifying Report Styling**
Edit the `generate.py` file to customize:
- Colors and fonts
- Header/footer content
- Section layouts
- Text formatting

### **Adjusting Text Wrapping**
Modify the character width calculation:
```python
# Current setting (aggressive space utilization)
chars_per_line = int(max_width / 1.7)

# For more conservative wrapping
chars_per_line = int(max_width / 2.0)
```

## 🚨 Troubleshooting

### **Common Issues**

1. **Semgrep not found:**
   ```bash
   # Install Semgrep CLI
   pip install semgrep
   # or
   brew install semgrep  # macOS
   ```

2. **Permission errors:**
   ```bash
   # Ensure write permissions to report directory
   chmod 755 report/
   ```

3. **Unicode errors:**
   - All text is now Latin-1 compatible
   - No special characters that could cause encoding issues

### **Debug Mode**
Add verbose output by modifying the scan function:
```python
print(f"Scanning directory: {path}")
print(f"Command: {command}")
```

## 📈 Performance

- **Fast scanning**: Direct directory access
- **Efficient PDF generation**: Optimized text handling
- **Memory management**: Streamlined content processing
- **Cross-platform**: Works on Windows, macOS, and Linux

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Semgrep** for the excellent security scanning tool
- **FPDF** for PDF generation capabilities
- **Rich** for beautiful progress indicators

## 📞 Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check the troubleshooting section
- Review the code comments for implementation details

---

**Happy Security Scanning! 🔒**

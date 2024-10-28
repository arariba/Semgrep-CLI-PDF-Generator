# Semgrep-CLI-PDF-Generator

This script has been tested on Ubuntu. Theoretically, it should be able to run on Windows and Mac as it is just a Python script.

First and foremost it is recommended to run it in a Python virtual environment
```
python -m venv venv
souce venv/bin/active
```

## Requirements

This code depends on Semgrep CLI, you can install Semgrep CLI following the steps in the websites
```
https://semgrep.dev/docs/getting-started/quickstart
```

Install the python required library
```
pip install -r requirement.txt
```

## Usage
The script will need the path and output filename 
```
python generate.py [PATH] [OUTPUT_NAME]
```

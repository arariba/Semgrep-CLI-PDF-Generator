# Semgrep-CLI-PDF-Generator
Automatically generate a pdf report from Semgrep CLI in Python.

This script have been tested on Ubuntu. Theoretically it should be able to run on Windows nad Mac as it just a python script.

First and foremost it is recommended to run it in a python virtual environment
```
python -m venv venv
souce venv/bin/active
```

## Requirements

This code depend on semgrep cli, you can install semgrep cli following the step in the websites
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

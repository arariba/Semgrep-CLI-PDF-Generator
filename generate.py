import subprocess
import sys
import re
from rich.progress import SpinnerColumn, Progress, TextColumn
from fpdf import FPDF

class Findings:
    def __init__(self, category, description, reference, code):
        self.category = category
        self.description = description
        self.reference = reference
        self.code = code

class PDF(FPDF):
    def header(self):
        self.set_font('Arial','BI' , size=8)
        # Title
        self.cell(30, 10, border=0, txt='Static Application Security Testing Report', align='L')
        # Line break
        self.ln(20)

    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Arial italic 8
        self.set_font('Arial', size=8)
        # Page number
        self.cell(0, 10, 'Page|' + str(self.page_no()), 0, 0, 'R')

    # Clean latin-1
    def clean_text(self, text):
        return text.encode("latin-1", "ignore").decode("latin-1")

    # Old code, to write the findings directly not in a table format
    # def write_findings(self, findings,type):
    #     if findings:
    #         self.multi_cell(200, 10, txt= type + " Severity Level")
    #         for finding in findings:
    #             self.multi_cell(200, 10, txt="Category: " + self.clean_text(str(finding.category)))
    #             self.multi_cell(200, 10, txt="Description: " + self.clean_text(str(finding.description))) 
    #             self.multi_cell(200, 10, txt="Reference: " + self.clean_text(str(finding.reference)))
    #             self.multi_cell(200, 10, txt="Affected Lines: " + self.clean_text(str(finding.code)))
    #             self.ln(1)

    # Function to create and write table
    def create_table(self,text, data, is_severity=False):
        self.set_font('Arial', '', 10)
        self.set_fill_color(255, 255, 255)

        if is_severity:
            if data == "High":
                self.set_fill_color(255, 204, 204)
            elif data == "Medium":
                self.set_fill_color(255, 255, 204)
            elif data == "Low":
                self.set_fill_color(204, 255, 204)
        self.cell(40, 10, text, 1)
        self.cell(160, 10, data, 1, fill=True)
        self.ln()

    # The function to iterate through the available findings and write to data
    def write_to_table(self, findings, type):
        col_width = 50
        if findings:
            for finding in findings:
                self.create_table("Category",self.clean_text(str(finding.category)))
                self.create_table("Description",self.clean_text(str(finding.description)))
                self.create_table("Severity Level", type, is_severity=True)
                self.create_table("Reference",self.clean_text(str(finding.reference)))
                self.create_table("Affected Lines",self.clean_text(str(finding.code)))
                self.ln()


# Scan the code for vulnerability using semgrep cli
def scan(path):
    command = "semgrep scan " + path
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
    ) as progress:
        task = progress.add_task("Scanning...", total=None)  
        
        # Run the subprocess command
        result = subprocess.run(command, capture_output=True, text=True, shell=True)

        progress.update(task, completed=1) 
        progress.update(task, description="Done")  
    return result.stdout

# Check for system arguments and extract the path
def check_sysarg():
    if len(sys.argv) != 3:
        print("Usage: python generate.py [PATH] [OUTPUT_NAME]")
        exit()

    path = sys.argv[1]
    filename = sys.argv[2]
    return path, filename

# Combine the description
def clean_description(messages):
    combined_messages = []
    temp = ""

    for message in messages[5:]:
        if message: 
            if temp:  
                temp += " " + message.strip()  
            else:
                temp = message.strip()  
        else:
            if temp: 
                combined_messages.append(temp)
                temp = ""  
    if temp:
        combined_messages.append(temp)
    return combined_messages

# Seperate the findings according to the severity level
def categorize_finding(lines):
    lines = lines.strip().split('\n')

    category = []  
    description = []  
    reference = [] 
    code_lines = []  

    for line in lines:
        stripped_line = line.strip()  

        if stripped_line.startswith('❯❱') or stripped_line.startswith('❱') or stripped_line.startswith('❯❯❱'):
            category.append(stripped_line)  
        elif stripped_line.lower().startswith('details:'):
            reference.append(stripped_line) 
        elif 'Details:' in stripped_line:
            continue
        elif '┆' in stripped_line:
            code_lines.append(stripped_line)  
        else:
            description.append(stripped_line)  

    return category, description, reference, code_lines

# Store the categorize findings to the class findings
def store_finding(category_deciders, descriptions, references, codes):
    high_findings = []
    medium_findings = []
    low_findings = []

    for i in range(len(category_deciders)): 
        category_decider = category_deciders[i]
        description = descriptions[i]
        reference = references[i]
        code = codes[i]

        if category_decider.startswith('❯❯❱'):
            category = "high"
            findings_list = high_findings
            
        elif category_decider.startswith('❯❱'):
            category = "medium"
            findings_list = medium_findings

        elif category_decider.startswith('❱'):
            category = "low"
            findings_list = low_findings

        else:
            continue 

        category_decider = category_decider.replace('❯❯❱', '').replace('❯❱', '').replace('❱', '').strip()
        code = code.replace('┆', '').strip()
        reference = reference.replace('Details:', '').strip()
        finding_instance = Findings(category_decider, description, reference, code)
        findings_list.append(finding_instance)

    return high_findings, medium_findings, low_findings

# Write to PDF
def generate_pdf_report(high, medium, low, filename):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    #Add title
    pdf.set_font("Arial", style="B", size=18)
    pdf.multi_cell(200, 10, txt="Semgrep Report")

    pdf.set_font("Arial", size=10)
    pdf.multi_cell(200,10,findings[0])
    pdf.ln(3)

    pdf.write_to_table(high,"High")
    pdf.ln()
    pdf.write_to_table(medium,"Medium")
    pdf.ln()
    pdf.write_to_table(low,"Low")

    # Save the PDF to a file
    pdf.output(filename)

if __name__ == "__main__":
    path,filename = check_sysarg()
    findings = scan(path)
    category, description, reference, code = categorize_finding(findings)
    description = clean_description(description)
    high ,medium, low = store_finding(category,description,reference,code)

    generate_pdf_report(high, medium, low, filename)
    
    

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

    # Handle long text by truncating if necessary
    def truncate_text(self, text, max_length=150):
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."

    # Calculate the height needed for text in a given width
    def calculate_text_height(self, text, width, line_height=10):
        # More accurate calculation of lines needed
        # Arial 10pt font: approximately 2.5 units per character
        chars_per_line = int(width / 2.5)
        
        if len(text) <= chars_per_line:
            return line_height
        
        # Count actual line breaks in text
        lines = text.split('\n')
        total_lines = 0
        
        for line in lines:
            if len(line) <= chars_per_line:
                total_lines += 1
            else:
                # Calculate how many lines this long line needs
                total_lines += max(1, (len(line) // chars_per_line) + 1)
        
        return total_lines * line_height

    # Check if there's enough space on the current page for a table row
    def check_page_break(self, required_height):
        # Get current Y position and page height
        current_y = self.get_y()
        page_height = self.h
        margin = 15  # Bottom margin
        
        # Check if adding the required height would exceed the page
        if current_y + required_height > page_height - margin:
            return True  # Need page break
        return False  # Enough space

    # Check if there's enough space for a section header
    def check_header_space(self, header_height=15):
        return self.check_page_break(header_height)

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
        
        # Truncate very long text to prevent layout issues
        display_data = self.truncate_text(str(data))
        
        # Calculate the actual height needed for the data text
        line_height = 10
        data_height = self.calculate_text_height(display_data, 160, line_height)
        
        # Check if we need a page break to keep the table row together
        if self.check_page_break(data_height):
            self.add_page()
        
        # Store current x position
        x_pos = self.get_x()
        y_pos = self.get_y()
        
        # First column (label) - use same height as data column
        self.cell(40, data_height, text, 1)
        
        # Second column (data) - use multi_cell for automatic text wrapping
        self.set_xy(x_pos + 40, y_pos)
        self.multi_cell(160, line_height, display_data, 1, fill=True)
        
        # Move to next line - the multi_cell already handles positioning
        # No need for additional ln() as multi_cell moves to the next row

    # The function to iterate through the available findings and write to data
    def write_to_table(self, findings, type):
        col_width = 50
        if findings:
            for i, finding in enumerate(findings):
                # Calculate total height needed for this finding
                total_height = 0
                total_height += self.calculate_text_height(str(finding.category), 160, 10)
                total_height += self.calculate_text_height(str(finding.description), 160, 10)
                total_height += 10  # Severity level row (fixed height)
                total_height += self.calculate_text_height(str(finding.reference), 160, 10)
                total_height += self.calculate_text_height(str(finding.code), 160, 10)
                total_height += 15  # Add spacing between rows
                
                # Check if we need a page break to keep the entire finding together
                if self.check_page_break(total_height):
                    self.add_page()
                
                self.create_table("Category",self.clean_text(str(finding.category)))
                self.create_table("Description",self.clean_text(str(finding.description)))
                self.create_table("Severity Level", type, is_severity=True)
                self.create_table("Reference",self.clean_text(str(finding.reference)))
                self.create_table("Affected Lines",self.clean_text(str(finding.code)))
                
                # Add consistent spacing between findings
                if i < len(findings) - 1:
                    self.ln(3)
                else:
                    self.ln(2)


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
    pdf.ln(5)

    # Add summary section
    # Check if there's enough space for the summary header
    if pdf.check_header_space(20):  # Summary needs more space
        pdf.add_page()
    pdf.set_font("Arial", style="B", size=12)
    pdf.multi_cell(200, 10, txt="Scan Summary")
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(200, 10, findings[0])
    pdf.ln(5)

    # High severity findings
    if high:
        # Check if there's enough space for the header
        if pdf.check_header_space():
            pdf.add_page()
        pdf.set_font("Arial", style="B", size=12)
        pdf.multi_cell(200, 10, txt="High Severity Findings")
        pdf.set_font("Arial", size=10)
        pdf.write_to_table(high,"High")
        pdf.ln(3)

    # Medium severity findings
    if medium:
        # Check if there's enough space for the header
        if pdf.check_header_space():
            pdf.add_page()
        pdf.set_font("Arial", style="B", size=12)
        pdf.multi_cell(200, 10, txt="Medium Severity Findings")
        pdf.set_font("Arial", size=10)
        pdf.write_to_table(medium,"Medium")
        pdf.ln(3)

    # Low severity findings
    if low:
        # Check if there's enough space for the header
        if pdf.check_header_space():
            pdf.add_page()
        pdf.set_font("Arial", style="B", size=12)
        pdf.multi_cell(200, 10, txt="Low Severity Findings")
        pdf.set_font("Arial", size=10)
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
    
    

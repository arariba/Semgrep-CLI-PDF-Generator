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
    def __init__(self):
        super().__init__()
        # Set proper page margins
        self.set_margins(20, 20, 20)  # Left, Top, Right margins
        self.set_auto_page_break(auto=True, margin=25)  # Bottom margin
    
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

    # Handle long text by truncating based on available height
    def truncate_text_by_height(self, text, max_width, max_height, line_height=10):
        # Calculate how many lines we can fit
        max_lines = int(max_height / line_height)
        chars_per_line = int(max_width / 2.5)
        
        # If text fits in one line, return as is
        if len(text) <= chars_per_line:
            return text
        
        # Split text into lines and limit to max_lines
        lines = text.split('\n')
        truncated_lines = []
        total_chars = 0
        
        for line in lines:
            if len(truncated_lines) >= max_lines:
                break
                
            if len(line) <= chars_per_line:
                truncated_lines.append(line)
                total_chars += len(line)
            else:
                # Split long line into multiple lines
                remaining_lines = max_lines - len(truncated_lines)
                if remaining_lines <= 0:
                    break
                    
                # Calculate how many lines this long line needs
                needed_lines = max(1, (len(line) // chars_per_line) + 1)
                lines_to_add = min(needed_lines, remaining_lines)
                
                for i in range(lines_to_add):
                    start = i * chars_per_line
                    end = start + chars_per_line
                    if start < len(line):
                        truncated_lines.append(line[start:end])
                        total_chars += len(line[start:end])
        
        # Join lines and truncate if still too long
        result = '\n'.join(truncated_lines)
        
        # Truncate if the result is still too long for the width
        if len(result) > chars_per_line * max_lines:
            result = result[:chars_per_line * max_lines - 3] + "..."
        
        return result

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
        
        # Ensure minimum height and add small buffer for consistency
        calculated_height = total_lines * line_height
        return max(calculated_height, line_height)

    # Check if there's enough space on the current page for a table row
    def check_page_break(self, required_height):
        # Get current Y position and page height
        current_y = self.get_y()
        page_height = self.h
        margin = 25  # Bottom margin - increased for better spacing
        
        # Check if adding the required height would exceed the page
        if current_y + required_height > page_height - margin:
            return True  # Need page break
        return False  # Enough space

    # Check if there's enough space for a section header
    def check_header_space(self, header_height=15):
        return self.check_page_break(header_height)

    # Ensure proper table positioning within margins
    def ensure_table_position(self):
        # Reset to proper left margin for tables
        self.set_x(20)
        # Ensure we have enough space from top
        if self.get_y() < 40:  # Account for header
            self.set_y(40)

    # Get available width for content (respecting margins)
    def get_available_width(self):
        return self.w - 40  # Page width minus left and right margins

    # Create a table cell with proper vertical alignment
    def create_aligned_cell(self, width, height, text, border=1, align='C', fill=False):
        # Calculate vertical center position for the text
        text_height = 10  # Height of single line text
        y_offset = (height - text_height) / 2
        
        # Store current position
        current_x = self.get_x()
        current_y = self.get_y()
        
        # Draw the cell border
        self.cell(width, height, '', border, ln=0, fill=fill)
        
        # Position text in the center of the cell
        self.set_xy(current_x, current_y + y_offset)
        self.cell(width, text_height, text, 0, align=align, ln=0)
        
        # Don't change position - let the calling method control it
        # This ensures table continuity

    # Create a multi_cell with exact height control
    def create_exact_height_cell(self, width, height, text, border=1, fill=False):
        # Store current position
        current_x = self.get_x()
        current_y = self.get_y()
        
        # Draw the cell border with exact height
        self.cell(width, height, '', border, ln=0, fill=fill)
        
        # Calculate line height to fit text within the exact height
        line_height = 10
        max_lines = int(height / line_height)
        
        # Use multi_cell but limit to the exact height
        self.set_xy(current_x, current_y)
        self.multi_cell(width, line_height, text, 0, fill=fill)
        
        # Don't change position - let the calling method control it
        # This ensures table continuity

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
        available_width = self.get_available_width()
        data_width = available_width - int(available_width * 0.2)  # Calculate data width
        data_height = self.calculate_text_height(display_data, data_width, line_height)
        
        # Further truncate text to fit within the calculated height
        display_data = self.truncate_text_by_height(str(data), data_width, data_height, line_height)
        
        # Check if we need a page break to keep the table row together
        if self.check_page_break(data_height):
            self.add_page()
        
        # Ensure we're within page margins
        current_x = self.get_x()
        if current_x < 20:  # Left margin
            self.set_x(20)
        elif current_x > self.w - 200:  # Right margin (table width is 200)
            self.set_x(20)  # Reset to left margin
        
        # Calculate column widths based on available space
        available_width = self.get_available_width()
        label_width = int(available_width * 0.2)  # 20% for label
        data_width = available_width - label_width  # Remaining for data
        
        # Store current x position
        x_pos = self.get_x()
        y_pos = self.get_y()
        
        # First column (label) - use same height as data column and center text vertically
        self.create_aligned_cell(label_width, data_height, text, border=1, align='C', fill=False)
        
        # Second column (data) - use exact height control to match first column
        self.set_xy(x_pos + label_width, y_pos)
        self.create_exact_height_cell(data_width, data_height, display_data, border=1, fill=True)
        
        # Position for next row - both cells now have exactly the same height
        # Don't use ln() as it breaks table continuity
        self.set_xy(20, y_pos + data_height)  # Reset to left margin, move down by cell height

    # The function to iterate through the available findings and write to data
    def write_to_table(self, findings, type):
        col_width = 50
        if findings:
            for i, finding in enumerate(findings):
                # Ensure proper table positioning
                self.ensure_table_position()
                
                # Calculate total height needed for this finding
                total_height = 0
                available_width = self.get_available_width()
                data_width = available_width - int(available_width * 0.2)
                total_height += self.calculate_text_height(str(finding.category), data_width, 10)
                total_height += self.calculate_text_height(str(finding.description), data_width, 10)
                total_height += 10  # Severity level row (fixed height)
                total_height += self.calculate_text_height(str(finding.reference), data_width, 10)
                total_height += self.calculate_text_height(str(finding.code), data_width, 10)
                total_height += 15  # Add spacing between rows
                
                # Check if we need a page break to keep the entire finding together
                if self.check_page_break(total_height):
                    self.add_page()
                    self.ensure_table_position()  # Reset position on new page
                
                self.create_table("Category",self.clean_text(str(finding.category)))
                self.create_table("Description",self.clean_text(str(finding.description)))
                self.create_table("Severity Level", type, is_severity=True)
                self.create_table("Reference",self.clean_text(str(finding.reference)))
                self.create_table("Affected Lines",self.clean_text(str(finding.code)))
                
                # Add spacing between findings while maintaining table structure
                if i < len(findings) - 1:
                    # Add space between findings but keep table structure
                    current_y = self.get_y()
                    self.set_xy(20, current_y + 5)  # Small gap between findings
                else:
                    # Last finding - add final spacing
                    current_y = self.get_y()
                    self.set_xy(20, current_y + 3)


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
    pdf.add_page()

    #Add title
    pdf.set_font("Arial", style="B", size=18)
    pdf.multi_cell(pdf.get_available_width(), 10, txt="Semgrep Report")
    pdf.ln(5)

    # Add summary section
    # Check if there's enough space for the summary header
    if pdf.check_header_space(20):  # Summary needs more space
        pdf.add_page()
    pdf.set_font("Arial", style="B", size=12)
    pdf.multi_cell(pdf.get_available_width(), 10, txt="Scan Summary")
    pdf.set_font("Arial", size=10)
    pdf.multi_cell(pdf.get_available_width(), 10, findings[0])
    pdf.ln(5)

    # High severity findings
    if high:
        # Check if there's enough space for the header
        if pdf.check_header_space():
            pdf.add_page()
        pdf.set_font("Arial", style="B", size=12)
        pdf.multi_cell(pdf.get_available_width(), 10, txt="High Severity Findings")
        pdf.set_font("Arial", size=10)
        pdf.write_to_table(high,"High")
        pdf.ln(3)

    # Medium severity findings
    if medium:
        # Check if there's enough space for the header
        if pdf.check_header_space():
            pdf.add_page()
        pdf.set_font("Arial", style="B", size=12)
        pdf.multi_cell(pdf.get_available_width(), 10, txt="Medium Severity Findings")
        pdf.set_font("Arial", size=10)
        pdf.write_to_table(medium,"Medium")
        pdf.ln(3)

    # Low severity findings
    if low:
        # Check if there's enough space for the header
        if pdf.check_header_space():
            pdf.add_page()
        pdf.set_font("Arial", style="B", size=12)
        pdf.multi_cell(pdf.get_available_width(), 10, txt="Low Severity Findings")
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
    
    

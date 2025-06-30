import pandas as pd
import pdfplumber
import re
import os
import sys
from pathlib import Path

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF using pdfplumber for better layout handling"""
    try:
        text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {str(e)}")
        return ""

def extract_field_value(text, field_patterns):
    for pattern in field_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            value = match.group(1).strip()
            value = re.sub(r'\s+', ' ', value)
            value = value.replace('\n', ' ').strip()
            value = re.sub(r'[^\w\s\-,./()&]+$', '', value)
            return value
    return ""

def extract_by_line_parsing(text):
    lines = text.split('\n')
    data = {}
    for i, line in enumerate(lines):
        line = line.strip()
        if 'First Name' in line and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if next_line and not any(x in next_line.lower() for x in ['middle', 'last', 'name']):
                data['First Name'] = next_line
        elif 'Middle Name' in line and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if next_line and not any(x in next_line.lower() for x in ['first', 'last', 'name']):
                data['Middle Name'] = next_line
        elif 'Last Name' in line and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if next_line and 'any criminal' not in next_line.lower():
                data['Last Name'] = next_line
        elif 'House Number' in line and i + 1 < len(lines):
            data['House Number'] = lines[i + 1].strip()
        elif 'Building Name' in line and i + 1 < len(lines):
            data['Building Name'] = lines[i + 1].strip()
        elif 'Street Name' in line and i + 1 < len(lines):
            data['Street Name'] = lines[i + 1].strip()
        elif 'Locality' in line and i + 1 < len(lines):
            data['Locality'] = lines[i + 1].strip()
        elif 'Landmark' in line and i + 1 < len(lines):
            data['Landmark'] = lines[i + 1].strip()
        elif 'State/UT' in line and i + 1 < len(lines):
            data['State/UT'] = lines[i + 1].strip()
        elif 'Division' in line and i + 1 < len(lines):
            data['Division'] = lines[i + 1].strip()
        elif 'District' in line and i + 1 < len(lines):
            data['District'] = lines[i + 1].strip()
        elif 'Taluka' in line and i + 1 < len(lines):
            data['Taluka'] = lines[i + 1].strip()
        elif 'Village' in line and i + 1 < len(lines):
            data['Village'] = lines[i + 1].strip()
        elif 'Pin Code' in line and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if re.match(r'^[0-9]{6}$', next_line):
                data['Pin Code'] = next_line
        elif 'Office Number' in line and i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            if re.match(r'^[0-9]+$', next_line):
                data['Office Number'] = next_line
        elif 'Website URL' in line and i + 1 < len(lines):
            data['Website URL'] = lines[i + 1].strip()
    return data

def extract_information_from_pdf(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    if not text:
        return None

    print("DEBUG: Extracted text from PDF:")
    print("=" * 50)
    print(text[:2000])
    print("=" * 50)

    patterns = {
        'First Name': [
            r'First Name\s+([A-Z]+)',
            r'First Name\s+([A-Z]+)\s+Middle Name',
            r'First Name\s+([A-Z]+)\s+Last Name',
        ],
        'Middle Name': [
            r'Middle Name\s+([A-Z]+)',
            r'Middle Name\s+([A-Z]+)\s+Last Name',
        ],
        'Last Name': [
            r'Last Name\s+([A-Z]+)',
            r'Last Name\s+([A-Z]+)\s+Any',
        ],
        'House Number': [
            r'House Number\s+([^\n]+?)\s+Building',
            r'House Number\s+([^\n]+)',
        ],
        'Building Name': [
            r'Building Name\s+([^\n]+?)\s+Street',
            r'Building Name\s+([^\n]+)',
        ],
        'Street Name': [
            r'Street Name\s+([^\n]+?)\s+Locality',
            r'Street Name\s+([^\n]+)',
        ],
        'Locality': [
            r'Locality\s+([^\n]+?)\s+Landmark',
            r'Locality\s+([^\n]+)',
        ],
        'Landmark': [
            r'Landmark\s+([^\n]+?)\s+State',
            r'Landmark\s+([^\n]+)',
        ],
        'State/UT': [
            r'State/UT\s+([^\n]+?)\s+Division',
            r'State/UT\s+([^\n]+)',
        ],
        'Division': [
            r'Division\s+([^\n]+?)\s+District',
            r'Division\s+([^\n]+)',
        ],
        'District': [
            r'District\s+([^\n]+?)\s+Taluka',
            r'District\s+([^\n]+)',
        ],
        'Taluka': [
            r'Taluka\s+([^\n]+?)\s+Village',
            r'Taluka\s+([^\n]+)',
        ],
        'Village': [
            r'Village\s+([^\n]+?)\s+Pin',
            r'Village\s+([^\n]+)',
        ],
        'Pin Code': [
            r'Pin Code\s+([0-9]{6})',
        ],
        'Office Number': [
            r'Office Number\s+([0-9]+)',
        ],
        'Website URL': [
            r'Website URL\s+([^\s]+)',
        ]
    }

    extracted_data = {}
    for field, field_patterns in patterns.items():
        value = extract_field_value(text, field_patterns)
        extracted_data[field] = value
        print(f"DEBUG: {field}: '{value}'")

    line_parsed_data = extract_by_line_parsing(text)
    for field in extracted_data.keys():
        if not extracted_data[field] and field in line_parsed_data:
            extracted_data[field] = line_parsed_data[field]
            print(f"DEBUG: {field} (line parsing): '{line_parsed_data[field]}'")

    result = {
        'First Name': extracted_data.get('First Name', ''),
        'Middle Name': extracted_data.get('Middle Name', ''),
        'Last Name': extracted_data.get('Last Name', ''),
        'House Number': extracted_data.get('House Number', ''),
        'Building Name': extracted_data.get('Building Name', ''),
        'Street Name': extracted_data.get('Street Name', ''),
        'Locality': extracted_data.get('Locality', ''),
        'Landmark': extracted_data.get('Landmark', ''),
        'State/UT': extracted_data.get('State/UT', ''),
        'Division': extracted_data.get('Division', ''),
        'District': extracted_data.get('District', ''),
        'Taluka': extracted_data.get('Taluka', ''),
        'Village': extracted_data.get('Village', ''),
        'Pin Code': extracted_data.get('Pin Code', ''),
        'Contact Details': extracted_data.get('Office Number', ''),
        'Website': extracted_data.get('Website URL', ''),
        'Source File': os.path.basename(pdf_path)
    }
    return result

def process_single_pdf(pdf_path, output_csv='extracted_data.csv'):
    if not os.path.exists(pdf_path):
        print(f"Error: File {pdf_path} not found!")
        return
    print(f"Processing: {pdf_path}")
    data = extract_information_from_pdf(pdf_path)
    if data:
        df = pd.DataFrame([data])
        df.to_csv(output_csv, index=False)
        print(f"Data extracted and saved to {output_csv}")
        print("\nExtracted Information:")
        for key, value in data.items():
            print(f"{key}: {value}")
    else:
        print("Failed to extract data from PDF")

def process_multiple_pdfs(pdf_folder, output_csv='extracted_data.csv'):
    if not os.path.exists(pdf_folder):
        print(f"Error: Folder {pdf_folder} not found!")
        return
    pdf_files = list(Path(pdf_folder).glob("*.pdf"))
    if not pdf_files:
        print(f"No PDF files found in {pdf_folder}")
        return
    all_data = []
    for pdf_file in pdf_files:
        print(f"Processing: {pdf_file}")
        data = extract_information_from_pdf(str(pdf_file))
        if data:
            all_data.append(data)
        else:
            print(f"Failed to extract data from {pdf_file}")
    if all_data:
        df = pd.DataFrame(all_data)
        df.to_csv(output_csv, index=False)
        print(f"\nData from {len(all_data)} PDFs extracted and saved to {output_csv}")
        print(f"Processed {len(pdf_files)} PDF files")
        print(f"Successfully extracted data from {len(all_data)} files")
    else:
        print("No data could be extracted from any PDF files")

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  For single PDF: python script.py <pdf_file_path> [output_csv]")
        print("  For folder of PDFs: python script.py <folder_path> [output_csv]")
        print("\nExample:")
        print("  python script.py document.pdf")
        print("  python script.py ./pdf_folder/ all_data.csv")
        return
    input_path = sys.argv[1]
    output_csv = sys.argv[2] if len(sys.argv) > 2 else 'extracted_data.csv'
    if os.path.isfile(input_path) and input_path.lower().endswith('.pdf'):
        process_single_pdf(input_path, output_csv)
    elif os.path.isdir(input_path):
        process_multiple_pdfs(input_path, output_csv)
    else:
        print("Error: Please provide a valid PDF file or folder containing PDF files")

if __name__ == "__main__":
    main()

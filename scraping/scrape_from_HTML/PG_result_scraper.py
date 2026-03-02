import os
import glob
import json
from bs4 import BeautifulSoup
import re

# Set the base directory to target ONLY the MSC folder
BASE_DIR = "/Users/sameerbanchhor/Desktop/durg results/datasets/PG/MSC" # MA , OTHER_PG , MSC

def clean_text(text):
    """Removes extra whitespace and non-breaking spaces."""
    if not text:
        return ""
    return text.replace('&nbsp;', '').strip()

def extract_metadata(soup, label):
    """Helper function to find a label (like 'Roll Number') and get its corresponding value."""
    # Find the <strong> tag containing the label
    lbl_tag = soup.find('strong', string=re.compile(label, re.IGNORECASE))
    if lbl_tag:
        parent_td = lbl_tag.find_parent('td')
        if parent_td:
            # The structure is usually <td>Label</td> <td>:</td> <td>Value</td>
            siblings = parent_td.find_next_siblings('td')
            if len(siblings) >= 2:
                return clean_text(siblings[1].get_text())
    return ""

def parse_html_result(filepath):
    """Parses a single HTML result file and returns a comprehensive dictionary of the data."""
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    soup = BeautifulSoup(content, 'html.parser')
    result_data = {"file_path": filepath}

    # 1. Extract Exam Name / Semester & Declaration Date
    exam_name_td = soup.find('td', style=lambda v: v and 'font-size:16px' in v)
    result_data['exam_name'] = clean_text(exam_name_td.get_text()) if exam_name_td else ""
    
    decl_date_td = soup.find('td', string=re.compile(r'Result Declared', re.IGNORECASE))
    result_data['result_declared'] = clean_text(decl_date_td.get_text()).replace("Result Declared :", "").strip() if decl_date_td else ""

    # 2. Extract Student Details
    result_data['roll_number'] = extract_metadata(soup, "Roll Number")
    result_data['enrollment_no'] = extract_metadata(soup, "Enrollment No")
    result_data['name'] = extract_metadata(soup, "Name")
    result_data['student_type'] = extract_metadata(soup, "Student Type")
    result_data['father_husband_name'] = extract_metadata(soup, "Father's/Husband's Name")
    result_data['mother_name'] = extract_metadata(soup, "Mother's Name")
    result_data['college'] = extract_metadata(soup, "College")
    result_data['center'] = extract_metadata(soup, "Center")

    # 3. Extract Marks Data
    # The marks table is uniquely identified by border="1"
    marks_table = soup.find('table', border="1")
    subjects = []
    
    if marks_table:
        rows = marks_table.find_all('tr')
        # Skip the first 2 rows (header rows)
        for row in rows[2:]:
            cols = row.find_all('td')
            
            # The main subject rows have exactly 16 columns
            if len(cols) == 16:
                subj_code = clean_text(cols[0].get_text())
                subj_name = clean_text(cols[1].get_text())
                
                # Check if this is the Grand Total row
                if "TOTAL" in subj_name.upper() and not subj_code:
                    result_data['grand_max_marks'] = clean_text(cols[2].get_text())
                    result_data['grand_total_obtained'] = clean_text(cols[14].get_text())
                    continue
                
                # Check if this is the SGPA / Result Status row (usually colspan is used, but just in case)
                if "SGPA" in subj_code.upper() or "SGPA" in subj_name.upper():
                    continue

                # Normal subject row
                subject_data = {
                    "subject_code": subj_code,
                    "subject_name": subj_name,
                    "max_marks": clean_text(cols[2].get_text()),
                    "min_marks": clean_text(cols[3].get_text()),
                    "theory_marks": {
                        "I": clean_text(cols[4].get_text()),
                        "II": clean_text(cols[5].get_text()),
                        "III": clean_text(cols[6].get_text())
                    },
                    "sessional_marks": {
                        "I": clean_text(cols[7].get_text()),
                        "II": clean_text(cols[8].get_text()),
                        "III": clean_text(cols[9].get_text())
                    },
                    "theory_total": clean_text(cols[10].get_text()),
                    "practical_marks": {
                        "I": clean_text(cols[11].get_text()),
                        "II": clean_text(cols[12].get_text()),
                        "sessional": clean_text(cols[13].get_text())
                    },
                    "subject_total": clean_text(cols[14].get_text()),
                    "status": clean_text(cols[15].get_text())
                }
                subjects.append(subject_data)
                
    result_data['subjects'] = subjects

    # 4. Extract SGPA and Result (from the bottom of the table)
    sgpa_td = soup.find('td', string=re.compile(r'\s*SGPA\s*'))
    if sgpa_td:
        sgpa_val = sgpa_td.find_next_sibling('td')
        result_data['sgpa'] = clean_text(sgpa_val.get_text()) if sgpa_val else ""
    else:
        result_data['sgpa'] = ""

    result_status_td = soup.find('td', string=re.compile(r'\s*RESULT\s*'))
    if result_status_td:
        res_val = result_status_td.find_next_sibling('td')
        result_data['result_status'] = clean_text(res_val.get_text()) if res_val else ""
    else:
        result_data['result_status'] = ""

    return result_data

def main():
    all_results = []
    
    # Use glob to recursively find all .html files specifically in the MSC directory
    search_pattern = os.path.join(BASE_DIR, "**", "*.html")
    html_files = glob.glob(search_pattern, recursive=True)
    
    print(f"Found {len(html_files)} HTML files in the MSC directory. Starting extraction...")

    for filepath in html_files:
        try:
            parsed_data = parse_html_result(filepath)
            # Filter out empty or incorrectly parsed files by ensuring a roll number exists
            if parsed_data.get('roll_number'):
                all_results.append(parsed_data)
        except Exception as e:
            print(f"Error parsing {filepath}: {e}")

    # Save to JSON
    output_file = "msc_comprehensive_results.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=4, ensure_ascii=False)

    print(f"Extraction complete! Successfully scraped {len(all_results)} records.")
    print(f"Data saved to {output_file}")

if __name__ == "__main__":
    main()
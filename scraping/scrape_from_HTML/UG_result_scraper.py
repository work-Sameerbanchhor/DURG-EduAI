import os
import glob
import json
import multiprocessing as mp
from bs4 import BeautifulSoup
import re
import time

# Set the base directory to target ONLY the UG folder
BASE_DIR = "/Users/sameerbanchhor/Desktop/durg results/datasets/UG"
OUTPUT_FILE = "ug_comprehensive_results.json"

def clean_text(text):
    """Removes extra whitespace, non-breaking spaces, and random asterisks."""
    if not text:
        return ""
    return text.replace('&nbsp;', '').replace('*', '').strip()

def extract_metadata(soup, label):
    """Helper function to find a label and get its corresponding value."""
    lbl_tag = soup.find('strong', string=re.compile(label, re.IGNORECASE))
    if lbl_tag:
        parent_td = lbl_tag.find_parent('td')
        if parent_td:
            siblings = parent_td.find_next_siblings('td')
            if len(siblings) >= 2:
                return clean_text(siblings[1].get_text())
    return ""

def process_file(filepath):
    """
    Parses a single HTML file using the ultra-fast 'lxml' parser.
    Returns the dictionary if successful, or None if it fails/is empty.
    """
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Swapped to 'lxml' for massive speed gains
        soup = BeautifulSoup(content, 'lxml')
        
        # Quick check: if there is no Roll Number, skip heavy processing
        roll_number = extract_metadata(soup, "Roll Number")
        if not roll_number:
            return None

        result_data = {
            "file_path": filepath,
            "roll_number": roll_number
        }

        # 1. Extract Exam Name & Declaration Date
        exam_name_td = soup.find('td', style=lambda v: v and 'font-size:16px' in v)
        result_data['exam_name'] = clean_text(exam_name_td.get_text()) if exam_name_td else ""
        
        decl_date_td = soup.find('td', string=re.compile(r'Result Declared', re.IGNORECASE))
        result_data['result_declared'] = clean_text(decl_date_td.get_text()).replace("Result Declared :", "").strip() if decl_date_td else ""

        # 2. Extract Remaining Student Details
        result_data['enrollment_no'] = extract_metadata(soup, "Enrollment No")
        result_data['name'] = extract_metadata(soup, "Name")
        result_data['student_type'] = extract_metadata(soup, "Student Type")
        result_data['father_husband_name'] = extract_metadata(soup, "Father's/Husband's Name")
        result_data['mother_name'] = extract_metadata(soup, "Mother's Name")
        result_data['college'] = extract_metadata(soup, "College")
        result_data['center'] = extract_metadata(soup, "Center")

        # 3. Extract Marks Data
        marks_table = soup.find('table', border="1")
        subjects = []
        result_data['past_years'] = {}

        if marks_table:
            rows = marks_table.find_all('tr')
            for row in rows[2:]:
                cols = row.find_all('td')
                
                if len(cols) == 16:
                    subj_code = clean_text(cols[0].get_text())
                    subj_name = clean_text(cols[1].get_text())
                    
                    if "TOTAL" == subj_name.upper() and not subj_code:
                        result_data['grand_max_marks'] = clean_text(cols[2].get_text())
                        result_data['grand_total_obtained'] = clean_text(cols[14].get_text())
                        continue
                    
                    if "FIRST YEAR TOTAL/OBTAIN" in subj_name.upper():
                        result_data['past_years']['first_year_max'] = clean_text(cols[2].get_text())
                        result_data['past_years']['first_year_obtained'] = clean_text(cols[14].get_text())
                        continue
                    
                    if "SECOND YEAR TOTAL/OBTAIN" in subj_name.upper():
                        result_data['past_years']['second_year_max'] = clean_text(cols[2].get_text())
                        result_data['past_years']['second_year_obtained'] = clean_text(cols[14].get_text())
                        continue

                    if "RESULT" in subj_name.upper() or "SGPA" in subj_code.upper():
                        continue

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

        # 4. Extract Result Status
        result_status_td = soup.find('td', string=re.compile(r'\s*RESULT\s*'))
        if result_status_td:
            res_val = result_status_td.find_next_sibling('td')
            result_data['result_status'] = clean_text(res_val.get_text()) if res_val else ""
        else:
            result_data['result_status'] = ""

        return result_data
        
    except Exception as e:
        # Fails silently for corrupted files, returns None
        return None

def main():
    start_time = time.time()
    
    # iglob creates a generator, meaning it doesn't load all 106k paths into memory at once
    search_pattern = os.path.join(BASE_DIR, "**", "*.html")
    html_files_generator = glob.iglob(search_pattern, recursive=True)
    
    print("Beginning high-speed extraction across multiple CPU cores...")
    
    # We will manually construct the JSON file to keep RAM usage near zero.
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write("[\n")  # Open the JSON array
        
        # Use all available logical CPU cores for maximum aggression
        cores = mp.cpu_count()
        processed_count = 0
        first_item = True
        
        # imap_unordered is incredibly fast because it yields results the millisecond a core finishes a file
        with mp.Pool(processes=cores) as pool:
            for result in pool.imap_unordered(process_file, html_files_generator, chunksize=200):
                if result is not None:
                    # JSON formatting logic
                    if not first_item:
                        f.write(",\n")
                    json.dump(result, f, ensure_ascii=False)
                    first_item = False
                    processed_count += 1
                    
                    # Live progress update
                    if processed_count % 5000 == 0:
                        print(f"Processed {processed_count} files...")

        f.write("\n]")  # Close the JSON array
        
    elapsed_time = time.time() - start_time
    print(f"\nExtraction complete! Successfully scraped {processed_count} records.")
    print(f"Data saved to {OUTPUT_FILE}")
    print(f"Total time elapsed: {elapsed_time:.2f} seconds.")

if __name__ == "__main__":
    main()
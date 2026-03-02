import os
import glob
import json
import re
from collections import defaultdict
from datetime import datetime

# Automatically targets your Mac's Desktop
DESKTOP_PATH = os.path.expanduser("~/Desktop")
OUTPUT_FILE = os.path.join(DESKTOP_PATH, "University_Comprehensive_Report.md")

def safe_float(val, default=0.0):
    """Safely convert dirty strings to float."""
    if not val: return default
    try:
        clean_val = re.sub(r'[^\d.]', '', str(val))
        return float(clean_val) if clean_val else default
    except ValueError:
        return default

def generate_report():
    print("🚀 Initializing Comprehensive Data Analysis...")
    
    dataset = []
    json_files = glob.glob("*.json")
    
    if not json_files:
        print("❌ No JSON files found in the current directory.")
        return

    # Load all data
    for file in json_files:
        print(f"Loading {file}...")
        try:
            with open(file, 'r', encoding='utf-8') as f:
                dataset.extend(json.load(f))
        except Exception as e:
            print(f"Error reading {file}: {e}")

    total_students = len(dataset)
    print(f"✅ Loaded {total_students} student records. Crunching numbers...")

    # --- AGGREGATION VARIABLES ---
    status_counts = defaultdict(int)
    college_stats = defaultdict(lambda: {"total": 0, "passed": 0, "total_score": 0, "max_score": 0})
    course_stats = defaultdict(lambda: {"total": 0, "passed": 0})
    subject_stats = defaultdict(lambda: {"attempts": 0, "earned": 0, "possible": 0})
    
    ug_students = []
    pg_students = []

    # --- PROCESS DATA ---
    for s in dataset:
        # 1. Status Breakdown
        status = s.get("result_status", "UNKNOWN").upper().strip()
        status_counts[status] += 1

        # 2. Extract Grand Totals for %, routing to UG or PG
        obt = safe_float(s.get("grand_total_obtained"))
        max_m = safe_float(s.get("grand_max_marks"))
        percentage = (obt / max_m * 100) if max_m > 0 else 0
        
        # Categorize student for leaderboards
        exam_name = s.get("exam_name", "Unknown Course").strip()
        student_data = {
            "name": " ".join(s.get("name", "Unknown").split()), # Smart space normalization!
            "roll": s.get("roll_number", ""),
            "college": " ".join(s.get("college", "").split('-')[1:]).strip() if "-" in s.get("college", "") else s.get("college", ""),
            "course": exam_name,
            "percentage": percentage,
            "sgpa": safe_float(s.get("sgpa"))
        }

        if s.get("sgpa") or "M." in exam_name or "PG" in exam_name:
            pg_students.append(student_data)
        else:
            ug_students.append(student_data)

        # 3. College Stats
        col = student_data["college"]
        if col:
            college_stats[col]["total"] += 1
            if status == "PASS":
                college_stats[col]["passed"] += 1
            college_stats[col]["total_score"] += obt
            college_stats[col]["max_score"] += max_m

        # 4. Course Stats (Simplify exam name to group effectively)
        course_base = exam_name.split('-')[0].strip() if '-' in exam_name else exam_name
        course_stats[course_base]["total"] += 1
        if status == "PASS":
            course_stats[course_base]["passed"] += 1

        # 5. Subject Diagnostics
        for subj in s.get("subjects", []):
            s_name = " ".join(subj.get("subject_name", "").split())
            s_obt = safe_float(subj.get("subject_total"))
            s_max = safe_float(subj.get("max_marks"))
            if s_max > 0 and s_name:
                subject_stats[s_name]["attempts"] += 1
                subject_stats[s_name]["earned"] += s_obt
                subject_stats[s_name]["possible"] += s_max

    print("📊 Writing Markdown Report...")

    # --- SORT & PREPARE DATA FOR MARKDOWN ---
    pass_rate = (status_counts.get("PASS", 0) / total_students * 100) if total_students else 0
    
    # Sort Colleges by Pass Rate (Min 50 students)
    ranked_colleges = []
    for col, data in college_stats.items():
        if data["total"] >= 50:
            c_pass = (data["passed"] / data["total"]) * 100
            ranked_colleges.append((col, data["total"], c_pass))
    ranked_colleges.sort(key=lambda x: x[2], reverse=True)

    # Sort Subjects to find Bottlenecks (Min 100 attempts)
    bottlenecks = []
    for subj, data in subject_stats.items():
        if data["attempts"] >= 100:
            avg_pct = (data["earned"] / data["possible"]) * 100
            bottlenecks.append((subj, data["attempts"], avg_pct))
    bottlenecks.sort(key=lambda x: x[2]) # Lowest first

    # Sort Leaderboards
    ug_toppers = sorted(ug_students, key=lambda x: x["percentage"], reverse=True)[:10]
    pg_toppers = sorted(pg_students, key=lambda x: x["sgpa"], reverse=True)[:10]

    # --- GENERATE MARKDOWN CONTENT ---
    md = f"""# Hemchand Yadav Vishwavidyalaya - Comprehensive Data Report
*Generated on: {datetime.now().strftime("%B %d, %Y at %I:%M %p")}*

---

## 📈 1. University Overview
* **Total Students Evaluated:** {total_students:,}
* **Undergraduate Candidates:** {len(ug_students):,}
* **Postgraduate Candidates:** {len(pg_students):,}
* **Overall Pass Rate:** {pass_rate:.2f}%

### Result Breakdown
| Status | Count | Percentage |
| :--- | :--- | :--- |
"""
    for stat, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
        if stat:
            md += f"| **{stat}** | {count:,} | {(count/total_students*100):.2f}% |\n"

    md += """
---

## 🏆 2. University Merit Lists

### Top 10 Undergraduate Students (By Grand Percentage)
| Rank | Name | Roll Number | Course | College | Score (%) |
| :---: | :--- | :--- | :--- | :--- | :---: |
"""
    for i, t in enumerate(ug_toppers, 1):
        md += f"| {i} | **{t['name']}** | {t['roll']} | {t['course']} | {t['college']} | {t['percentage']:.2f}% |\n"

    md += """
### Top 10 Postgraduate Students (By SGPA)
| Rank | Name | Roll Number | Course | College | SGPA |
| :---: | :--- | :--- | :--- | :--- | :---: |
"""
    for i, t in enumerate(pg_toppers, 1):
        md += f"| {i} | **{t['name']}** | {t['roll']} | {t['course']} | {t['college']} | {t['sgpa']:.2f} |\n"

    md += """
---

## 🏛 3. Institutional Rankings
*Showing top 15 colleges by pass percentage (Requires a minimum of 50 students enrolled).*

| Rank | College Name | Total Students | Pass Rate |
| :---: | :--- | :---: | :---: |
"""
    for i, c in enumerate(ranked_colleges[:15], 1):
        md += f"| {i} | {c[0]} | {c[1]:,} | **{c[2]:.2f}%** |\n"

    md += """
---

## ⚠️ 4. Academic Bottlenecks (Toughest Subjects)
*The 15 subjects with the lowest average scoring percentage across the university (Min. 100 attempts).*

| Danger Rank | Subject Name | Total Attempts | Avg. Score (%) |
| :---: | :--- | :---: | :---: |
"""
    for i, b in enumerate(bottlenecks[:15], 1):
        md += f"| {i} | {b[0]} | {b[1]:,} | **{b[2]:.2f}%** |\n"

    md += """
---
*Report generated via Durg University Fast-Scraper Engine.*
"""

    # --- SAVE TO FILE ---
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(md)

    print(f"\n✨ Success! Report saved to your desktop: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_report()
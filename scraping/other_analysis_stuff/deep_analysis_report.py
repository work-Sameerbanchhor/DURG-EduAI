import os
import glob
import json
import re
from collections import defaultdict
from datetime import datetime

DESKTOP_PATH = os.path.expanduser("~/Desktop")
OUTPUT_FILE = os.path.join(DESKTOP_PATH, "Durg_University_Deep_Analytics.md")

def safe_float(val, default=0.0):
    if not val: return default
    try:
        clean_val = re.sub(r'[^\d.]', '', str(val))
        return float(clean_val) if clean_val else default
    except ValueError:
        return default

def get_base_course(exam_name):
    """Extracts 'B.Sc.', 'B.A.', 'M.Sc.', etc. from the full exam name."""
    if "B.Sc." in exam_name.upper() or "BSC" in exam_name.upper(): return "B.Sc."
    if "B.A." in exam_name.upper() or " BA " in exam_name.upper(): return "B.A."
    if "B.COM" in exam_name.upper(): return "B.Com."
    if "M.Sc." in exam_name.upper() or "MSC" in exam_name.upper(): return "M.Sc."
    if "M.A." in exam_name.upper() or " MA " in exam_name.upper(): return "M.A."
    return "Other Programs"

def generate_deep_report():
    print("🚀 Initializing Deep Analytics Engine...")
    
    dataset = []
    for file in glob.glob("*.json"):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                dataset.extend(json.load(f))
        except Exception as e:
            print(f"Skipping {file}: {e}")

    total_students = len(dataset)
    if total_students == 0:
        print("❌ No data found.")
        return

    print(f"✅ Loaded {total_students} records. Processing features 1 to 6...")

    # --- DATA STRUCTURES ---
    # 1. Leaderboards
    course_toppers_ug = defaultdict(list)
    course_toppers_pg = defaultdict(list)
    
    # 2. Grade Distribution (UG Percentages)
    grade_bins = {"Distinction (>75%)": 0, "First Div (60-74.9%)": 0, "Second Div (45-59.9%)": 0, "Third Div (33-44.9%)": 0, "Fail/Supply (<33%)": 0}
    
    # 3. UG Progression
    progression = {"y1_total": 0, "y2_total": 0, "y3_total": 0, "count": 0}
    
    # 4. Subject Deep Dive
    subjects = defaultdict(lambda: {"attempts": 0, "earned": 0, "possible": 0})
    
    # 5. Demographics (Regular vs Private/Non-Collegiate)
    demographics = defaultdict(lambda: {"total": 0, "passed": 0, "total_pct": 0, "valid_pct_count": 0})
    
    # 6. Course vs Course
    course_compare = defaultdict(lambda: {"total": 0, "passed": 0, "total_pct": 0, "valid_pct_count": 0})

    # --- CORE PROCESSING LOOP ---
    for s in dataset:
        exam_name = s.get("exam_name", "Unknown")
        base_course = get_base_course(exam_name)
        status = s.get("result_status", "UNKNOWN").upper().strip()
        student_type = s.get("student_type", "UNKNOWN").upper().strip()
        
        # Calculate Percentage / SGPA
        obt = safe_float(s.get("grand_total_obtained"))
        max_m = safe_float(s.get("grand_max_marks"))
        pct = (obt / max_m * 100) if max_m > 0 else 0
        sgpa = safe_float(s.get("sgpa"))

        name = " ".join(s.get("name", "Unknown").split())
        col = " ".join(s.get("college", "").split('-')[1:]).strip() if "-" in s.get("college", "") else s.get("college", "")

        is_pg = sgpa > 0 or "M." in base_course

        # F1: Leaderboards
        student_record = {"name": name, "college": col, "pct": pct, "sgpa": sgpa}
        if is_pg:
            course_toppers_pg[base_course].append(student_record)
        else:
            course_toppers_ug[base_course].append(student_record)

        # F2: Grade Distribution (UG Only for percentage bell curve)
        if not is_pg and max_m > 0:
            if pct >= 75: grade_bins["Distinction (>75%)"] += 1
            elif pct >= 60: grade_bins["First Div (60-74.9%)"] += 1
            elif pct >= 45: grade_bins["Second Div (45-59.9%)"] += 1
            elif pct >= 33: grade_bins["Third Div (33-44.9%)"] += 1
            else: grade_bins["Fail/Supply (<33%)"] += 1

        # F3: UG Progression
        if "past_years" in s and s["past_years"]:
            y1 = safe_float(s["past_years"].get("first_year_obtained"))
            y2 = safe_float(s["past_years"].get("second_year_obtained"))
            if y1 > 0 and y2 > 0 and obt > 0:
                progression["y1_total"] += y1
                progression["y2_total"] += y2
                progression["y3_total"] += obt
                progression["count"] += 1

        # F4: Subjects
        for subj in s.get("subjects", []):
            s_name = " ".join(subj.get("subject_name", "").split())
            s_obt = safe_float(subj.get("subject_total"))
            s_max = safe_float(subj.get("max_marks"))
            if s_max > 0 and s_name:
                subjects[s_name]["attempts"] += 1
                subjects[s_name]["earned"] += s_obt
                subjects[s_name]["possible"] += s_max

        # F5 & F6: Demographics & Course Compare
        # Clean up student type (Group ex-students and private together if needed)
        std_type = "REGULAR" if "REGULAR" in student_type else ("PRIVATE/EX" if student_type else "UNKNOWN")
        
        for tracker in [demographics[std_type], course_compare[base_course]]:
            tracker["total"] += 1
            if status == "PASS": tracker["passed"] += 1
            if max_m > 0:
                tracker["total_pct"] += pct
                tracker["valid_pct_count"] += 1

    print("📊 Writing Deep Analytics Markdown Report...")

    # --- MARKDOWN GENERATION ---
    md = f"""# Hemchand Yadav Vishwavidyalaya - Deep Analytics Report
*Comprehensive Institutional Intelligence • Generated on {datetime.now().strftime("%B %d, %Y")}*

---

## 1. 🏆 Top 5 Merit Leaders by Core Programs

### Undergraduate Toppers (By Percentage)
"""
    for course, students in course_toppers_ug.items():
        if len(students) < 5: continue
        md += f"**{course}**\n"
        top5 = sorted(students, key=lambda x: x["pct"], reverse=True)[:5]
        for i, s in enumerate(top5, 1):
            md += f"{i}. **{s['name']}** ({s['college']}) — **{s['pct']:.2f}%**\n"
        md += "\n"

    md += "### Postgraduate Toppers (By SGPA)\n"
    for course, students in course_toppers_pg.items():
        if len(students) < 5: continue
        md += f"**{course}**\n"
        top5 = sorted(students, key=lambda x: x["sgpa"], reverse=True)[:5]
        for i, s in enumerate(top5, 1):
            md += f"{i}. **{s['name']}** ({s['college']}) — **{s['sgpa']:.2f} SGPA**\n"
        md += "\n"

    md += """---

## 2. 📊 Grade Distribution (UG Bell Curve)
*How Undergraduate students map across standard percentage brackets.*

| Grade Bracket | Student Count | % of UG Base |
| :--- | :---: | :---: |
"""
    ug_total = sum(grade_bins.values())
    for grade, count in grade_bins.items():
        pct = (count / ug_total * 100) if ug_total > 0 else 0
        md += f"| {grade} | {count:,} | {pct:.1f}% |\n"

    md += """
---

## 3. 📈 Multi-Year Growth Trajectory (UG Progression)
*Tracking cohort consistency across their 3-year journey.*

"""
    if progression["count"] > 0:
        c = progression["count"]
        y1_avg = progression["y1_total"] / c
        y2_avg = progression["y2_total"] / c
        y3_avg = progression["y3_total"] / c
        trend = "Upward 🟢" if y3_avg > y1_avg else "Downward 🔴"
        
        md += f"- **Cohort Size Analyzed:** {c:,} students (complete 3-year data)\n"
        md += f"- **First Year Average:** {y1_avg:.1f} marks\n"
        md += f"- **Second Year Average:** {y2_avg:.1f} marks\n"
        md += f"- **Final Year Average:** {y3_avg:.1f} marks\n"
        md += f"- **Overall Trajectory:** {trend}\n"
    else:
        md += "*Insufficient 3-year historical data found.*\n"

    md += """
---

## 4. 🔬 Subject-Specific Deep Dive
*Identifying the absolute easiest and toughest papers in the university (Min. 100 attempts).*

### The 10 Toughest Subjects (Lowest Avg % Scoring)
| Rank | Subject Name | Attempts | Avg Score (%) |
| :---: | :--- | :---: | :---: |
"""
    # Calculate subject percentages
    subj_list = []
    for s_name, data in subjects.items():
        if data["attempts"] >= 100:
            subj_list.append((s_name, data["attempts"], (data["earned"] / data["possible"] * 100)))
    
    subj_list.sort(key=lambda x: x[2]) # Sort lowest to highest
    for i, s in enumerate(subj_list[:10], 1):
        md += f"| {i} | {s[0]} | {s[1]:,} | **{s[2]:.2f}%** |\n"

    md += """
### The 10 Easiest/Highest-Scoring Subjects
| Rank | Subject Name | Attempts | Avg Score (%) |
| :---: | :--- | :---: | :---: |
"""
    subj_list.sort(key=lambda x: x[2], reverse=True) # Sort highest to lowest
    for i, s in enumerate(subj_list[:10], 1):
        md += f"| {i} | {s[0]} | {s[1]:,} | **{s[2]:.2f}%** |\n"

    md += """
---

## 5. 👥 Demographic & Enrollment Trends
*Performance comparison based on enrollment type.*

| Enrollment Type | Total Students | Pass Rate | Average Score (%) |
| :--- | :---: | :---: | :---: |
"""
    for dtype, data in demographics.items():
        if data["total"] > 0:
            pass_rate = (data["passed"] / data["total"] * 100)
            avg_pct = (data["total_pct"] / data["valid_pct_count"]) if data["valid_pct_count"] > 0 else 0
            md += f"| **{dtype}** | {data['total']:,} | {pass_rate:.1f}% | {avg_pct:.1f}% |\n"

    md += """
---

## 6. ⚔️ Course vs. Course Comparison
*Which major programs are yielding the highest success rates?*

| Academic Program | Total Enrolled | Pass Rate | Avg Score (%) |
| :--- | :---: | :---: | :---: |
"""
    # Sort courses by total enrolled
    sorted_courses = sorted(course_compare.items(), key=lambda x: x[1]["total"], reverse=True)
    for course, data in sorted_courses:
        if data["total"] >= 50: # Only show major courses
            pass_rate = (data["passed"] / data["total"] * 100)
            avg_pct = (data["total_pct"] / data["valid_pct_count"]) if data["valid_pct_count"] > 0 else 0
            md += f"| **{course}** | {data['total']:,} | {pass_rate:.1f}% | {avg_pct:.1f}% |\n"

    # Save to desktop
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(md)

    print(f"\n✨ Absolute Success! Deep analytics report generated at: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_deep_report()
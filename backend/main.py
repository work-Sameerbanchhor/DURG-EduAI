from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import json
import glob
import os
import re
from collections import defaultdict

app = FastAPI(title="Durg University Ultimate Analytics API", version="3.0")

# --- CORS MIDDLEWARE ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for local development
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# --- GLOBAL IN-MEMORY DATABASE ---
DATABASE = []
ROLL_NUMBER_INDEX = {}

# --- HELPER FUNCTIONS ---
def safe_float(val, default=0.0):
    """Safely convert dirty strings to float."""
    if not val: return default
    try:
        clean_val = re.sub(r'[^\d.]', '', str(val))
        return float(clean_val) if clean_val else default
    except ValueError:
        return default

def get_base_course(exam_name):
    """Extracts base course name for grouping."""
    if "B.Sc." in exam_name.upper() or "BSC" in exam_name.upper(): return "B.Sc."
    if "B.A." in exam_name.upper() or " BA " in exam_name.upper(): return "B.A."
    if "B.COM" in exam_name.upper(): return "B.Com."
    if "M.Sc." in exam_name.upper() or "MSC" in exam_name.upper(): return "M.Sc."
    if "M.A." in exam_name.upper() or " MA " in exam_name.upper(): return "M.A."
    return "Other Programs"

# --- STARTUP LOGIC ---
@app.on_event("startup")
def load_data():
    global DATABASE, ROLL_NUMBER_INDEX
    print("🚀 Booting up API and loading massive datasets into memory...")
    
    json_files = glob.glob("*.json") 
    for file in json_files:
        print(f"Loading {file}...")
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                DATABASE.extend(data)
        except Exception as e:
            print(f"❌ Could not load {file}: {e}")
            
    # Create O(1) lookup index for ultra-fast Roll Number searches
    for student in DATABASE:
        if "roll_number" in student:
            ROLL_NUMBER_INDEX[student["roll_number"]] = student
            
    print(f"✅ Server Ready! Loaded {len(DATABASE):,} total student records into RAM.")

# ==========================================
# 1. CORE SEARCH & FILTER ENDPOINTS
# ==========================================

@app.get("/")
def read_root():
    return {"message": "API is live. Navigate to http://127.0.0.1:8000/docs for the interactive dashboard."}

@app.get("/api/v1/student/{roll_number}")
def get_by_roll_number(roll_number: str):
    student = ROLL_NUMBER_INDEX.get(roll_number)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@app.get("/api/v1/search")
def search_by_name(name: str = Query(..., min_length=3), limit: int = 50):
    """
    Search by student name with smart space normalization.
    Fixes the "double space" issue from dirty university data.
    """
    query = " ".join(name.lower().split())
    
    results = []
    for s in DATABASE:
        if "name" in s:
            normalized_db_name = " ".join(s["name"].lower().split())
            if query in normalized_db_name:
                results.append(s)
                
    if not results:
        raise HTTPException(status_code=404, detail="No students found matching that name")
                
    return {"count": len(results), "results": results[:limit]}

@app.get("/api/v1/filter")
def filter_results(
    status: Optional[str] = None,
    course: Optional[str] = None,
    college: Optional[str] = None,
    limit: int = 50
):
    results = DATABASE
    if status: results = [s for s in results if s.get("result_status", "").lower() == status.lower()]
    if course: results = [s for s in results if course.lower() in s.get("exam_name", "").lower()]
    if college: results = [s for s in results if college.lower() in s.get("college", "").lower()]
    return {"count": len(results), "results": results[:limit]}

# ==========================================
# 2. UNIVERSITY-WIDE ANALYTICS ENDPOINTS
# ==========================================

@app.get("/api/v1/analytics/overview")
def analyze_overview(course: Optional[str] = None, college: Optional[str] = None):
    dataset = DATABASE
    if course: dataset = [s for s in dataset if course.lower() in s.get("exam_name", "").lower()]
    if college: dataset = [s for s in dataset if college.lower() in s.get("college", "").lower()]

    if not dataset: raise HTTPException(status_code=404, detail="No data matches filters")

    status_counts = defaultdict(int)
    total_score, valid_score_count = 0, 0

    for s in dataset:
        status_counts[s.get("result_status", "UNKNOWN").upper()] += 1
        score = safe_float(s.get("grand_total_obtained"))
        if score > 0:
            total_score += score
            valid_score_count += 1

    return {
        "total_students": len(dataset),
        "status_breakdown": dict(status_counts),
        "pass_percentage": round((status_counts.get("PASS", 0) / len(dataset)) * 100, 2),
        "average_grand_total": round(total_score / valid_score_count, 2) if valid_score_count else 0
    }

@app.get("/api/v1/analytics/colleges")
def rank_colleges(course: Optional[str] = None):
    dataset = DATABASE
    if course: dataset = [s for s in dataset if course.lower() in s.get("exam_name", "").lower()]

    college_stats = defaultdict(lambda: {"total": 0, "passed": 0, "total_score": 0})

    for s in dataset:
        col = s.get("college", "UNKNOWN")
        college_stats[col]["total"] += 1
        if s.get("result_status", "").upper() == "PASS":
            college_stats[col]["passed"] += 1
        college_stats[col]["total_score"] += safe_float(s.get("grand_total_obtained"))

    ranking = []
    for col, stats in college_stats.items():
        if stats["total"] > 10: 
            ranking.append({
                "college": col,
                "total_students": stats["total"],
                "pass_percentage": round((stats["passed"] / stats["total"]) * 100, 2),
                "average_score": round(stats["total_score"] / stats["total"], 2)
            })

    return sorted(ranking, key=lambda x: x["pass_percentage"], reverse=True)

@app.get("/api/v1/analytics/subjects")
def subject_diagnostics(course: Optional[str] = None):
    dataset = DATABASE
    if course: dataset = [s for s in dataset if course.lower() in s.get("exam_name", "").lower()]

    subject_stats = defaultdict(lambda: {"attempts": 0, "total_marks_earned": 0, "max_marks_possible": 0})

    for s in dataset:
        for subj in s.get("subjects", []):
            name = " ".join(subj.get("subject_name", "Unknown").split())
            obtained = safe_float(subj.get("subject_total"))
            maximum = safe_float(subj.get("max_marks"))
            if maximum > 0:
                subject_stats[name]["attempts"] += 1
                subject_stats[name]["total_marks_earned"] += obtained
                subject_stats[name]["max_marks_possible"] += maximum

    diagnostics = []
    for name, stats in subject_stats.items():
        if stats["attempts"] > 100:
            avg_percentage = (stats["total_marks_earned"] / stats["max_marks_possible"]) * 100
            diagnostics.append({
                "subject_name": name,
                "total_attempts": stats["attempts"],
                "average_percentage": round(avg_percentage, 2)
            })

    return sorted(diagnostics, key=lambda x: x["average_percentage"])

# ==========================================
# 3. NEW: DEEP TARGETED COLLEGE ANALYTICS
# ==========================================

@app.get("/api/v1/analytics/college/{college_code}")
def college_deep_analytics(college_code: str):
    """
    Returns a massive payload of deep analytics exclusively for a single college.
    """
    college_data = []
    clean_college_name = f"College {college_code}"

    # 1. Isolate the specific college's data
    for s in DATABASE:
        col_str = s.get("college", "")
        # Match "331-..." or just "331"
        if col_str.startswith(f"{college_code}-") or col_str.split('-')[0].strip() == college_code:
            college_data.append(s)
            if clean_college_name == f"College {college_code}" and "-" in col_str:
                clean_college_name = " ".join(col_str.split('-')[1:]).strip()

    total_students = len(college_data)
    if total_students == 0:
        raise HTTPException(status_code=404, detail=f"No data found for college code: {college_code}")

    # 2. Setup Trackers
    status_counts = defaultdict(int)
    course_toppers_ug = defaultdict(list)
    course_toppers_pg = defaultdict(list)
    grade_bins = {"Distinction (>75%)": 0, "First Div (60-74.9%)": 0, "Second Div (45-59.9%)": 0, "Third Div (33-44.9%)": 0, "Fail/Supply (<33%)": 0}
    progression = {"y1_total": 0, "y2_total": 0, "y3_total": 0, "count": 0}
    subjects = defaultdict(lambda: {"attempts": 0, "earned": 0, "possible": 0})
    course_compare = defaultdict(lambda: {"total": 0, "passed": 0, "total_pct": 0, "valid_pct_count": 0})

    # 3. Crunch the Numbers
    for s in college_data:
        base_course = get_base_course(s.get("exam_name", ""))
        status = s.get("result_status", "UNKNOWN").upper().strip()
        status_counts[status] += 1

        obt = safe_float(s.get("grand_total_obtained"))
        max_m = safe_float(s.get("grand_max_marks"))
        pct = (obt / max_m * 100) if max_m > 0 else 0
        sgpa = safe_float(s.get("sgpa"))

        name = " ".join(s.get("name", "Unknown").split())
        is_pg = sgpa > 0 or "M." in base_course

        # Leaderboards
        record = {"name": name, "roll": s.get("roll_number"), "pct": round(pct, 2), "sgpa": sgpa}
        if is_pg: course_toppers_pg[base_course].append(record)
        else: course_toppers_ug[base_course].append(record)

        # Grade Distribution
        if not is_pg and max_m > 0:
            if pct >= 75: grade_bins["Distinction (>75%)"] += 1
            elif pct >= 60: grade_bins["First Div (60-74.9%)"] += 1
            elif pct >= 45: grade_bins["Second Div (45-59.9%)"] += 1
            elif pct >= 33: grade_bins["Third Div (33-44.9%)"] += 1
            else: grade_bins["Fail/Supply (<33%)"] += 1

        # Progression
        if "past_years" in s and s["past_years"]:
            y1 = safe_float(s["past_years"].get("first_year_obtained"))
            y2 = safe_float(s["past_years"].get("second_year_obtained"))
            if y1 > 0 and y2 > 0 and obt > 0:
                progression["y1_total"] += y1
                progression["y2_total"] += y2
                progression["y3_total"] += obt
                progression["count"] += 1

        # Subjects
        for subj in s.get("subjects", []):
            s_name = " ".join(subj.get("subject_name", "").split())
            s_max = safe_float(subj.get("max_marks"))
            if s_max > 0 and s_name:
                subjects[s_name]["attempts"] += 1
                subjects[s_name]["earned"] += safe_float(subj.get("subject_total"))
                subjects[s_name]["possible"] += s_max

        # Course Compare
        course_compare[base_course]["total"] += 1
        if status == "PASS": course_compare[base_course]["passed"] += 1
        if max_m > 0:
            course_compare[base_course]["total_pct"] += pct
            course_compare[base_course]["valid_pct_count"] += 1

    # 4. Format Output Arrays
    # Format Leaderboards (Top 5 per course)
    ug_merit = {k: sorted(v, key=lambda x: x["pct"], reverse=True)[:5] for k, v in course_toppers_ug.items() if v}
    pg_merit = {k: sorted(v, key=lambda x: x["sgpa"], reverse=True)[:5] for k, v in course_toppers_pg.items() if v}

    # Format Subjects (Only min 10 attempts for college level)
    formatted_subjects = []
    for s_name, data in subjects.items():
        if data["attempts"] >= 10:
            formatted_subjects.append({
                "subject": s_name,
                "attempts": data["attempts"],
                "avg_score_pct": round((data["earned"] / data["possible"]) * 100, 2)
            })
    
    # Format Progression
    prog_data = None
    if progression["count"] > 0:
        c = progression["count"]
        prog_data = {
            "cohort_size": c,
            "y1_avg": round(progression["y1_total"] / c, 2),
            "y2_avg": round(progression["y2_total"] / c, 2),
            "y3_avg": round(progression["y3_total"] / c, 2)
        }

    # Format Course Performance
    course_perf = []
    for c_name, data in course_compare.items():
        if data["total"] > 0:
            course_perf.append({
                "course": c_name,
                "total_students": data["total"],
                "pass_rate": round((data["passed"] / data["total"]) * 100, 2),
                "avg_score_pct": round(data["total_pct"] / data["valid_pct_count"], 2) if data["valid_pct_count"] else 0
            })

    # 5. Return JSON Payload
    return {
        "college_code": college_code,
        "college_name": clean_college_name,
        "overview": {
            "total_students": total_students,
            "pass_rate": round((status_counts.get("PASS", 0) / total_students) * 100, 2),
            "status_breakdown": dict(status_counts)
        },
        "merit_lists": {
            "ug_toppers": ug_merit,
            "pg_toppers": pg_merit
        },
        "ug_grade_distribution": grade_bins,
        "ug_progression_trajectory": prog_data,
        "course_performance": sorted(course_perf, key=lambda x: x["total_students"], reverse=True),
        "toughest_subjects": sorted(formatted_subjects, key=lambda x: x["avg_score_pct"])[:10],
        "easiest_subjects": sorted(formatted_subjects, key=lambda x: x["avg_score_pct"], reverse=True)[:10]
    }
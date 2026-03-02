"""
DURG-EduAI — Feature Engineering Utilities
Author: Sameer Banchhor
DOI: https://doi.org/10.5281/zenodo.18826162
"""

import numpy as np


def to_float(v):
    """Safely convert a value to float, returning NaN on failure."""
    try:
        return float(str(v).strip())
    except (ValueError, TypeError):
        return np.nan


def extract_subject_features(subjects: list) -> dict:
    """
    Parse the subjects array from a student record and return
    aggregated numeric features.

    Parameters
    ----------
    subjects : list of dict
        Each dict follows the DURG-RESULTS JSON schema.

    Returns
    -------
    dict with keys:
        subject_totals, max_marks_list, theory_list,
        practical_list, sessional_list,
        fail_count, near_fail_count
    """
    subject_totals   = []
    max_marks_list   = []
    theory_list      = []
    practical_list   = []
    sessional_list   = []
    fail_count       = 0
    near_fail_count  = 0

    for s in subjects:
        st = to_float(s.get("subject_total", ""))
        mx = to_float(s.get("max_marks", ""))
        mn = to_float(s.get("min_marks", ""))
        tt = to_float(s.get("theory_total", ""))

        # Practical: sum all non-NaN components
        pm   = s.get("practical_marks", {})
        prac = sum(
            to_float(pm.get(k, ""))
            for k in ["I", "II", "sessional"]
            if not np.isnan(to_float(pm.get(k, "")))
        )

        # Sessional: sum all non-NaN components
        sm   = s.get("sessional_marks", {})
        sess = sum(
            to_float(sm.get(k, ""))
            for k in ["I", "II", "III"]
            if not np.isnan(to_float(sm.get(k, "")))
        )

        subject_totals.append(st)
        max_marks_list.append(mx)
        theory_list.append(tt)
        practical_list.append(prac if prac > 0 else np.nan)
        sessional_list.append(sess if sess > 0 else np.nan)

        # Count failed / near-failed subjects
        if not np.isnan(st) and not np.isnan(mn) and mn > 0:
            if st < mn:
                fail_count += 1
            elif st < mn * 1.3:
                near_fail_count += 1

    return {
        "subject_totals":  subject_totals,
        "max_marks_list":  max_marks_list,
        "theory_list":     theory_list,
        "practical_list":  practical_list,
        "sessional_list":  sessional_list,
        "fail_count":      fail_count,
        "near_fail_count": near_fail_count,
    }


def build_feature_vector(record: dict, source: str, artifacts: dict) -> dict:
    """
    Build the complete feature dictionary from a raw student record.

    Parameters
    ----------
    record   : raw student JSON record
    source   : 'msc' | 'ma' | 'other_pg' | 'ug'
    artifacts: loaded from artifacts.pkl

    Returns
    -------
    dict of all computed features
    """
    subjects = record.get("subjects", [])
    sf       = extract_subject_features(subjects)

    valid_totals = [x for x in sf["subject_totals"] if not np.isnan(x)]
    valid_max    = [x for x in sf["max_marks_list"]  if not np.isnan(x)]

    total_obtained = sum(valid_totals) if valid_totals else np.nan
    total_max      = sum(valid_max)    if valid_max    else np.nan
    percentage     = (total_obtained / total_max * 100) if total_max else np.nan

    mean_theory    = (np.nanmean(sf["theory_list"])
                      if any(~np.isnan(x) for x in sf["theory_list"])
                      else artifacts.get("theory_fill", 0))
    mean_practical = (np.nanmean(sf["practical_list"])
                      if any(~np.isnan(x) for x in sf["practical_list"])
                      else 0)
    mean_sessional = (np.nanmean(sf["sessional_list"])
                      if any(~np.isnan(x) for x in sf["sessional_list"])
                      else artifacts.get("sessional_fill", 0))
    has_practical  = int(any(~np.isnan(x) for x in sf["practical_list"]))

    # Categorical encodings
    source_enc  = artifacts["source_map"].get(source, 1)
    result_enc  = artifacts["result_status_map"].get(
        record.get("result_status", "").strip().upper(), -1
    )
    student_enc = 1 if record.get("student_type", "").upper() == "REGULAR" else 0

    # Min score percentage (for dropout risk)
    min_score   = np.nanmin(sf["subject_totals"]) if valid_totals else np.nan
    min_max_val = np.nanmin(sf["max_marks_list"]) if valid_max    else np.nan
    min_score_pct = (
        (min_score / min_max_val * 100)
        if (not np.isnan(min_score) and not np.isnan(min_max_val) and min_max_val > 0)
        else 50.0
    )

    # UG past-year features
    past   = record.get("past_years", {})
    py_max = to_float(past.get("second_year_max",  past.get("first_year_max",  "")))
    py_obt = to_float(past.get("second_year_obtained", past.get("first_year_obtained", "")))
    past_year_pct = (
        (py_obt / py_max * 100)
        if (not np.isnan(py_obt) and not np.isnan(py_max) and py_max > 0)
        else -1
    )

    return {
        "num_subjects":       len(subjects),
        "total_obtained":     total_obtained,
        "total_max":          total_max,
        "percentage":         percentage,
        "mean_subject_score": np.nanmean(sf["subject_totals"]) if valid_totals else np.nan,
        "std_subject_score":  np.nanstd(sf["subject_totals"])  if valid_totals else 0.0,
        "min_subject_score":  np.nanmin(sf["subject_totals"])  if valid_totals else np.nan,
        "max_subject_score":  np.nanmax(sf["subject_totals"])  if valid_totals else np.nan,
        "min_score_pct":      min_score_pct,
        "mean_theory":        mean_theory,
        "mean_practical":     mean_practical,
        "mean_sessional":     mean_sessional,
        "has_practical":      has_practical,
        "failed_subjects":    sf["fail_count"],
        "near_fail_subjects": sf["near_fail_count"],
        "result_enc":         result_enc,
        "student_enc":        student_enc,
        "source_enc":         source_enc,
        "past_year_pct":      past_year_pct,
        # raw lists (for subject analysis)
        "_subject_totals":    sf["subject_totals"],
        "_max_marks_list":    sf["max_marks_list"],
    }

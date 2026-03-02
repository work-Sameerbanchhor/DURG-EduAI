"""
DURG-EduAI — Core Inference Pipeline
Author: Sameer Banchhor
DOI: https://doi.org/10.5281/zenodo.18826162

Usage
-----
    from src.predict import load_models, analyze_student, print_report

    models = load_models()                          # load once
    report = analyze_student(record, "msc", models) # call per student
    print_report(report)
"""

import numpy as np
import pandas as pd
import joblib
from huggingface_hub import hf_hub_download

from src.features import build_feature_vector
from src.warnings_engine import generate_warnings

REPO = "sameerbanchhor-work/durg-EDU-ai-models"


# ── Model loader ──────────────────────────────────────────────────
def load_models(repo: str = REPO) -> dict:
    """
    Download and load all DURG-EduAI models from HuggingFace Hub.

    Returns
    -------
    dict with keys: xgb_sgpa, xgb_cls, xgb_drop,
                    artifacts, benchmarks,
                    features_cls, features_drop
    """
    def _load(fname):
        return joblib.load(hf_hub_download(repo_id=repo, filename=fname))

    print("Loading DURG-EduAI models from HuggingFace...")
    models = {
        "xgb_sgpa":      _load("xgb_sgpa_model.pkl"),
        "xgb_cls":       _load("xgb_result_classifier.pkl"),
        "xgb_drop":      _load("xgb_dropout_risk.pkl"),
        "artifacts":     _load("artifacts.pkl"),
        "benchmarks":    _load("subject_benchmarks.pkl"),
        "features_cls":  _load("result_classifier_features.pkl"),
        "features_drop": _load("dropout_risk_features.pkl"),
    }
    models["features_sgpa"] = models["artifacts"]["features"]
    print("All models loaded successfully.")
    return models


# ── Subject analysis ──────────────────────────────────────────────
def _analyze_subjects(subjects: list, benchmarks: dict) -> list:
    """Return per-subject analysis dicts with cohort comparison."""
    results = []
    for s in subjects:
        try:
            st  = float(str(s.get("subject_total", "")).strip())
            mx  = float(str(s.get("max_marks",     "")).strip())
            mn  = float(str(s.get("min_marks",     "")).strip())
            pct = (st / mx * 100) if mx > 0 else None
        except (ValueError, TypeError):
            st, mx, mn, pct = None, None, None, None

        code  = s.get("subject_code", "").strip()
        bench = benchmarks.get(code, {})

        status = "OK"
        if st is not None and mn is not None and mn > 0:
            if st < mn:
                status = "❌ FAIL"
            elif st < mn * 1.3:
                status = "⚠️  NEAR-FAIL"

        vs_avg = ""
        if bench and pct is not None:
            diff   = pct - bench["mean_pct"]
            vs_avg = f"{'↑' if diff >= 0 else '↓'}{abs(diff):.1f}% vs cohort avg"

        results.append({
            "code":             code,
            "name":             s.get("subject_name", ""),
            "obtained":         st,
            "max":              mx,
            "min":              mn,
            "pct":              round(pct, 1) if pct is not None else None,
            "status":           status,
            "vs_cohort_avg":    vs_avg,
            "cohort_fail_rate": f"{bench['fail_rate']:.1f}%" if bench else "N/A",
        })
    return results


# ── Main inference ────────────────────────────────────────────────
def analyze_student(record: dict, source: str, models: dict) -> dict:
    """
    Run the full DURG-EduAI prediction pipeline on a student record.

    Parameters
    ----------
    record  : raw student JSON record (DURG-RESULTS schema)
    source  : 'msc' | 'ma' | 'other_pg' | 'ug'
    models  : dict returned by load_models()

    Returns
    -------
    dict with all predictions and analysis
    """
    arts        = models["artifacts"]
    benchmarks  = models["benchmarks"]
    subjects    = record.get("subjects", [])

    fv = build_feature_vector(record, source, arts)

    # ── 1. SGPA Regression (PG only) ─────────────────────────
    sgpa_pred = None
    if source in ("msc", "ma", "other_pg"):
        feat = pd.DataFrame([[
            fv["num_subjects"],       fv["total_obtained"],    fv["total_max"],
            fv["percentage"],         fv["mean_subject_score"],fv["std_subject_score"],
            fv["min_subject_score"],  fv["max_subject_score"],
            fv["mean_theory"],        fv["mean_practical"],    fv["mean_sessional"],
            fv["has_practical"],      fv["result_enc"],
            fv["student_enc"],        fv["source_enc"],
        ]], columns=models["features_sgpa"])
        sgpa_pred = float(np.clip(models["xgb_sgpa"].predict(feat)[0], 0, 10))

    # ── 2. Result Classification ──────────────────────────────
    feat_cls = pd.DataFrame([[
        fv["num_subjects"],       fv["total_obtained"],     fv["total_max"],
        fv["percentage"],         fv["mean_subject_score"], fv["std_subject_score"],
        fv["min_subject_score"],  fv["max_subject_score"],
        fv["mean_theory"],        fv["mean_practical"],     fv["mean_sessional"],
        fv["has_practical"],      fv["failed_subjects"],
        fv["student_enc"],        fv["source_enc"],         fv["past_year_pct"],
    ]], columns=models["features_cls"])
    result_enc   = int(models["xgb_cls"].predict(feat_cls)[0])
    result_label = ["FAIL", "ATKT", "PASS"][result_enc]
    result_proba = models["xgb_cls"].predict_proba(feat_cls)[0]

    # ── 3. Dropout Risk ───────────────────────────────────────
    sgpa_for_drop   = sgpa_pred if sgpa_pred is not None else -1
    result_fail_flg = 1 if result_enc in (0, 1) else 0

    feat_drop = pd.DataFrame([[
        fv["num_subjects"],       fv["total_obtained"],     fv["total_max"],
        fv["percentage"],         fv["mean_subject_score"], fv["std_subject_score"],
        fv["min_subject_score"],  fv["max_subject_score"],  fv["min_score_pct"],
        fv["mean_theory"],        fv["mean_practical"],     fv["mean_sessional"],
        fv["has_practical"],      fv["failed_subjects"],    fv["near_fail_subjects"],
        sgpa_for_drop,            result_fail_flg,
        fv["student_enc"],        fv["source_enc"],         fv["past_year_pct"],
    ]], columns=models["features_drop"])
    drop_pred   = int(models["xgb_drop"].predict(feat_drop)[0])
    drop_proba  = models["xgb_drop"].predict_proba(feat_drop)[0]
    drop_label  = ["🟢 Low Risk", "🟡 Medium Risk", "🔴 High Risk"][drop_pred]

    # ── 4. Subject Analysis ───────────────────────────────────
    subject_analysis = _analyze_subjects(subjects, benchmarks)

    # ── 5. Early Warnings ─────────────────────────────────────
    warnings = generate_warnings(
        fv["failed_subjects"], fv["near_fail_subjects"],
        fv["percentage"], sgpa_pred, drop_pred
    )

    return {
        "student_name":    record.get("name", "Unknown"),
        "roll_number":     record.get("roll_number", ""),
        "exam_name":       record.get("exam_name", ""),
        "source":          source,
        # ── Predictions ─────────────────────────────────────
        "predicted_sgpa":  round(sgpa_pred, 2) if sgpa_pred is not None else None,
        "sgpa_band":       (
            f"{max(0, sgpa_pred-0.158):.2f} – {min(10, sgpa_pred+0.158):.2f}"
            if sgpa_pred is not None else None
        ),
        "predicted_result": result_label,
        "result_probabilities": {
            "FAIL": round(float(result_proba[0]), 4),
            "ATKT": round(float(result_proba[1]), 4),
            "PASS": round(float(result_proba[2]), 4),
        },
        "dropout_risk":  drop_label,
        "dropout_probabilities": {
            "Low":    round(float(drop_proba[0]), 4),
            "Medium": round(float(drop_proba[1]), 4),
            "High":   round(float(drop_proba[2]), 4),
        },
        # ── Analysis ────────────────────────────────────────
        "warnings":        warnings,
        "subjects":        subject_analysis,
        # ── Summary ─────────────────────────────────────────
        "total_obtained":  fv["total_obtained"],
        "total_max":       fv["total_max"],
        "percentage":      round(fv["percentage"], 2) if not np.isnan(fv["percentage"]) else None,
        "failed_subjects": fv["failed_subjects"],
    }


# ── Pretty printer ────────────────────────────────────────────────
def print_report(report: dict):
    """Print a formatted student analysis report to stdout."""
    W = 62
    print("\n" + "═" * W)
    print("  STUDENT ANALYSIS REPORT")
    print("═" * W)
    print(f"  Name       : {report['student_name']}")
    print(f"  Roll No    : {report['roll_number']}")
    print(f"  Exam       : {report['exam_name']}")
    print("─" * W)

    if report["predicted_sgpa"] is not None:
        print(f"  Predicted SGPA   : {report['predicted_sgpa']:.2f} / 10.0"
              f"  (95% band: {report['sgpa_band']})")
    else:
        print("  Predicted SGPA   : N/A (UG — annual system)")

    rp = report["result_probabilities"]
    print(f"  Predicted Result : {report['predicted_result']}")
    print(f"  Result Proba     : PASS {rp['PASS']*100:.1f}%  "
          f"ATKT {rp['ATKT']*100:.1f}%  FAIL {rp['FAIL']*100:.1f}%")

    dp = report["dropout_probabilities"]
    print(f"  Dropout Risk     : {report['dropout_risk']}")
    print(f"  Risk Proba       : Low {dp['Low']*100:.1f}%  "
          f"Med {dp['Medium']*100:.1f}%  High {dp['High']*100:.1f}%")

    pct = report["percentage"]
    print(f"  Overall %        : {pct}%  "
          f"({report['total_obtained']:.0f}/{report['total_max']:.0f})")
    print("─" * W)

    print("  ⚡ EARLY WARNINGS:")
    for w in report["warnings"]:
        print(f"     {w}")
    print("─" * W)

    print("  📚 SUBJECT-WISE BREAKDOWN:")
    print(f"  {'Code':<7} {'Subject':<36} {'Score':>8} {'%':>6}  {'Status':<14} Cohort")
    print("  " + "-" * 80)
    for s in report["subjects"]:
        score = (f"{s['obtained']:.0f}/{s['max']:.0f}"
                 if s["obtained"] is not None else "—/—")
        pct_s = f"{s['pct']}%" if s["pct"] else "—"
        print(f"  {s['code']:<7} {s['name'][:35]:<36} {score:>8} "
              f"{pct_s:>6}  {s['status']:<14} {s['vs_cohort_avg']}")
    print("═" * W)

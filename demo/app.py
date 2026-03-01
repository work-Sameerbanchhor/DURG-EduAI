"""
DURG-EduAI — Student Performance Prediction System
Gradio app for HuggingFace Spaces
Models: sameerbanchhor-work/durg-EDU-ai-models
"""

import gradio as gr
import joblib
import numpy as np
import pandas as pd
from huggingface_hub import hf_hub_download
import os

# ── Load all models from HuggingFace Hub ─────────────────────────
print("Loading models from HuggingFace Hub...")

REPO = "sameerbanchhor-work/durg-EDU-ai-models"

def load_model(filename):
    path = hf_hub_download(repo_id=REPO, filename=filename)
    return joblib.load(path)

xgb_sgpa       = load_model("xgb_sgpa_model.pkl")
xgb_cls        = load_model("xgb_result_classifier.pkl")
xgb_drop       = load_model("xgb_dropout_risk.pkl")
artifacts      = load_model("artifacts.pkl")
subj_bench     = load_model("subject_benchmarks.pkl")
FEATURES_CLS   = load_model("result_classifier_features.pkl")
FEATURES_DROP  = load_model("dropout_risk_features.pkl")
FEATURES_SGPA  = artifacts["features"]

print("All models loaded successfully!")

# ── Prediction logic ──────────────────────────────────────────────
def predict(
    source, student_type,
    num_subjects, total_obtained, total_max,
    mean_theory, mean_practical, mean_sessional,
    mean_subject_score, std_subject_score,
    min_subject_score, max_subject_score,
    failed_subjects, near_fail_subjects,
    has_practical, past_year_pct,
    result_status_known
):
    def to_f(v):
        try: return float(v)
        except: return 0.0

    num_subjects       = int(num_subjects)
    total_obtained     = to_f(total_obtained)
    total_max          = to_f(total_max)
    mean_theory        = to_f(mean_theory)
    mean_practical     = to_f(mean_practical)
    mean_sessional     = to_f(mean_sessional)
    mean_subject_score = to_f(mean_subject_score)
    std_subject_score  = to_f(std_subject_score)
    min_subject_score  = to_f(min_subject_score)
    max_subject_score  = to_f(max_subject_score)
    failed_subjects    = int(failed_subjects)
    near_fail_subjects = int(near_fail_subjects)
    has_practical_enc  = 1 if has_practical else 0
    past_year_pct      = to_f(past_year_pct) if past_year_pct else -1

    percentage = (total_obtained / total_max * 100) if total_max > 0 else 0.0

    source_enc = {"M.Sc. (MSC)": 0, "M.A. (MA)": 1, "Other PG": 2, "UG": 3}.get(source, 1)
    student_enc = 1 if student_type == "Regular" else 0
    result_enc = {"PASS": 2, "ATKT": 1, "FAIL": 0, "Unknown": -1}.get(result_status_known, -1)

    min_score_pct = (min_subject_score / (total_max / num_subjects) * 100) if (num_subjects > 0 and total_max > 0) else 50.0

    # ── 1. SGPA (PG only) ──────────────────────────────────────
    sgpa_pred = None
    sgpa_band = ""
    if source in ("M.Sc. (MSC)", "M.A. (MA)", "Other PG"):
        feat_sgpa = pd.DataFrame([[
            num_subjects, total_obtained, total_max, percentage,
            mean_subject_score, std_subject_score,
            min_subject_score, max_subject_score,
            mean_theory, mean_practical, mean_sessional,
            has_practical_enc, result_enc, student_enc, source_enc
        ]], columns=FEATURES_SGPA)
        sgpa_pred = float(np.clip(xgb_sgpa.predict(feat_sgpa)[0], 0, 10))
        mae = 0.0791
        sgpa_band = f"{max(0, sgpa_pred - 2*mae):.2f} – {min(10, sgpa_pred + 2*mae):.2f}"

    # ── 2. Result Classification ───────────────────────────────
    feat_cls = pd.DataFrame([[
        num_subjects, total_obtained, total_max, percentage,
        mean_subject_score, std_subject_score,
        min_subject_score, max_subject_score,
        mean_theory, mean_practical, mean_sessional,
        has_practical_enc, failed_subjects,
        student_enc, source_enc, past_year_pct
    ]], columns=FEATURES_CLS)
    result_enc_pred = int(xgb_cls.predict(feat_cls)[0])
    result_label    = ["FAIL", "ATKT", "PASS"][result_enc_pred]
    result_proba    = xgb_cls.predict_proba(feat_cls)[0]

    # ── 3. Dropout Risk ────────────────────────────────────────
    sgpa_for_drop = sgpa_pred if sgpa_pred is not None else -1
    result_fail_flag = 1 if result_enc_pred in (0, 1) else 0

    feat_drop = pd.DataFrame([[
        num_subjects, total_obtained, total_max, percentage,
        mean_subject_score, std_subject_score,
        min_subject_score, max_subject_score,
        min_score_pct, mean_theory, mean_practical, mean_sessional,
        has_practical_enc, failed_subjects, near_fail_subjects,
        sgpa_for_drop, result_fail_flag, student_enc, source_enc, past_year_pct
    ]], columns=FEATURES_DROP)
    drop_pred   = int(xgb_drop.predict(feat_drop)[0])
    drop_proba  = xgb_drop.predict_proba(feat_drop)[0]
    drop_label  = ["🟢 Low Risk", "🟡 Medium Risk", "🔴 High Risk"][drop_pred]

    # ── 4. Early Warnings ──────────────────────────────────────
    warnings = []
    if failed_subjects >= 1:
        warnings.append(f"🚨 Failed {failed_subjects} subject(s) — immediate academic support needed")
    if near_fail_subjects >= 2:
        warnings.append(f"⚠️  {near_fail_subjects} subjects near minimum threshold")
    if percentage < 45:
        warnings.append(f"⚠️  Overall percentage critically low ({percentage:.1f}%)")
    if sgpa_pred is not None and sgpa_pred < 5.0:
        warnings.append(f"⚠️  Predicted SGPA is very low ({sgpa_pred:.2f})")
    if drop_pred == 2:
        warnings.append("🚨 HIGH dropout risk — immediate intervention recommended")
    elif drop_pred == 1:
        warnings.append("⚠️  Medium dropout risk — monitor this student closely")
    if not warnings:
        warnings.append("✅ No major academic concerns detected")

    # ── Build output strings ───────────────────────────────────
    sgpa_out = (
        f"**{sgpa_pred:.2f}** / 10.0\n95% confidence band: {sgpa_band}"
        if sgpa_pred is not None else
        "N/A — SGPA prediction is for PG programs only"
    )

    result_out = (
        f"**{result_label}**\n\n"
        f"PASS: {result_proba[2]*100:.1f}%  |  "
        f"ATKT: {result_proba[1]*100:.1f}%  |  "
        f"FAIL: {result_proba[0]*100:.1f}%"
    )

    drop_out = (
        f"**{drop_label}**\n\n"
        f"Low: {drop_proba[0]*100:.1f}%  |  "
        f"Medium: {drop_proba[1]*100:.1f}%  |  "
        f"High: {drop_proba[2]*100:.1f}%"
    )

    warnings_out = "\n\n".join(warnings)

    summary_out = (
        f"**Overall %:** {percentage:.1f}%  ({total_obtained:.0f} / {total_max:.0f})\n"
        f"**Program:** {source}  |  **Type:** {student_type}\n"
        f"**Subjects:** {num_subjects}  |  **Failed:** {failed_subjects}  |  **Near-fail:** {near_fail_subjects}"
    )

    return sgpa_out, result_out, drop_out, warnings_out, summary_out


# ── Example presets ───────────────────────────────────────────────
EXAMPLES = [
    # [source, student_type, num_subj, total_obt, total_max, mean_th, mean_prac,
    #  mean_sess, mean_subj, std_subj, min_subj, max_subj, failed, near_fail,
    #  has_prac, past_yr_pct, result_known]
    ["M.Sc. (MSC)", "Regular", 6, 413, 600, 65, 84, 18, 68.8, 15.2, 41, 88, 0, 0, True,  None, "Unknown"],   # Good student
    ["M.Sc. (MSC)", "Regular", 6, 155, 600, 41, 57, 15, 25.8, 14.1, 14, 70, 2, 3, True,  None, "Unknown"],   # At-risk
    ["M.A. (MA)",   "Regular", 5, 320, 500, 63,  0, 20, 64.0, 10.5, 48, 80, 0, 1, False, None, "Unknown"],   # Average
    ["UG",          "Regular", 6, 280, 600, 45,  0, 16, 46.7, 12.3, 28, 65, 1, 2, False, 55.0, "Unknown"],   # UG borderline
]


# ── Gradio UI ─────────────────────────────────────────────────────
with gr.Blocks(
    theme=gr.themes.Base(
        primary_hue="blue",
        secondary_hue="slate",
        font=[gr.themes.GoogleFont("Inter"), "sans-serif"],
    ),
    title="DURG-EduAI — Student Prediction System",
    css="""
        .header-box { background: linear-gradient(135deg, #0D2B5E, #1A4A8A);
                      padding: 24px; border-radius: 12px; margin-bottom: 16px; }
        .header-box h1 { color: white !important; margin: 0 !important; font-size: 1.8em; }
        .header-box p  { color: #A8C4E8 !important; margin: 6px 0 0 0; }
        .output-card   { border-left: 4px solid #1A4A8A; padding-left: 12px; }
        footer { display: none !important; }
    """
) as demo:

    # ── Header ───────────────────────────────────────────────
    gr.HTML("""
        <div class="header-box">
            <h1>🎓 DURG-EduAI — Student Performance Prediction</h1>
            <p>Multi-task ML system · Hemchand Yadav University, Durg ·
               248,139 training records · Built by Sameer Banchhor</p>
        </div>
    """)

    gr.Markdown("""
    Enter a student's examination details below to get **5 simultaneous predictions**:
    SGPA · Result Status · Dropout Risk · Early Warnings · Performance Summary.
    Use the **Load Example** buttons to try preloaded student profiles.
    """)

    with gr.Row():
        with gr.Column(scale=1):
            # ── Student Info ──────────────────────────────
            gr.Markdown("### 🧑‍🎓 Student Info")
            source       = gr.Dropdown(["M.Sc. (MSC)", "M.A. (MA)", "Other PG", "UG"],
                                        value="M.Sc. (MSC)", label="Program")
            student_type = gr.Dropdown(["Regular", "Private", "Ex-Student"],
                                        value="Regular", label="Student Type")
            result_known = gr.Dropdown(["Unknown", "PASS", "ATKT", "FAIL"],
                                        value="Unknown", label="Known Result (optional)")

            # ── Marks Summary ─────────────────────────────
            gr.Markdown("### 📊 Marks Summary")
            with gr.Row():
                total_obtained = gr.Number(label="Total Marks Obtained", value=413, precision=0)
                total_max      = gr.Number(label="Total Maximum Marks",  value=600, precision=0)
            num_subjects   = gr.Slider(1, 12, value=6, step=1, label="Number of Subjects")

            # ── Subject Details ───────────────────────────
            gr.Markdown("### 📚 Subject-wise Breakdown")
            with gr.Row():
                mean_subject_score = gr.Number(label="Mean Subject Score", value=68.8)
                std_subject_score  = gr.Number(label="Std Dev of Scores",  value=15.2)
            with gr.Row():
                min_subject_score  = gr.Number(label="Min Subject Score",  value=41)
                max_subject_score  = gr.Number(label="Max Subject Score",  value=88)
            with gr.Row():
                failed_subjects    = gr.Slider(0, 12, value=0, step=1, label="Failed Subjects (below min marks)")
                near_fail_subjects = gr.Slider(0, 12, value=0, step=1, label="Near-fail Subjects (within 30% of min)")

            # ── Component Marks ───────────────────────────
            gr.Markdown("### 🧪 Component Averages")
            with gr.Row():
                mean_theory    = gr.Number(label="Mean Theory Marks",     value=65)
                mean_practical = gr.Number(label="Mean Practical Marks",  value=84)
            mean_sessional = gr.Number(label="Mean Sessional Marks",       value=18)
            has_practical  = gr.Checkbox(label="Has Practical Subjects?",  value=True)
            past_year_pct  = gr.Number(label="Past Year % (UG only, leave blank for PG)",
                                        value=None, precision=1)

            with gr.Row():
                clear_btn  = gr.Button("🗑️ Clear",   variant="secondary", size="sm")
                submit_btn = gr.Button("🔍 Predict", variant="primary",   size="lg")

        with gr.Column(scale=1):
            # ── Outputs ───────────────────────────────────
            gr.Markdown("### 📈 Predictions")
            sgpa_out    = gr.Markdown(label="SGPA Prediction",     elem_classes="output-card")
            gr.Markdown("---")
            result_out  = gr.Markdown(label="Result Status",       elem_classes="output-card")
            gr.Markdown("---")
            drop_out    = gr.Markdown(label="Dropout Risk",        elem_classes="output-card")
            gr.Markdown("---")

            gr.Markdown("### ⚡ Early Warning Alerts")
            warnings_out = gr.Markdown(elem_classes="output-card")
            gr.Markdown("---")

            gr.Markdown("### 📋 Summary")
            summary_out  = gr.Markdown(elem_classes="output-card")

    # ── Example buttons ───────────────────────────────────────
    gr.Markdown("---\n### 🧪 Load Example Student Profiles")
    with gr.Row():
        ex_labels = [
            "✅ High Performer (MSC)",
            "🔴 At-Risk Student (MSC)",
            "📊 Average Student (MA)",
            "🟡 Borderline UG",
        ]
        ex_btns = [gr.Button(label, size="sm") for label in ex_labels]

    all_inputs = [
        source, student_type, num_subjects, total_obtained, total_max,
        mean_theory, mean_practical, mean_sessional,
        mean_subject_score, std_subject_score,
        min_subject_score, max_subject_score,
        failed_subjects, near_fail_subjects,
        has_practical, past_year_pct, result_known
    ]
    all_outputs = [sgpa_out, result_out, drop_out, warnings_out, summary_out]

    def load_example(idx):
        ex = EXAMPLES[idx]
        return ex

    for i, btn in enumerate(ex_btns):
        btn.click(fn=lambda i=i: EXAMPLES[i], inputs=[], outputs=all_inputs)

    submit_btn.click(fn=predict, inputs=all_inputs, outputs=all_outputs)
    clear_btn.click(fn=lambda: [None]*5, outputs=all_outputs)

    # ── Footer info ───────────────────────────────────────────
    gr.Markdown("""
    ---
    **Model Details**  
    🔵 SGPA Regressor — XGBoost · R² = 0.9969 · MAE = 0.079 · 99.84% within ±0.5  
    🔵 Result Classifier — XGBoost · F1 = 0.99+ across PASS / ATKT / FAIL  
    🔵 Dropout Risk — XGBoost · 100% accuracy · Low / Medium / High tiers  
    🔵 Training data: 248,139 records · Hemchand Yadav University, Durg (2016–2025)  

    **Author:** Sameer Banchhor · MSc Computer Science · Hemchand Yadav University  
    **Dataset & Models:** [HuggingFace](https://huggingface.co/sameerbanchhor-work) ·
    **GitHub:** [work-sameerbanchhor](https://github.com/work-sameerbanchhor)
    """)

if __name__ == "__main__":
    demo.launch()
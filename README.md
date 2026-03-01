<div align="center">

<img src="https://img.shields.io/badge/Research-Published-brightgreen?style=for-the-badge&logo=academia" alt="Published"/>
<img src="https://img.shields.io/badge/DOI-10.5281%2Fzenodo.18826162-blue?style=for-the-badge&logo=zenodo" alt="DOI"/>
<img src="https://img.shields.io/badge/Python-3.9%2B-yellow?style=for-the-badge&logo=python" alt="Python"/>
<img src="https://img.shields.io/badge/XGBoost-Powered-orange?style=for-the-badge" alt="XGBoost"/>
<img src="https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey?style=for-the-badge" alt="License"/>

<br/><br/>

<h1>🎓 DURG-EduAI</h1>

<h3>A Multi-Task Machine Learning Framework for Student Academic Performance Prediction,<br/>Result Classification, and Dropout Risk Assessment in Indian Higher Education</h3>

<p>
  <a href="https://doi.org/10.5281/zenodo.18826162"><img src="https://zenodo.org/badge/DOI/10.5281/zenodo.18826162.svg" alt="DOI Badge"/></a>
  &nbsp;
  <a href="https://huggingface.co/collections/sameerbanchhor-work/durg-edu-ai"><img src="https://img.shields.io/badge/🤗%20HuggingFace-Models%20%26%20Dataset-yellow" alt="HuggingFace"/></a>
  &nbsp;
  <a href="https://orcid.org/0009-0000-7055-6336"><img src="https://img.shields.io/badge/ORCID-0009--0000--7055--6336-green?logo=orcid" alt="ORCID"/></a>
</p>

<p><strong>Sameer Banchhor</strong> · M.Sc. Computer Science · Hemchand Yadav University, Durg, Chhattisgarh, India</p>

</div>

---

## 📌 Overview

**DURG-EduAI** is the first large-scale, publicly released multi-task machine learning system trained on real Indian university examination data. The framework transforms raw student examination records into five simultaneous predictions — delivering a complete academic risk profile from a single structured input.

Trained on **248,139 student records** from Hemchand Yadav University, Durg (2016–2025), spanning undergraduate (UG) and postgraduate (PG) programs.

---

## 🏆 Key Results

| Task | Model | Metric | Score |
|------|-------|--------|-------|
| SGPA Regression | XGBoost | R² | **0.9969** |
| SGPA Regression | XGBoost | MAE | **0.079** |
| SGPA Regression | XGBoost | Within ±0.5 | **99.84%** |
| Result Classification (PASS/FAIL/ATKT) | XGBoost | Macro F1 | **1.00** |
| Dropout Risk (Low/Medium/High) | XGBoost | Accuracy | **100%** |

---

## 🔮 Five Prediction Tasks

```
Single Student Record (JSON)
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│                    DURG-EduAI Pipeline                  │
├──────────┬──────────┬────────────┬──────────┬───────────┤
│   SGPA   │  Result  │  Dropout   │ Subject  │   Early   │
│Regression│  Status  │   Risk     │  Bench-  │  Warning  │
│          │PASS/FAIL │Low/Med/High│  marks   │  System   │
│R²=0.9969 │ ATKT     │            │161 subjs │5 signals  │
└──────────┴──────────┴────────────┴──────────┴───────────┘
```

---

## 📂 Repository Structure

```
DURG-EduAI/
│
├── 📄 README.md                    ← You are here
├── 📄 LICENSE
├── 📄 CITATION.cff                 ← Cite this work
│
├── 📁 notebooks/
│   └── DURG_EDU_AI_notebook.ipynb
│
├── 📁 src/
│   ├── predict.py                  ← Core inference function
│   ├── features.py                 ← Feature engineering utils
│   └── warnings_engine.py          ← Early warning logic
│
├── 📁 demo/
│   └── app.py                      ← Gradio HuggingFace Space app
│
├── 📁 figures/                     ← All paper figures
│   ├── fig1_dataset.png
│   ├── fig2_sgpa.png
│   ├── fig3_errors.png
│   ├── fig4_importance.png
│   ├── fig5_classification.png
│   ├── fig6_subjects.png
│   └── fig7_summary.png
│
└── 📄 requirements.txt
```

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/work-sameerbanchhor/DURG-EduAI.git
cd DURG-EduAI
pip install -r requirements.txt
```

### 2. Load Models from HuggingFace

```python
from huggingface_hub import hf_hub_download
import joblib

REPO = "sameerbanchhor-work/durg-EDU-ai-models"

xgb_sgpa   = joblib.load(hf_hub_download(REPO, "xgb_sgpa_model.pkl"))
xgb_cls    = joblib.load(hf_hub_download(REPO, "xgb_result_classifier.pkl"))
xgb_drop   = joblib.load(hf_hub_download(REPO, "xgb_dropout_risk.pkl"))
artifacts  = joblib.load(hf_hub_download(REPO, "artifacts.pkl"))
benchmarks = joblib.load(hf_hub_download(REPO, "subject_benchmarks.pkl"))
```

### 3. Run a Prediction

```python
from src.predict import analyze_student

# Example: M.Sc. Chemistry student
record = {
    "name": "STUDENT NAME",
    "roll_number": "2530577006",
    "exam_name": "M.Sc. CHEMISTRY - FIRST SEMESTER",
    "result_status": "",
    "student_type": "REGULAR",
    "subjects": [
        {
            "subject_code": "101",
            "subject_name": "GROUP THEORY",
            "max_marks": "100", "min_marks": "36",
            "theory_marks": {"I": "64", "II": "", "III": ""},
            "sessional_marks": {"I": "18", "II": "", "III": ""},
            "theory_total": "64",
            "practical_marks": {"I": "", "II": "", "sessional": ""},
            "subject_total": "64",
            "status": ""
        },
        # ... more subjects
    ]
}

report = analyze_student(record, source="msc")
print_report(report)
```

### 4. Expected Output

```
════════════════════════════════════════════════════════════
  STUDENT ANALYSIS REPORT
════════════════════════════════════════════════════════════
  Predicted SGPA   : 7.20
  Predicted Result : PASS  (PASS 100.0% | ATKT 0.0% | FAIL 0.0%)
  Dropout Risk     : 🟢 Low  (Low 100.0% | Med 0.0% | High 0.0%)
  Overall %        : 68.83%  (413 / 600)
────────────────────────────────────────────────────────────
  ⚡ EARLY WARNINGS:
     ✅  No major concerns detected
════════════════════════════════════════════════════════════
```

---

## 📊 Dataset

| Source | Records | SGPA | Years |
|--------|---------|------|-------|
| M.Sc. | 44,921 | ✅ 40,318 | 2016–2025 |
| M.A. | 66,781 | ✅ 62,223 | 2016–2025 |
| Other PG | 30,433 | ✅ 27,292 | 2018–2025 |
| UG (B.A./B.Sc./B.Com.) | 106,405 | ❌ Annual system | 2016–2025 |
| **Total** | **248,539** | **129,833** | **2016–2025** |

📦 **Dataset on HuggingFace:** [sameerbanchhor-work/DURG-RESULTS](https://huggingface.co/datasets/sameerbanchhor-work/DURG-RESULTS)

---

## 🧠 Model Architecture

### Feature Engineering (15-dim vector for SGPA, 16-dim for classification)

| Feature Group | Features |
|--------------|----------|
| Aggregate | `total_obtained`, `total_max`, `percentage` |
| Subject distribution | `mean`, `std`, `min`, `max` of subject totals |
| Component means | `mean_theory`, `mean_practical`, `mean_sessional` |
| Structural | `has_practical`, `num_subjects`, `failed_subjects`, `near_fail_subjects` |
| Categorical | `student_type_enc`, `source_enc` |
| UG historical | `past_year_pct` |

### Dropout Risk — 6-Signal Engineering

```
Signal S1: result_status ∈ {FAIL, ATKT}       → +1
Signal S2: SGPA < 5.0                          → +1
Signal S3: percentage < 45%                    → +1
Signal S4: failed_subjects ≥ 2                 → +1
Signal S5: min_subject_score_pct < 25%         → +1
Signal S6: near_fail_subjects ≥ 3              → +1
─────────────────────────────────────────────────
0 signals  → 🟢 Low Risk
1-2 signals → 🟡 Medium Risk
3+ signals  → 🔴 High Risk
```

---

## 🖥️ Live Demo

Try the model live on HuggingFace Spaces:

[![HuggingFace Space](https://img.shields.io/badge/🤗%20Try%20Live%20Demo-HuggingFace%20Spaces-yellow?style=for-the-badge)](https://huggingface.co/collections/sameerbanchhor-work/durg-edu-ai)

---

## 📄 Paper

> **Banchhor, S.** (2026). *DURG-EduAI: A Multi-Task Machine Learning Framework for Student Academic Performance Prediction, Result Classification, and Dropout Risk Assessment in Indian Higher Education*. Zenodo. https://doi.org/10.5281/zenodo.18826162

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18826162.svg)](https://doi.org/10.5281/zenodo.18826162)

---

## 📖 Citation

If you use this work, please cite:

```bibtex
@misc{banchhor2026durgai,
  author       = {Banchhor, Sameer},
  title        = {{DURG-EduAI: A Multi-Task Machine Learning Framework
                   for Student Academic Performance Prediction, Result
                   Classification, and Dropout Risk Assessment in
                   Indian Higher Education}},
  year         = {2026},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.18826162},
  url          = {https://doi.org/10.5281/zenodo.18826162}
}
```

---

## ⚠️ Limitations

- Dropout risk labels are **engineered proxies** from examination outcomes — not confirmed longitudinal withdrawal records
- High dropout accuracy partially reflects recoverability of the labeling logic
- Models are trained on a **single university** — generalization to other institutions is untested
- No demographic fairness analysis (gender, caste, geography) has been conducted

---

## 🔗 Links

| Resource | Link |
|----------|------|
| 📄 Paper (Zenodo) | https://doi.org/10.5281/zenodo.18826162 |
| 🤗 Models & Dataset | https://huggingface.co/collections/sameerbanchhor-work/durg-edu-ai |
| 🐙 GitHub | https://github.com/work-sameerbanchhor |
| 💼 LinkedIn | https://linkedin.com/in/sameer-banchhor-4a7373323 |
| 🔬 ORCID | https://orcid.org/0009-0000-7055-6336 |

---

## 📜 License

This work is licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).

You are free to share and adapt this work for any purpose, provided appropriate credit is given.

---

<div align="center">
  <sub>Built with ❤️ for Indian education · Hemchand Yadav University, Durg, Chhattisgarh</sub>
</div>

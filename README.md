<div align="center">

<h1>DURG-EduAI</h1>

<h3>University Result Analytics Platform & Multi-Task Academic Prediction Framework</h3>

<p><em>Hemchand Yadav University, Durg, Chhattisgarh, India · 248,539 student records · 2016–2025</em></p>

<p>
  <a href="https://analysis.durguniversity.workers.dev"><img src="https://img.shields.io/badge/Live_Dashboard-analysis.durguniversity.workers.dev-blue?style=for-the-badge" alt="Dashboard"/></a>
  <a href="https://sameerbanchhor-work-durg-university-result-api.hf.space"><img src="https://img.shields.io/badge/API-Hugging_Face_Spaces-yellow?style=for-the-badge" alt="API"/></a>
</p>
<p>
  <a href="https://doi.org/10.5281/zenodo.18826162"><img src="https://zenodo.org/badge/DOI/10.5281/zenodo.18826162.svg" alt="DOI"/></a>

  <a href="https://huggingface.co/collections/sameerbanchhor-work/durg-edu-ai"><img src="https://img.shields.io/badge/🤗%20HuggingFace-Models%20%26%20Dataset-yellow" alt="HuggingFace"/></a>
  <a href="https://orcid.org/0009-0000-7055-6336"><img src="https://img.shields.io/badge/ORCID-0009--0000--7055--6336-green?logo=orcid" alt="ORCID"/></a>
  <img src="https://img.shields.io/badge/Python-3.9%2B-yellow?logo=python" alt="Python"/>
  <img src="https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey" alt="License"/>
</p>

<p><strong>Sameer Banchhor</strong> · M.Sc. Computer Science · Hemchand Yadav University, Durg</p>

</div>

---

## Overview

**DURG-EduAI** is a full-stack academic intelligence system built on real examination data from Hemchand Yadav University. It has two integrated components:

- **DU Analysis** — A data pipeline, REST API, and interactive dashboard that makes university result data searchable, comparable, and analytically transparent for students, teachers, and administrators.
- **Prediction Model** — The first publicly released multi-task ML framework trained on Indian university data, delivering five simultaneous academic risk predictions from a single student record.

> Originally built as a final-year project at **Kalyan College, Bhilai, Durg (CG)** — now a published research artifact with a peer-reviewed DOI.

---

## Model Performance

| Task | Model | Metric | Score |
|------|-------|--------|-------|
| SGPA Regression | XGBoost | R² | **0.9969** |
| SGPA Regression | XGBoost | MAE | **0.079** |
| SGPA Regression | XGBoost | Within ±0.5 | **99.84%** |
| Result Classification (PASS/FAIL/ATKT) | XGBoost | Macro F1 | **1.00** |
| Dropout Risk (Low/Medium/High) | XGBoost | Accuracy | **99.21%** |

---

## Repository Structure

```
DURG-EduAI/
│
├── app.py                          # Root-level Gradio app entry point
├── requirements.txt
├── roll number structure.xlsx      # DU roll number format reference
├── CITATION.cff
│
├── Prediction_Model_training/      # ML model training & inference
│   ├── notebook/
│   │   └── DURG_EDU_AI_notebook.ipynb
│   └── src/
│       ├── predict.py              # Core inference function
│       ├── features.py             # Feature engineering
│       └── warnings_engine.py      # Early warning logic
│
├── frontend/                       # Dashboard UI (Cloudflare Workers)
│   └── public/
│       ├── index.html              # Home — Dashboard
│       ├── student.html            # Individual student result view
│       ├── analysis.html           # University & college-level analytics
│       ├── prediction.html         # Live ML prediction interface
│       ├── status.html             # Server overview
│       └── theme.js                # Dark/light mode toggle
│
├── backend/                        # REST API (FastAPI + Hugging Face Spaces)
│   ├── main.py                     # All API endpoints & analytics logic
│   ├── requirements.txt
│   └── Dockerfile
│
├── demo/
│   └── app.py                      # Gradio HuggingFace Space app
│
├── scraping/                       # Data collection & processing
│   ├── gather_dataset/
│   │   └── hemchand_Yadav_university_complete_result_scraper_.ipynb
│   ├── scrape_from_HTML/
│   │   ├── UG_result_scraper.py
│   │   ├── PG_result_scraper.py
│   │   └── generate_directory.py
│   └── other_analysis_stuff/
│       ├── analysis.py
│       └── deep_analysis_report.py
│
└── schemas/
    ├── UG_PG_schema.md
    ├── json_data_model.json
    └── result_dataset_directory.txt
```

---

## System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         DATA PIPELINE                            │
│                                                                  │
│  [Scraping]  ──▶  [Parsing]  ──▶  [JSON Datasets]  ──▶  [API]    │
│  Jupyter NB      Python/BS4       248,539 records    FastAPI     │
└──────────────────────────────────────────────────────────────────┘
                                          │
                    ┌─────────────────────┴──────────────────────┐
                    ▼                                            ▼
       ┌────────────────────────┐              ┌───────────────────────────┐
       │     DU ANALYSIS        │              │    PREDICTION MODEL       │
       │  Web Dashboard (CF)    │              │  XGBoost Multi-Task ML    │
       │                        │              │                           │
       │ • Student Search       │              │ • SGPA Regression         │
       │ • College Rankings     │              │ • Result Classification   │
       │ • Subject Diagnostics  │              │ • Dropout Risk            │
       │ • Merit Lists          │              │ • Subject Benchmarks      │
       │ • Progression Trends   │              │ • Early Warning Signals   │
       └────────────────────────┘              └───────────────────────────┘
```

---

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+ (for frontend dev server)

### Clone

```bash
git clone https://github.com/work-sameerbanchhor/DURG-EduAI.git
cd DURG-EduAI
pip install -r requirements.txt
```

### Run the Backend API

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
# Swagger docs at http://localhost:8000/docs
```

### Run the Frontend

```bash
cd frontend
npm install
npm run dev
# Dashboard at http://localhost:8787
```

### Run the Prediction Demo (Gradio)

```bash
python app.py
```

### Docker (Backend)

```bash
cd backend
docker build -t du-api .
docker run -p 7860:7860 du-api
```

---

## API Reference

### Core Search

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/student/{roll_number}` | Fetch a student's full result by roll number |
| `GET` | `/api/v1/search?name=...` | Search students by name (min 3 chars) |
| `GET` | `/api/v1/filter?status=...&course=...&college=...` | Filter by status, course, or college |

### University-Wide Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/analytics/overview` | Overall pass rates, status breakdown, averages |
| `GET` | `/api/v1/analytics/colleges` | Rank all colleges by pass percentage |
| `GET` | `/api/v1/analytics/subjects` | Subject-level difficulty diagnostics |
| `GET` | `/api/v1/analytics/college/{college_code}` | Full analytics for a single college |

> All analytics endpoints support optional `?course=` and `?college=` query parameters.

---

## Prediction Model

### Load Models from HuggingFace

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

### Run a Prediction

```python
from Prediction_Model_training.src.predict import analyze_student

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
        }
    ]
}

report = analyze_student(record, source="msc")
```

### Expected Output

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

## Model Details

### Feature Engineering

| Feature Group | Features |
|--------------|----------|
| Aggregate | `total_obtained`, `total_max`, `percentage` |
| Subject distribution | `mean`, `std`, `min`, `max` of subject totals |
| Component means | `mean_theory`, `mean_practical`, `mean_sessional` |
| Structural | `has_practical`, `num_subjects`, `failed_subjects`, `near_fail_subjects` |
| Categorical | `student_type_enc`, `source_enc` |
| UG historical | `past_year_pct` |

### Dropout Risk — 6-Signal Logic

```
S1: result_status ∈ {FAIL, ATKT}       → +1
S2: SGPA < 5.0                          → +1
S3: percentage < 45%                    → +1
S4: failed_subjects ≥ 2                 → +1
S5: min_subject_score_pct < 25%         → +1
S6: near_fail_subjects ≥ 3              → +1
─────────────────────────────────────────────
0 signals  → 🟢 Low Risk
1–2 signals → 🟡 Medium Risk
3+ signals  → 🔴 High Risk
```

---

## 📊 Dataset

| Source | Records | SGPA Available | Years |
|--------|---------|----------------|-------|
| M.Sc. | 44,921 | ✅ 40,318 | 2016–2025 |
| M.A. | 66,781 | ✅ 62,223 | 2016–2025 |
| Other PG | 30,433 | ✅ 27,292 | 2018–2025 |
| UG (B.A./B.Sc./B.Com.) | 106,405 | ❌ Annual system | 2016–2025 |
| **Total** | **248,539** | **129,833** | **2016–2025** |

📦 **Dataset:** [sameerbanchhor-work/DURG-RESULTS](https://huggingface.co/datasets/sameerbanchhor-work/DURG-RESULTS)

> If you prefer not to scrape from scratch, extract `datasets.zip` (3.4GB) containing all pre-downloaded HTML result pages.

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | HTML, CSS, JavaScript (vanilla) |
| Frontend Hosting | Cloudflare Workers |
| Backend | Python, FastAPI, Uvicorn |
| Backend Hosting | Hugging Face Spaces (Docker) |
| ML Models | XGBoost, Scikit-learn |
| Data Processing | Pandas, BeautifulSoup |
| Demo UI | Gradio |
| Notebooks | Jupyter / Google Colab |

---

## Limitations

- Dropout risk labels are **engineered proxies** derived from exam outcomes — not confirmed longitudinal withdrawal records.
- High dropout accuracy partially reflects the recoverability of the labeling logic.
- Models are trained on a **single university** — generalization to other institutions is untested.
- No demographic fairness analysis (gender, caste, geography) has been conducted.

---

## Citation

```bibtex
@misc{banchhor2026durgai,
  author    = {Banchhor, Sameer},
  title     = {{DURG-EduAI: A Multi-Task Machine Learning Framework for Student
                Academic Performance Prediction, Result Classification, and
                Dropout Risk Assessment in Indian Higher Education}},
  year      = {2026},
  publisher = {Zenodo},
  doi       = {10.5281/zenodo.18826162},
  url       = {https://doi.org/10.5281/zenodo.18826162}
}
```

---

## Links

| Resource | Link |
|----------|------|
| Live Dashboard | [analysis.durguniversity.workers.dev](https://analysis.durguniversity.workers.dev) |
| API | [sameerbanchhor-work-durg-university-result-api.hf.space](https://sameerbanchhor-work-durg-university-result-api.hf.space) |
| Colab Notebook | [Google Colab](https://colab.research.google.com/drive/1zW0SSNIBrZJ-Oiclgw2DD9cRar9RV1iI) |
| Paper (Zenodo) | [doi.org/10.5281/zenodo.18826162](https://doi.org/10.5281/zenodo.18826162) |
| Models & Dataset | [HuggingFace Collection](https://huggingface.co/collections/sameerbanchhor-work/durg-edu-ai) |
| GitHub | [github.com/work-sameerbanchhor](https://github.com/work-sameerbanchhor) |
| LinkedIn | [sameer-banchhor](https://linkedin.com/in/sameer-banchhor-4a7373323) |
| ORCID | [0009-0000-7055-6336](https://orcid.org/0009-0000-7055-6336) |

---

## 📜 License

This work is licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/). You are free to share and adapt this work for any purpose, provided appropriate credit is given.

---

## Contributing

Contributions, suggestions, and bug reports are welcome!

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push and open a Pull Request

> Want to adapt this system for your own university? Feel free to reach out!

---

<div align="center">
  <sub>Built with ❤️ for Indian education · Hemchand Yadav University, Durg, Chhattisgarh</sub>
</div>
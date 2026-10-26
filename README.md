# Beacon — AI-Powered Early Warning System for Student Dropout Prediction

Beacon is a human-supervised decision-support platform that helps faculty and academic advisors identify students at risk of academic failure or dropout. It processes academic performance and attendance data uploaded as CSV/XLSX files, generates batch risk predictions, and provides SHAP-based explanations for each student.

Beacon does **not** make automatic decisions about students. Its purpose is to support early counselling, remedial teaching, and intervention planning.

---

## Architecture Overview

```
+-----------------------------+
| React Frontend |
| Upload, Dashboard, Alerts |
+--------------+--------------+
| JSON / multipart upload
v
+-----------------------------+
| FastAPI Backend |
| Authentication & Routing |
+--------------+--------------+
|
v
+-----------------------------+
| SQLAlchemy + SQLite DB |
| Users, Students, Records, |
| Predictions, Interventions |
+--------------+--------------+
|
v
+-----------------------------+
| CSV / XLSX Data Upload |
| Academic + Attendance Data |
+--------------+--------------+
|
v
+-----------------------------+
| Preprocessing Pipeline |
| Cleaning, Encoding, Scaling|
+--------------+--------------+
|
v
+-----------------------------+
| Trained ML Classifier |
| Random Forest / XGBoost |
+--------------+--------------+
|
v
+-----------------------------+
| SHAP Explainability Layer |
| Top Risk Factor Detection |
+--------------+--------------+
|
v
+-----------------------------+
| Advisor Dashboard Response |
| Risk Score, Category, |
| Explanations, Alerts |
+-----------------------------+
```

---


---

## Key Features

- **CSV / Excel batch upload**: Faculty can upload student academic and attendance records using `.csv` or `.xlsx` files.
- **Academic and attendance analysis**: Uses internal/series marks, end-semester examination marks, subject-wise attendance, and assignment performance.
- **Batch risk prediction**: Processes multiple student records in one request instead of requiring individual form submissions.
- **Risk stratification**: Automatically classifies students into:
  - **Low Risk** — probability below 0.35
  - **Medium Risk** — probability from 0.35 to below 0.70
  - **High Risk** — probability 0.70 or above
- **SHAP-based explanations**: Identifies the main factors contributing to each student’s predicted risk.
- **Advisor alerts**: High-risk students are highlighted for follow-up and counselling.
- **Intervention tracking**: Advisors can record counselling, remedial actions, and follow-up outcomes.
- **Role-based access**: Supports separate modules for administrators, faculty/advisors, and students.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React, JavaScript, CSS |
| Backend | Python, FastAPI |
| Database | SQLite with SQLAlchemy ORM |
| Machine Learning | Scikit-learn, Pandas, NumPy |
| Model Explainability | SHAP |
| Data Upload | Pandas, openpyxl |
| API Communication | REST APIs with JSON |
| Model Persistence | Joblib |

---

## Directory Structure

```text
beacon/
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI application entrypoint
│   │   ├── database.py           # SQLAlchemy database connection
│   │   ├── models.py             # Database tables / ORM models
│   │   ├── schemas.py            # Pydantic request-response schemas
│   │   ├── routes/
│   │   │   ├── auth.py           # Login and role-based access
│   │   │   ├── students.py       # Student management endpoints
│   │   │   ├── upload.py         # CSV / XLSX upload endpoints
│   │   │   ├── predictions.py    # Risk prediction endpoints
│   │   │   ├── alerts.py         # Advisor alert endpoints
│   │   │   └── interventions.py  # Counselling / intervention records
│   │   ├── services/
│   │   │   ├── data_processor.py # Data cleaning and preprocessing
│   │   │   ├── predictor.py      # Model loading and batch inference
│   │   │   └── explainer.py      # SHAP explanation generation
│   │   └── utils/
│   ├── ml/
│   │   ├── training.py           # Model training and evaluation
│   │   ├── model.pkl             # Trained classifier artifact
│   │   ├── scaler.pkl            # Fitted preprocessing scaler
│   │   └── feature_columns.json  # Expected input feature names
│   ├── data/
│   │   ├── sample_students.csv   # Example upload file
│   │   └── beacon.db             # SQLite database
│   ├── requirements.txt
│   └── .venv/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/api.js       # Axios / fetch API calls
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
└── README.md
```

---

## Installation & Local Setup

### 1. Prerequisites

- Python 3.10 or higher
- Node.js and npm
- Git

### 2. Clone the Repository

```bash
git clone [https://github.com/](https://github.com/)<your-username>/beacon.git
cd beacon
```

### 3. Backend Setup

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# Linux / macOS
source .venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run the Backend

```bash
uvicorn app.main:app --reload
```

The backend will start at:

```text
http://127.0.0.1:8000
```

FastAPI interactive documentation is available at:

```text
http://127.0.0.1:8000/docs
```

### 5. Frontend Setup

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

The React application will start at:

```text
http://127.0.0.1:5173
```

---

## API Documentation

### 1. Health Check

**Endpoint:** `GET /api/health`

**Response:**

```json
{
  "status": "healthy",
  "service": "Beacon Backend",
  "version": "1.0.0"
}
```

### 2. Upload Student Data

**Endpoint:** `POST /api/upload/students`

**Headers:**

```text
Content-Type: multipart/form-data
```

**Request:** Upload a `.csv` or `.xlsx` file containing academic and attendance records.

**Example columns:**

```text
student_id
student_name
department
semester
subject_code
internal_marks
series_test_marks
end_semester_marks
assignment_score
attendance_percentage
```

**Response:**

```json
{
  "message": "Student data uploaded successfully",
  "records_processed": 120,
  "students_created": 60,
  "invalid_rows": 0
}
```

### 3. Generate Batch Risk Predictions

**Endpoint:** `POST /api/predictions/batch`

**Response:**

```json
{
  "batch_id": "BATCH-2026-001",
  "students_processed": 60,
  "high_risk_count": 8,
  "medium_risk_count": 17,
  "low_risk_count": 35,
  "results": [
    {
      "student_id": "STU-2024-089",
      "student_name": "Student A",
      "risk_probability": 0.784,
      "risk_category": "High",
      "top_risk_factors": [
        "Low attendance percentage",
        "Low end-semester marks",
        "Low assignment score"
      ],
      "shap_explanations": [
        {
          "feature": "attendance_percentage",
          "impact": -0.31
        },
        {
          "feature": "end_semester_marks",
          "impact": -0.24
        }
      ]
    }
  ]
}
```

### 4. Get Student Prediction

**Endpoint:** `GET /api/predictions/{student_id}`

**Response:**

```json
{
  "student_id": "STU-2024-089",
  "risk_probability": 0.784,
  "risk_category": "High",
  "action_required": true,
  "top_risk_factors": [
    "Low attendance percentage",
    "Low end-semester marks",
    "Low assignment score"
  ],
  "generated_at": "2026-10-26T16:50:00Z"
}
```

### 5. Record Intervention

**Endpoint:** `POST /api/interventions`

**Request:**

```json
{
  "student_id": "STU-2024-089",
  "advisor_id": 3,
  "intervention_type": "counselling",
  "notes": "Discussed attendance issues and scheduled remedial session.",
  "follow_up_date": "2026-11-05"
}
```

---

## Model Training & Evaluation

- **Training data:** Public higher-education student performance datasets, adapted to Beacon’s academic and attendance feature set.
- **Model candidates:** Random Forest Classifier and XGBoost Classifier.
- **Final model:** The model with the stronger recall, F1-score, and usable SHAP explanation quality.
- **Primary evaluation metrics:**
  - Accuracy
  - Precision
  - Recall
  - F1-score
  - ROC-AUC
- **Priority metric:** Recall, because missing genuinely at-risk students is more harmful than issuing additional advisor alerts.

---

## Ethical Use

Beacon is intended as a **decision-support tool**, not an automated judgement system. Risk predictions should be reviewed by faculty or advisors before any intervention. Predictions must be used to offer academic support, counselling, and remedial assistance—not to penalise, label, or exclude students.

---

## Roadmap

- [ ] Add per-student SHAP contribution charts in the React dashboard.
- [ ] Add exportable PDF/Excel risk reports for faculty meetings.
- [ ] Add email or dashboard notification alerts for high-risk students.
- [ ] Add model retraining workflow using newly uploaded institutional data.
- [ ] Containerize the backend and frontend using Docker.
- [ ] Add longitudinal tracking of student risk across semesters.

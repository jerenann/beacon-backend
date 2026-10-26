## Key Features

- **Automated Data Preprocessing**: Robust pipeline handling missing value imputation, one-hot encoding, and numerical normalization.
- **Probabilistic Risk Scoring**: Calibrated classification output providing probability percentiles alongside binary classifications.
- **Risk Stratification**: Automatic classification into actionable tiers:
  - 'Low Risk' ($p < 0.35$)
  - 'Moderate Risk' ($0.35 \\le p < 0.70$)
  - 'High Risk' ($p \\ge 0.70$)
- **RESTful Endpoints**: Clean, decoupled API endpoints returning structured JSON for frontend dashboards and client integrations.
- **Explainable Metrics**: Extraction of primary feature importance drivers to assist academic counselors.

---

## Tech Stack

- **Language**: Python 3.10+
- **Framework**: Flask
- **Machine Learning & Data**: Scikit-Learn, Pandas, NumPy, Joblib
- **Database / ORM**: SQLite / SQLAlchemy
- **Environment & Quality**: Flake8, Virtualenv

---

## Directory Structure

```text
student-dropout-predictor-backend/
├── api/
│   ├── __init__.py
│   ├── routes.py            # API routing & endpoint handlers
│   └── validators.py        # Request validation logic
├── core/
│   ├── __init__.py
│   ├── preprocessor.py      # Data cleaning, encoding & scaling
│   └── predictor.py         # Model loader & inference logic
├── models/
│   ├── model.pkl            # Serialized trained model artifact
│   └── scaler.pkl           # Fitted preprocessing scaler
├── data/
│   └── sample_input.json    # Example payload for testing
├── tests/
│   └── test_api.py          # Unit & integration tests
├── app.py                   # Application entrypoint
├── requirements.txt         # Project dependencies
├── .gitignore
└── README.md

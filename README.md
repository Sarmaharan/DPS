# DPS - AI-Based Diabetes Prediction & Patient Management System

A full-stack web application for diabetes risk prediction using machine learning, with patient management, analytics, and role-based access control.

## Features

- **Patient Registration** - Register and manage patient demographic data
- **Machine Learning Prediction** - AI-based diabetes risk assessment using multiple models
- **Multi-Model Comparison** - Compare predictions across Logistic Regression, Random Forest, SVM, Gradient Boosting, and XGBoost
- **Risk Classification** - Low, Medium, High risk levels based on prediction probability
- **Analytics Dashboard** - Overview of patients, predictions, risk distribution, and model accuracy
- **Report Generation** - PDF reports for patient history and system summary
- **Role-Based Login** - Admin, Doctor, Nurse, and Staff roles with appropriate permissions

## Quick Start

### 1. Create virtual environment

```bash
python -m venv venv
venv\Scripts\activate   # Windows
# or: source venv/bin/activate   # Linux/Mac
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
python run.py
```

Open http://localhost:5000 in your browser.

### Default Login Credentials

| Role  | Username | Password   |
|-------|----------|------------|
| Admin | admin    | admin123   |
| Doctor| doctor   | doctor123  |
| Staff | staff    | staff123   |

## Project Structure

```
DPS/
├── app/
│   ├── __init__.py      # App factory
│   ├── models.py        # User, Patient, Prediction models
│   ├── ml_engine.py     # ML models (Logistic Regression, RF, SVM, etc.)
│   ├── routes/          # Blueprints for auth, patients, prediction, dashboard, reports
│   └── templates/       # Jinja2 HTML templates
├── data/
│   └── diabetes.csv     # Pima Indians diabetes dataset
├── config.py
├── run.py
└── requirements.txt
```

## Clinical Features for Prediction

The system uses 8 input features based on the Pima Indians Diabetes dataset:

- Pregnancies
- Glucose (plasma, 2-hour)
- Blood Pressure (diastolic, mm Hg)
- Skin Thickness (triceps, mm)
- Insulin (2-hour serum, mu U/ml)
- BMI
- Diabetes Pedigree Function
- Age (years)

## Environment Variables

- `SECRET_KEY` - Flask secret key (set in production)
- `DATABASE_URL` - SQLite by default; use PostgreSQL URL for production

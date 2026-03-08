"""ML prediction and risk classification routes."""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Patient, Prediction, User
from app.ml_engine import MLEngine

prediction_bp = Blueprint('prediction', __name__)


def require_staff(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.can_manage_patients():
            flash('Access denied.', 'error')
            return redirect(url_for('dashboard.overview'))
        return f(*args, **kwargs)
    return decorated


@prediction_bp.route('/new', methods=['GET', 'POST'])
@login_required
@require_staff
def new():
    """Run diabetes prediction for a patient."""
    patients = Patient.query.order_by(Patient.last_name).all()
    
    if request.method == 'POST':
        patient_id = request.form.get('patient_id')
        features = {
            'Pregnancies': request.form.get('pregnancies', 0),
            'Glucose': request.form.get('glucose', 0),
            'BloodPressure': request.form.get('blood_pressure', 0),
            'SkinThickness': request.form.get('skin_thickness', 0),
            'Insulin': request.form.get('insulin', 0),
            'BMI': request.form.get('bmi', 0),
            'DiabetesPedigreeFunction': request.form.get('diabetes_pedigree', 0),
            'Age': request.form.get('age', 0),
        }
        
        result = MLEngine.predict(features)
        
        prediction = Prediction(
            patient_id=int(patient_id),
            pregnancies=features['Pregnancies'],
            glucose=features['Glucose'],
            blood_pressure=features['BloodPressure'],
            skin_thickness=features['SkinThickness'],
            insulin=features['Insulin'],
            bmi=features['BMI'],
            diabetes_pedigree=features['DiabetesPedigreeFunction'],
            age=features['Age'],
            risk_level=result['risk_level'],
            probability=result['probability'],
            primary_model=result['primary_model'],
            model_comparison=result['model_comparison'],
            predicted_by=current_user.id
        )
        db.session.add(prediction)
        db.session.commit()
        
        flash(f"Prediction complete. Risk: {result['risk_level'].upper()}", 'success')
        return render_template(
            'prediction/result.html',
            prediction=prediction,
            result=result,
            patient=Patient.query.get(int(patient_id))
        )
    
    return render_template('prediction/new.html', patients=patients)


@prediction_bp.route('/compare/<int:id>')
@login_required
def compare(id):
    """View multi-model comparison for a prediction."""
    prediction = Prediction.query.get_or_404(id)
    return render_template('prediction/compare.html', prediction=prediction)

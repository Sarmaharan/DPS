"""Patient registration and management routes."""
import uuid
from datetime import datetime
from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import db
from app.models import Patient, Prediction, User

patient_bp = Blueprint('patient', __name__)


def require_staff(f):
    """Decorator to require staff/doctor/admin role."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.can_manage_patients():
            flash('Access denied. Staff role required.', 'error')
            return redirect(url_for('dashboard.overview'))
        return f(*args, **kwargs)
    return decorated


@patient_bp.route('/')
@login_required
@require_staff
def list_patients():
    """List all patients."""
    patients = Patient.query.order_by(Patient.created_at.desc()).all()
    return render_template('patients/list.html', patients=patients)


@patient_bp.route('/register', methods=['GET', 'POST'])
@login_required
@require_staff
def register():
    """Register a new patient."""
    if request.method == 'POST':
        patient_id = f"P{datetime.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:4].upper()}"
        
        patient = Patient(
            patient_id=patient_id,
            first_name=request.form.get('first_name'),
            last_name=request.form.get('last_name'),
            date_of_birth=datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d').date(),
            gender=request.form.get('gender'),
            contact_number=request.form.get('contact_number'),
            email=request.form.get('email'),
            address=request.form.get('address'),
            registered_by=current_user.id
        )
        db.session.add(patient)
        db.session.commit()
        flash(f'Patient {patient_id} registered successfully.', 'success')
        return redirect(url_for('patient.view', id=patient.id))
    
    return render_template('patients/register.html')


@patient_bp.route('/<int:id>')
@login_required
@require_staff
def view(id):
    """View patient details and predictions."""
    patient = Patient.query.get_or_404(id)
    predictions = Prediction.query.filter_by(patient_id=patient.id).order_by(Prediction.created_at.desc()).all()
    return render_template('patients/view.html', patient=patient, predictions=predictions)


@patient_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@require_staff
def edit(id):
    """Edit patient details."""
    patient = Patient.query.get_or_404(id)
    if request.method == 'POST':
        patient.first_name = request.form.get('first_name')
        patient.last_name = request.form.get('last_name')
        patient.date_of_birth = datetime.strptime(request.form.get('date_of_birth'), '%Y-%m-%d').date()
        patient.gender = request.form.get('gender')
        patient.contact_number = request.form.get('contact_number')
        patient.email = request.form.get('email')
        patient.address = request.form.get('address')
        db.session.commit()
        flash('Patient updated successfully.', 'success')
        return redirect(url_for('patient.view', id=patient.id))
    return render_template('patients/edit.html', patient=patient)

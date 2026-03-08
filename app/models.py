"""Database models for DPS."""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class User(UserMixin, db.Model):
    """User model for role-based authentication."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # admin, doctor, nurse, staff
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def can_manage_patients(self):
        return self.role in ('admin', 'doctor', 'nurse', 'staff')


class Patient(db.Model):
    """Patient registration and demographic data."""
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    contact_number = db.Column(db.String(20))
    email = db.Column(db.String(120))
    address = db.Column(db.Text)
    registered_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    predictions = db.relationship('Prediction', backref='patient', lazy='dynamic')
    
    def __repr__(self):
        return f'<Patient {self.patient_id}>'


class Prediction(db.Model):
    """ML prediction results and risk classification."""
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    
    # Clinical features used for prediction
    pregnancies = db.Column(db.Float, nullable=False)
    glucose = db.Column(db.Float, nullable=False)
    blood_pressure = db.Column(db.Float, nullable=False)
    skin_thickness = db.Column(db.Float, nullable=False)
    insulin = db.Column(db.Float, nullable=False)
    bmi = db.Column(db.Float, nullable=False)
    diabetes_pedigree = db.Column(db.Float, nullable=False)
    age = db.Column(db.Float, nullable=False)
    
    # Prediction results
    risk_level = db.Column(db.String(20), nullable=False)  # low, medium, high
    probability = db.Column(db.Float, nullable=False)  # 0-1 probability
    primary_model = db.Column(db.String(50))  # Model that made primary prediction
    model_comparison = db.Column(db.JSON)  # All model predictions for comparison
    
    predicted_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Prediction {self.id} - {self.risk_level}>'

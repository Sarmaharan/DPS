"""Analytics dashboard routes."""
from flask import Blueprint, render_template
from flask_login import login_required
from app.models import Patient, Prediction, User
from app.ml_engine import MLEngine

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def overview():
    """Main analytics dashboard."""
    total_patients = Patient.query.count()
    total_predictions = Prediction.query.count()
    
    risk_breakdown = {'low': 0, 'medium': 0, 'high': 0}
    for p in Prediction.query.all():
        risk_breakdown[p.risk_level] = risk_breakdown.get(p.risk_level, 0) + 1
    
    model_metrics = MLEngine.get_model_metrics()
    
    return render_template(
        'dashboard/overview.html',
        total_patients=total_patients,
        total_predictions=total_predictions,
        risk_breakdown=risk_breakdown,
        model_metrics=model_metrics
    )

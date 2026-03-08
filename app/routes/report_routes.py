"""Report generation routes."""
from io import BytesIO
from datetime import datetime
from flask import Blueprint, send_file, make_response
from flask_login import login_required
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from app.models import Patient, Prediction

report_bp = Blueprint('report', __name__)


@report_bp.route('/patient/<int:patient_id>')
@login_required
def patient_report(patient_id):
    """Generate PDF report for a patient's predictions."""
    patient = Patient.query.get_or_404(patient_id)
    predictions = Prediction.query.filter_by(patient_id=patient_id).order_by(
        Prediction.created_at.desc()
    ).limit(10).all()
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72)
    styles = getSampleStyleSheet()
    story = []
    
    title = Paragraph(
        f"<b>Diabetes Risk Assessment Report</b><br/>Patient: {patient.first_name} {patient.last_name} ({patient.patient_id})",
        ParagraphStyle('title', parent=styles['Heading1'], fontSize=16)
    )
    story.append(title)
    story.append(Spacer(1, 0.3 * inch))
    
    info = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}<br/>DOB: {patient.date_of_birth}"
    story.append(Paragraph(info, styles['Normal']))
    story.append(Spacer(1, 0.5 * inch))
    
    if predictions:
        data = [['Date', 'Risk Level', 'Probability', 'Models Used']]
        for p in predictions:
            models = ', '.join([m['model'] for m in (p.model_comparison or [])[:3]])
            data.append([
                p.created_at.strftime('%Y-%m-%d'),
                p.risk_level.upper(),
                f"{p.probability:.2%}",
                models
            ])
        t = Table(data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black)
        ]))
        story.append(t)
    else:
        story.append(Paragraph("No predictions on record.", styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'DPS_Report_{patient.patient_id}_{datetime.now().strftime("%Y%m%d")}.pdf'
    )


@report_bp.route('/summary')
@login_required
def summary_report():
    """Generate summary analytics report."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72)
    styles = getSampleStyleSheet()
    story = []
    
    story.append(Paragraph("<b>DPS Analytics Summary Report</b>", ParagraphStyle('title', parent=styles['Heading1'], fontSize=16)))
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 0.5 * inch))
    
    total_patients = Patient.query.count()
    total_predictions = Prediction.query.count()
    
    risk_breakdown = {'low': 0, 'medium': 0, 'high': 0}
    for p in Prediction.query.all():
        risk_breakdown[p.risk_level] = risk_breakdown.get(p.risk_level, 0) + 1
    
    data = [
        ['Metric', 'Value'],
        ['Total Patients', str(total_patients)],
        ['Total Predictions', str(total_predictions)],
        ['Low Risk', str(risk_breakdown['low'])],
        ['Medium Risk', str(risk_breakdown['medium'])],
        ['High Risk', str(risk_breakdown['high'])]
    ]
    
    t = Table(data)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black)
    ]))
    story.append(t)
    doc.build(story)
    buffer.seek(0)
    
    return send_file(
        buffer,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'DPS_Summary_{datetime.now().strftime("%Y%m%d")}.pdf'
    )

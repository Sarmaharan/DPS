"""Authentication and role-based login routes."""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User

auth_bp = Blueprint('auth', __name__)

def init_default_users():
    """Create default admin and staff users if they don't exist."""
    if User.query.filter_by(username='admin').first() is None:
        admin = User(username='admin', email='admin@dps.local', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
    if User.query.filter_by(username='doctor').first() is None:
        doctor = User(username='doctor', email='doctor@dps.local', role='doctor')
        doctor.set_password('doctor123')
        db.session.add(doctor)
    if User.query.filter_by(username='staff').first() is None:
        staff = User(username='staff', email='staff@dps.local', role='staff')
        staff.set_password('staff123')
        db.session.add(staff)
    db.session.commit()


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.overview'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next') or url_for('dashboard.overview')
            return redirect(next_page)
        
        flash('Invalid username or password.', 'error')
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """User logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Staff registration (admin only in production)."""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'staff')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return render_template('auth/register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'error')
            return render_template('auth/register.html')
        
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash('User registered successfully.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html')

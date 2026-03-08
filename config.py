"""Configuration for DPS - Diabetes Prediction System."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

class Config:
    """Application configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dps-dev-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f'sqlite:///{BASE_DIR / "dps.db"}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DATA_PATH = BASE_DIR / 'data' / 'diabetes.csv'

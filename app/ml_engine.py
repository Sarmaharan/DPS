"""Machine Learning engine for diabetes prediction with multi-model comparison."""
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC

# Optional: XGBoost if available
try:
    from xgboost import XGBClassifier
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False

FEATURE_COLUMNS = [
    'Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness',
    'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age'
]
TARGET_COLUMN = 'Outcome'


class MLEngine:
    """Multi-model diabetes prediction engine."""
    
    _models = {}
    _scaler = None
    _trained = False
    _model_names = ['Logistic Regression', 'Random Forest', 'SVM', 'Gradient Boosting']
    
    @classmethod
    def _load_data(cls, data_path=None):
        """Load and preprocess diabetes dataset."""
        if data_path is None:
            data_path = Path(__file__).parent.parent / 'data' / 'diabetes.csv'
        
        df = pd.read_csv(data_path, header=None)
        df.columns = FEATURE_COLUMNS + [TARGET_COLUMN]
        
        # Replace zeros with median for key columns (common preprocessing)
        for col in ['Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI']:
            df[col] = df[col].replace(0, df[col].median())
        
        X = df[FEATURE_COLUMNS]
        y = df[TARGET_COLUMN]
        
        return train_test_split(X, y, test_size=0.2, random_state=42)
    
    @classmethod
    def train_models(cls, data_path=None):
        """Train all ML models on the diabetes dataset."""
        X_train, X_test, y_train, y_test = cls._load_data(data_path)
        
        cls._scaler = StandardScaler()
        X_train_scaled = cls._scaler.fit_transform(X_train)
        
        # Logistic Regression
        cls._models['logistic'] = LogisticRegression(random_state=42, max_iter=1000)
        cls._models['logistic'].fit(X_train_scaled, y_train)
        
        # Random Forest
        cls._models['random_forest'] = RandomForestClassifier(n_estimators=100, random_state=42)
        cls._models['random_forest'].fit(X_train_scaled, y_train)
        
        # SVM
        cls._models['svm'] = SVC(probability=True, random_state=42)
        cls._models['svm'].fit(X_train_scaled, y_train)
        
        # Gradient Boosting
        cls._models['gradient_boosting'] = GradientBoostingClassifier(random_state=42)
        cls._models['gradient_boosting'].fit(X_train_scaled, y_train)
        
        if HAS_XGBOOST:
            cls._models['xgboost'] = XGBClassifier(random_state=42)
            cls._models['xgboost'].fit(X_train_scaled, y_train)
            cls._model_names.append('XGBoost')
        
        cls._trained = True
    
    @classmethod
    def _get_risk_level(cls, probability):
        """Convert probability to risk classification."""
        if probability < 0.3:
            return 'low'
        elif probability < 0.7:
            return 'medium'
        else:
            return 'high'
    
    @classmethod
    def predict(cls, features_dict):
        """
        Run multi-model prediction and return comparison.
        features_dict: dict with keys matching FEATURE_COLUMNS
        """
        if not cls._trained:
            cls.train_models()
        
        # Build feature vector in correct order
        X = np.array([[
            float(features_dict.get('Pregnancies', 0)),
            float(features_dict.get('Glucose', 0)),
            float(features_dict.get('BloodPressure', 0)),
            float(features_dict.get('SkinThickness', 0)),
            float(features_dict.get('Insulin', 0)),
            float(features_dict.get('BMI', 0)),
            float(features_dict.get('DiabetesPedigreeFunction', 0)),
            float(features_dict.get('Age', 0)),
        ]])
        
        X_scaled = cls._scaler.transform(X)
        
        model_keys = ['logistic', 'random_forest', 'svm', 'gradient_boosting']
        if HAS_XGBOOST:
            model_keys.append('xgboost')
        
        comparison = []
        probabilities = []
        
        for i, key in enumerate(model_keys):
            model = cls._models[key]
            proba = model.predict_proba(X_scaled)[0][1]  # Probability of diabetes
            probabilities.append(proba)
            name = 'XGBoost' if key == 'xgboost' else cls._model_names[i]
            comparison.append({
                'model': name,
                'probability': round(float(proba), 4),
                'risk_level': cls._get_risk_level(proba),
                'prediction': int(proba >= 0.5)
            })
        
        # Primary prediction: ensemble average
        avg_prob = np.mean(probabilities)
        primary_model = 'Ensemble (Average)'
        
        return {
            'probability': round(float(avg_prob), 4),
            'risk_level': cls._get_risk_level(avg_prob),
            'primary_model': primary_model,
            'model_comparison': comparison,
            'prediction': int(avg_prob >= 0.5)
        }
    
    @classmethod
    def get_model_metrics(cls):
        """Get accuracy metrics for each model (for dashboard)."""
        if not cls._trained:
            cls.train_models()
        
        _, X_test, _, y_test = cls._load_data()
        X_test_scaled = cls._scaler.transform(X_test)
        
        metrics = []
        model_keys = ['logistic', 'random_forest', 'svm', 'gradient_boosting']
        if HAS_XGBOOST:
            model_keys.append('xgboost')
        
        for i, key in enumerate(model_keys):
            model = cls._models[key]
            acc = model.score(X_test_scaled, y_test)
            name = cls._model_names[i] if i < len(cls._model_names) else 'XGBoost'
            if key == 'xgboost':
                name = 'XGBoost'
            metrics.append({'model': name, 'accuracy': round(float(acc), 4)})
        
        return metrics

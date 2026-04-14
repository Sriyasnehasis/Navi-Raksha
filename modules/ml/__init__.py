"""
NaviRaksha ML Module
====================
Contains model loading and prediction utilities for ETA prediction.

Models available:
- Random Forest (rf_model.pkl) - Primary model, MAE: 0.0662 min
- LSTM (lstm_best_real.keras) - Alternative, temporal patterns
- GNN (gnn_graph_aware_final.pt) - Graph-aware, road network features

Usage:
    from modules.ml import load_rf_model, predict_eta
    
    model, scaler = load_rf_model()
    eta = predict_eta(model, scaler, distance=5.0, hour=14)
"""

import os
import numpy as np
import logging

logger = logging.getLogger(__name__)

# Path to trained models
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
MODELS_DIR = os.path.join(PROJECT_ROOT, 'models', 'trained')


def load_rf_model():
    """Load Random Forest model and feature scaler"""
    model_path = os.path.join(MODELS_DIR, 'rf_model.pkl')
    scaler_path = os.path.join(MODELS_DIR, 'rf_features.pkl')
    
    model = None
    scaler = None
    
    try:
        import joblib
        model = joblib.load(model_path)
        logger.info("RF model loaded successfully")
    except Exception as e:
        logger.warning(f"Could not load RF model: {e}")
    
    try:
        import pickle
        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)
        logger.info("Feature scaler loaded")
    except Exception as e:
        logger.warning(f"Could not load scaler: {e}")
    
    return model, scaler


def predict_eta(model, scaler, distance, hour, is_monsoon=False,
                ambulance_type=2, violations_zone=0):
    """
    Predict ETA using loaded RF model with fallback.
    
    Args:
        model: Trained RF model (or None for fallback)
        scaler: Feature scaler (or None for fallback)
        distance: Distance in km
        hour: Hour of day (0-23)
        is_monsoon: Boolean
        ambulance_type: 0=Bike, 1=Mini, 2=BLS, 3=ALS
        violations_zone: Violation count in zone
    
    Returns:
        ETA in minutes (float)
    """
    features = np.array([[distance, hour, int(is_monsoon), ambulance_type, violations_zone]])
    
    # Try model prediction
    if model is not None:
        try:
            if scaler is not None:
                if isinstance(scaler, list) and len(scaler) == 2:
                    features_scaled = (features - np.array(scaler[0])) / (np.array(scaler[1]) + 1e-8)
                else:
                    features_scaled = scaler.transform(features)
                eta = model.predict(features_scaled)[0]
            else:
                eta = model.predict(features)[0]
            return round(max(3, min(20, eta)), 2)
        except Exception as e:
            logger.warning(f"Model prediction failed: {e}")
    
    # Fallback heuristic
    base_speed = {0: 45, 1: 40, 2: 40, 3: 50}.get(ambulance_type, 40)
    
    # Time factor
    if 7 <= hour <= 9 or 16 <= hour <= 19:
        time_factor = 1.3
    elif 0 <= hour < 6 or hour >= 23:
        time_factor = 0.8
    else:
        time_factor = 1.0
    
    weather_factor = 1.2 if is_monsoon else 1.0
    violations_factor = 1.0 + (violations_zone * 0.1)
    
    effective_speed = base_speed / (time_factor * weather_factor * violations_factor)
    eta = (distance / effective_speed) * 60
    
    return round(max(3, min(20, eta)), 2)


# Model comparison results (from training notebooks)
MODEL_RESULTS = {
    'Random Forest': {'mae': 0.0662, 'rmse': 0.15, 'r2': 0.998, 'status': 'production'},
    'LSTM': {'mae': 0.1006, 'rmse': 0.2038, 'r2': 0.998, 'status': 'backup'},
    'GNN': {'mae': 0.1097, 'rmse': 0.2186, 'r2': 0.997, 'status': 'research'},
}

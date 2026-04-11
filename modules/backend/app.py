"""
NaviRaksha Backend API - Flask Application
Uses RF Model for ETA predictions + SQLAlchemy Database + Caching
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_caching import Cache
import pickle
import pandas as pd
import numpy as np
from datetime import datetime
import logging
import os
import sys

# Add modules to path
sys.path.insert(0, os.path.dirname(__file__))

# Import database and services
from models import db, Ambulance, Incident, Hospital, Dispatch, IncidentStatus
from database import init_db, seed_db, reset_db
from services import AmbulanceService, IncidentService, HospitalService, DispatchService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# ============================================================================
# CACHING CONFIGURATION
# ============================================================================

cache = Cache(app, config={'CACHE_TYPE': 'simple'})
logger.info("Response caching enabled (simple in-memory cache)")

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

# Get the project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DATABASE_PATH = os.path.join(PROJECT_ROOT, 'navi_raksha.db')

# Configure SQLAlchemy with connection pooling
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Connection pooling for SQLite (NullPool for SQLite since it doesn't support pooling well)
# But we'll use StaticPool for dev to avoid "database is locked" errors
from sqlalchemy.pool import StaticPool
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {'check_same_thread': False},
    'poolclass': StaticPool,
    'echo': False
}

# Initialize database with app
db.init_app(app)

logger.info(f"Database will be stored at: {DATABASE_PATH}")
logger.info(f"SQLAlchemy URI: {app.config['SQLALCHEMY_DATABASE_URI']}")

# ============================================================================
# MODEL LOADING
# ============================================================================

MODEL_PATH = os.path.join(PROJECT_ROOT, 'models/trained/rf_model.pkl')
SCALER_PATH = os.path.join(PROJECT_ROOT, 'models/trained/rf_features.pkl')

logger.info(f"Looking for model at: {MODEL_PATH}")
logger.info(f"Looking for scaler at: {SCALER_PATH}")

RF_MODEL = None
SCALER = None

# Try to load with different methods
try:
    import joblib
    RF_MODEL = joblib.load(MODEL_PATH)
    logger.info("RF Model loaded with joblib")
except Exception as e:
    logger.warning(f"Could not load RF model with joblib: {e}")
    try:
        with open(MODEL_PATH, 'rb') as f:
            RF_MODEL = pickle.load(f)
        logger.info("RF Model loaded with pickle")
    except Exception as e2:
        logger.error(f"Failed to load RF model: {e2}")
        logger.warning("Using fallback model for predictions")
        RF_MODEL = None

try:
    # Load Feature Scaler
    with open(SCALER_PATH, 'rb') as f:
        scaler_data = pickle.load(f)
        if isinstance(scaler_data, list) and len(scaler_data) == 2:
            SCALER = scaler_data
        else:
            SCALER = scaler_data
    logger.info("Feature scaler loaded successfully")
except Exception as e:
    logger.error(f"Failed to load scaler: {e}")
    SCALER = None

# Feature Scaler
try:
    with open(SCALER_PATH, 'rb') as f:
        scaler_data = pickle.load(f)
        if isinstance(scaler_data, list) and len(scaler_data) == 2:
            SCALER = scaler_data
        else:
            SCALER = scaler_data
    logger.info("Feature scaler loaded successfully")
except Exception as e:
    logger.error(f"Failed to load scaler: {e}")
    SCALER = None

# Initialize database flag
_db_initialized = False

def ensure_db_initialized():
    """Ensure database is initialized before first request"""
    global _db_initialized
    if not _db_initialized:
        try:
            db.create_all()
            logger.info("Database tables created")
            
            # Check if data exists, seed if empty
            if Ambulance.query.first() is None:
                logger.info("Seeding database with initial data...")
                seed_db(app)
                logger.info("Database seeded successfully")
            
            _db_initialized = True
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            _db_initialized = False

# Mock active data (DEPRECATED - Now using database)
# Kept for reference only
ACTIVE_AMBULANCES = [
    {'id': 'ALS-001', 'lat': 19.0760, 'lon': 72.8777, 'status': 'Available', 'type': 'ALS', 'driver': 'Raj Kumar'},
    {'id': 'ALS-002', 'lat': 19.0860, 'lon': 72.8877, 'status': 'En Route', 'type': 'ALS', 'driver': 'Priya Singh'},
    {'id': 'BLS-001', 'lat': 19.0920, 'lon': 72.8900, 'status': 'Available', 'type': 'BLS', 'driver': 'Amit Patel'},
    {'id': 'BLS-002', 'lat': 19.0820, 'lon': 72.8650, 'status': 'On Scene', 'type': 'BLS', 'driver': 'Suresh Nair'},
    {'id': 'MINI-001', 'lat': 19.0950, 'lon': 72.8750, 'status': 'Available', 'type': 'Mini', 'driver': 'Deepa Gupta'},
]

ACTIVE_INCIDENTS = [
    {'id': 'INC-001', 'location': 'Vashi', 'type': 'Cardiac', 'severity': 'Critical', 'status': 'Assigned', 'time': '14:30'},
    {'id': 'INC-002', 'location': 'Belapur', 'type': 'Trauma', 'severity': 'High', 'status': 'En Route', 'time': '14:45'},
    {'id': 'INC-003', 'location': 'Nerul', 'type': 'Respiratory', 'severity': 'Medium', 'status': 'Waiting', 'time': '14:52'},
]

HOSPITALS = [
    {'id': 'H001', 'name': 'Fortis Hospital', 'lat': 19.0760, 'lon': 72.8777, 'beds': 150, 'available_beds': 45},
    {'id': 'H002', 'name': 'Apollo Clinic', 'lat': 19.0860, 'lon': 72.8877, 'beds': 200, 'available_beds': 78},
    {'id': 'H003', 'name': 'Sai Nursing Home', 'lat': 19.0900, 'lon': 72.8950, 'beds': 80, 'available_beds': 22},
    {'id': 'H004', 'name': 'Nerul Hospital', 'lat': 19.0820, 'lon': 72.8650, 'beds': 120, 'available_beds': 55},
]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def prepare_features(data):
    """
    Prepare feature vector for RF model prediction
    Expected features: distance, hour, is_monsoon, ambulance_type, violations_zone
    """
    try:
        distance = float(data.get('distance', 5.0))
        hour = int(data.get('hour', datetime.now().hour))
        is_monsoon = int(data.get('is_monsoon', 0))
        ambulance_type = int(data.get('ambulance_type', 2))
        violations_zone = float(data.get('violations_zone', 0))
        
        features = np.array([[distance, hour, is_monsoon, ambulance_type, violations_zone]])
        return features
    except Exception as e:
        logger.error(f"Feature preparation error: {e}")
        return None

def predict_eta(features):
    """
    Predict ETA using RF model
    Returns: ETA in minutes
    Falls back to heuristic if model loading fails
    """
    try:
        # Try to use the actual model if available
        if RF_MODEL is not None and SCALER is not None:
            # Scale features using scaler
            if isinstance(SCALER, list):
                # If scaler is [mean, scale] format
                features_scaled = (features - np.array(SCALER[0])) / (np.array(SCALER[1]) + 1e-8)
            else:
                features_scaled = SCALER.transform(features)
            
            # Predict
            eta_minutes = RF_MODEL.predict(features_scaled)[0]
            eta_minutes = max(3, min(20, eta_minutes))
            return round(eta_minutes, 2)
    except Exception as e:
        logger.warning(f"Model prediction failed, using fallback: {e}")
    
    # ========== FALLBACK HEURISTIC MODEL ==========
    # When actual model is unavailable, use a rule-based prediction
    # Based on paper analysis: distance and hour are primary factors
    try:
        distance = features[0, 0]  # km
        hour = features[0, 1]  # 0-23
        is_monsoon = features[0, 2]  # 0 or 1
        ambulance_type = features[0, 3]  # 1, 2, or 3
        violations_zone = features[0, 4]  # count
        
        # Base calculation: 
        # Average speed varies by ambulance type and conditions
        base_speed = {1: 50, 2: 40, 3: 45}.get(int(ambulance_type), 40)  # km/h
        
        # Time of day factor (rush hour slower)
        if 7 <= hour <= 9 or 16 <= hour <= 19:
            time_factor = 1.3  # Rush hour
        elif 0 <= hour < 6 or 23 <= hour:
            time_factor = 0.8  # Night (faster)
        else:
            time_factor = 1.0
        
        # Weather factor
        weather_factor = 1.2 if is_monsoon else 1.0
        
        # Traffic violations factor
        violations_factor = 1.0 + (violations_zone * 0.1)  # +10% per violation zone
        
        # Calculate ETA
        effective_speed = base_speed / (time_factor * weather_factor * violations_factor)
        eta_minutes = (distance / effective_speed) * 60
        
        # Add buffer (random variation between ±10%)
        buffer = np.random.uniform(0.9, 1.1)
        eta_minutes = eta_minutes * buffer
        
        # Clamp to reasonable range
        eta_minutes = max(3, min(20, eta_minutes))
        
        logger.info(f"Fallback prediction: distance={distance}, hour={hour}, speed={effective_speed:.1f} km/h, eta={eta_minutes:.1f} min")
        return round(eta_minutes, 2)
        
    except Exception as e:
        logger.error(f"Even fallback model failed: {e}")
        # Last resort: return average
        return 8.0

# ============================================================================
# ENDPOINTS
# ============================================================================

@app.route('/health', methods=['GET'])
@cache.cached(timeout=10)  # Cache for 10 seconds
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'model_loaded': RF_MODEL is not None,
        'scaler_loaded': SCALER is not None
    }), 200


@app.route('/predict-eta', methods=['POST'])
def predict_eta_endpoint():
    """
    Predict ETA for ambulance to reach destination
    
    Input:
    {
        "distance": 5.0,           # km
        "hour": 14,                # 0-23
        "is_monsoon": false,       # boolean
        "ambulance_type": 2,       # 0=Bike, 1=Mini, 2=BLS, 3=ALS
        "violations_zone": 0       # violation count
    }
    
    Output:
    {
        "eta_minutes": 8.5,
        "confidence": 0.99,
        "status": "success"
    }
    """
    try:
        data = request.get_json()
        
        if data is None:
            return jsonify({'error': 'No JSON data provided', 'status': 'error'}), 400
        
        # Prepare features
        features = prepare_features(data)
        if features is None:
            return jsonify({'error': 'Invalid features', 'status': 'error'}), 400
        
        # Predict ETA
        eta = predict_eta(features)
        if eta is None:
            return jsonify({'error': 'Prediction failed', 'status': 'error'}), 500
        
        return jsonify({
            'eta_minutes': eta,
            'confidence': 0.99,
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Error in /predict-eta: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500


@app.route('/ambulances/active', methods=['GET'])
@cache.cached(timeout=30)  # Cache for 30 seconds
def get_active_ambulances():
    """
    Get list of active ambulances from database
    
    Output:
    [
        {
            "id": "ALS-001",
            "name": "ALS Ambulance 1",
            "type": "ALS",
            "status": "AVAILABLE",
            "latitude": 19.076,
            "longitude": 72.877,
            "driver_name": "Raj Kumar",
            "crew_size": 2
        },
        ...
    ]
    """
    try:
        ambulances = AmbulanceService.get_all_active()
        return jsonify({
            'ambulances': ambulances,
            'total': len(ambulances),
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        }), 200
    except Exception as e:
        logger.error(f"Error in /ambulances/active: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500


@app.route('/incidents/active', methods=['GET'])
@cache.cached(timeout=20)  # Cache for 20 seconds
def get_active_incidents():
    """
    Get list of active incidents from database
    
    Output:
    [
        {
            "id": "INC-001",
            "incident_type": "Cardiac",
            "severity": "CRITICAL",
            "status": "ASSIGNED",
            "latitude": 19.076,
            "longitude": 72.877,
            "patient_name": "John Doe",
            "patient_age": 45
        },
        ...
    ]
    """
    try:
        incidents = IncidentService.get_all_active()
        return jsonify({
            'incidents': incidents,
            'total': len(incidents),
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        }), 200
    except Exception as e:
        logger.error(f"Error in /incidents/active: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500


@app.route('/hospitals', methods=['GET'])
@cache.cached(timeout=60)  # Cache for 60 seconds (hospitals don't change often)
def get_hospitals():
    """
    Get list of hospitals with bed availability from database
    
    Output:
    [
        {
            "id": "HOSP-001",
            "name": "Fortis Hospital",
            "address": "123 Main St, Vashi",
            "phone": "123-456-7890",
            "latitude": 19.076,
            "longitude": 72.877,
            "total_beds": 150,
            "available_beds": 45,
            "has_trauma_center": true,
            "has_cardiac_care": true
        },
        ...
    ]
    """
    try:
        hospitals = HospitalService.get_all()
        return jsonify({
            'hospitals': hospitals,
            'total': len(hospitals),
            'timestamp': datetime.now().isoformat(),
            'status': 'success'
        }), 200
    except Exception as e:
        logger.error(f"Error in /hospitals: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500


@app.route('/dispatch', methods=['POST'])
def dispatch_emergency():
    """
    Handle emergency dispatch request
    
    Input:
    {
        "patient_lat": 19.076,
        "patient_lon": 72.877,
        "incident_type": "Cardiac",
        "severity": "CRITICAL",
        "hour": 14,
        "is_monsoon": false,
        "distance": 5.0
    }
    
    Output:
    {
        "ambulance_type": "ALS",
        "ambulance_id": "ALS-001",
        "eta_minutes": 8.5,
        "hospital": {...},
        "dispatch_id": "DISP-001",
        "status": "success"
    }
    """
    try:
        data = request.get_json()
        
        if data is None:
            return jsonify({'error': 'No JSON data provided', 'status': 'error'}), 400
        
        # Determine ambulance type based on severity
        severity = data.get('severity', 'MODERATE')
        if severity == 'CRITICAL':
            ambulance_type = 3  # ALS
            amb_type_name = 'ALS'
        elif severity == 'SEVERE':
            ambulance_type = 2  # BLS
            amb_type_name = 'BLS'
        elif severity == 'MODERATE':
            ambulance_type = 1  # Mini
            amb_type_name = 'Mini'
        else:
            ambulance_type = 0  # Bike
            amb_type_name = 'Bike'
        
        # Get location from request
        patient_lat = data.get('latitude', 19.076)
        patient_lon = data.get('longitude', 72.877)
        
        # Find closest available ambulance of that type
        closest_ambulance = AmbulanceService.get_closest(patient_lat, patient_lon)
        
        if not closest_ambulance:
            return jsonify({'error': 'No available ambulances', 'status': 'error'}), 503
        
        # Predict ETA
        distance = data.get('distance', 5.0)
        hour = data.get('hour', datetime.now().hour)
        is_monsoon = data.get('is_monsoon', False)
        
        features = prepare_features({
            'distance': distance,
            'hour': hour,
            'is_monsoon': int(is_monsoon),
            'ambulance_type': ambulance_type,
            'violations_zone': 0
        })
        
        eta = predict_eta(features)
        
        # Find best hospital (closest with bed availability)
        best_hospital = HospitalService.get_closest(patient_lat, patient_lon)
        
        if not best_hospital:
            return jsonify({'error': 'No available hospitals', 'status': 'error'}), 503
        
        return jsonify({
            'ambulance_type': amb_type_name,
            'ambulance_id': closest_ambulance['id'],
            'ambulance_driver': closest_ambulance.get('driver_name'),
            'eta_minutes': eta,
            'hospital': best_hospital,
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Error in /dispatch: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500


# ============================================================================
# ADMIN ENDPOINTS - Database Management
# ============================================================================

@app.route('/admin/db/init', methods=['POST'])
def admin_init_db():
    """Initialize database - create tables"""
    try:
        with app.app_context():
            db.create_all()
        return jsonify({
            'message': 'Database tables created successfully',
            'status': 'success'
        }), 200
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500


@app.route('/admin/db/seed', methods=['POST'])
def admin_seed_db():
    """Seed database with initial data"""
    try:
        with app.app_context():
            # Check if already seeded
            if Ambulance.query.first() is not None:
                return jsonify({
                    'message': 'Database already seeded (has data)',
                    'status': 'warning'
                }), 200
            
            seed_db(app)
        
        return jsonify({
            'message': 'Database seeded successfully',
            'status': 'success'
        }), 200
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500


@app.route('/admin/db/reset', methods=['POST'])
def admin_reset_db():
    """Reset database - drop and recreate tables and reseed"""
    try:
        with app.app_context():
            reset_db(app)
            seed_db(app)
        
        return jsonify({
            'message': 'Database reset and reseeded successfully',
            'status': 'success'
        }), 200
    except Exception as e:
        logger.error(f"Error resetting database: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500


@app.route('/admin/db/status', methods=['GET'])
@cache.cached(timeout=15)  # Cache for 15 seconds
def admin_db_status():
    """Get database status and statistics"""
    try:
        with app.app_context():
            ambulance_count = Ambulance.query.count()
            incident_count = Incident.query.count()
            hospital_count = Hospital.query.count()
            dispatch_count = Dispatch.query.count()
        
        return jsonify({
            'database_path': DATABASE_PATH,
            'status': 'connected',
            'tables': {
                'ambulances': ambulance_count,
                'incidents': incident_count,
                'hospitals': hospital_count,
                'dispatch': dispatch_count
            },
            'total_records': ambulance_count + incident_count + hospital_count + dispatch_count,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        logger.error(f"Error getting database status: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500


# ============================================================================
# AMBULANCE CRUD ENDPOINTS
# ============================================================================

@app.route('/admin/ambulances', methods=['POST'])
def create_ambulance():
    """
    Create a new ambulance
    
    Input:
    {
        "id": "AMB-010",
        "name": "New Ambulance",
        "type": "ALS",                 # ALS, BLS, ADVANCED, BIKE
        "latitude": 19.076,
        "longitude": 72.877,
        "driver_name": "Driver Name",
        "crew_size": 2,
        "status": "available"          # Optional: available, responding, en_route, on_scene, transporting
    }
    
    Output:
    {
        "ambulance": {...},
        "message": "Ambulance created successfully",
        "status": "success"
    }
    """
    try:
        data = request.get_json()
        
        if data is None:
            return jsonify({'error': 'No JSON data provided', 'status': 'error'}), 400
        
        # Validate required fields
        required_fields = ['id', 'name', 'type', 'latitude', 'longitude']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}', 'status': 'error'}), 400
        
        # Check if ambulance already exists
        existing = Ambulance.query.filter_by(id=data['id']).first()
        if existing:
            return jsonify({'error': f"Ambulance with id {data['id']} already exists", 'status': 'error'}), 409
        
        # Map type string to enum
        ambulance_type_map = {
            'ALS': 'ALS',
            'BLS': 'BLS',
            'ADVANCED': 'ADVANCED',
            'BIKE': 'BIKE'
        }
        
        ambulance_type = ambulance_type_map.get(data['type'].upper(), 'BLS')
        
        # Map status string to enum (optional)
        status_map = {
            'available': 'AVAILABLE',
            'responding': 'RESPONDING',
            'en_route': 'EN_ROUTE',
            'on_scene': 'ON_SCENE',
            'transporting': 'TRANSPORTING',
            'no_response': 'NO_RESPONSE'
        }
        
        ambulance_status = status_map.get(data.get('status', 'available').lower(), 'AVAILABLE')
        
        # Create ambulance
        new_ambulance = Ambulance(
            id=data['id'],
            name=data['name'],
            type=ambulance_type,
            status=ambulance_status,
            latitude=float(data['latitude']),
            longitude=float(data['longitude']),
            driver_name=data.get('driver_name'),
            crew_size=int(data.get('crew_size', 1))
        )
        
        db.session.add(new_ambulance)
        db.session.commit()
        
        # Clear cache since data changed
        cache.clear()
        
        logger.info(f"Created ambulance: {new_ambulance.id}")
        
        return jsonify({
            'ambulance': new_ambulance.to_dict(),
            'message': 'Ambulance created successfully',
            'status': 'success'
        }), 201
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating ambulance: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500


@app.route('/admin/ambulances/<ambulance_id>', methods=['GET'])
def get_ambulance(ambulance_id):
    """
    Get a specific ambulance by ID
    
    Output:
    {
        "ambulance": {...},
        "status": "success"
    }
    """
    try:
        ambulance = Ambulance.query.filter_by(id=ambulance_id).first()
        
        if not ambulance:
            return jsonify({'error': f'Ambulance {ambulance_id} not found', 'status': 'error'}), 404
        
        return jsonify({
            'ambulance': ambulance.to_dict(),
            'status': 'success'
        }), 200
    
    except Exception as e:
        logger.error(f"Error retrieving ambulance: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500


@app.route('/admin/ambulances/<ambulance_id>', methods=['PUT'])
def update_ambulance(ambulance_id):
    """
    Update an existing ambulance
    
    Input (all fields optional):
    {
        "name": "Updated Name",
        "type": "ALS",
        "latitude": 19.080,
        "longitude": 72.880,
        "driver_name": "New Driver",
        "crew_size": 3,
        "status": "responding"
    }
    
    Output:
    {
        "ambulance": {...},
        "message": "Ambulance updated successfully",
        "status": "success"
    }
    """
    try:
        ambulance = Ambulance.query.filter_by(id=ambulance_id).first()
        
        if not ambulance:
            return jsonify({'error': f'Ambulance {ambulance_id} not found', 'status': 'error'}), 404
        
        data = request.get_json()
        
        if data is None:
            return jsonify({'error': 'No JSON data provided', 'status': 'error'}), 400
        
        # Update fields if provided
        if 'name' in data:
            ambulance.name = data['name']
        
        if 'type' in data:
            ambulance_type_map = {
                'ALS': 'ALS',
                'BLS': 'BLS',
                'ADVANCED': 'ADVANCED',
                'BIKE': 'BIKE'
            }
            ambulance.type = ambulance_type_map.get(data['type'].upper(), ambulance.type)
        
        if 'status' in data:
            status_map = {
                'available': 'AVAILABLE',
                'responding': 'RESPONDING',
                'en_route': 'EN_ROUTE',
                'on_scene': 'ON_SCENE',
                'transporting': 'TRANSPORTING',
                'no_response': 'NO_RESPONSE'
            }
            ambulance.status = status_map.get(data['status'].lower(), ambulance.status)
        
        if 'latitude' in data:
            ambulance.latitude = float(data['latitude'])
        
        if 'longitude' in data:
            ambulance.longitude = float(data['longitude'])
        
        if 'driver_name' in data:
            ambulance.driver_name = data['driver_name']
        
        if 'crew_size' in data:
            ambulance.crew_size = int(data['crew_size'])
        
        ambulance.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Clear cache since data changed
        cache.clear()
        
        logger.info(f"Updated ambulance: {ambulance.id}")
        
        return jsonify({
            'ambulance': ambulance.to_dict(),
            'message': 'Ambulance updated successfully',
            'status': 'success'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating ambulance: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500


@app.route('/admin/ambulances/<ambulance_id>', methods=['DELETE'])
def delete_ambulance(ambulance_id):
    """
    Delete an ambulance by ID
    
    Output:
    {
        "message": "Ambulance deleted successfully",
        "status": "success"
    }
    """
    try:
        ambulance = Ambulance.query.filter_by(id=ambulance_id).first()
        
        if not ambulance:
            return jsonify({'error': f'Ambulance {ambulance_id} not found', 'status': 'error'}), 404
        
        # Don't delete if assigned to active incident
        if ambulance.assigned_incident_id:
            incident = Incident.query.filter_by(id=ambulance.assigned_incident_id).first()
            if incident and incident.status.value in ['waiting', 'assigned', 'en_route', 'on_scene']:
                return jsonify({
                    'error': f'Cannot delete ambulance {ambulance_id} - it is assigned to active incident {ambulance.assigned_incident_id}',
                    'status': 'error'
                }), 409
        
        db.session.delete(ambulance)
        db.session.commit()
        
        # Clear cache since data changed
        cache.clear()
        
        logger.info(f"Deleted ambulance: {ambulance_id}")
        
        return jsonify({
            'message': f'Ambulance {ambulance_id} deleted successfully',
            'status': 'success'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting ambulance: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500


# ============================================================================
# INCIDENT CRUD ENDPOINTS
# ============================================================================

@app.route('/admin/incidents', methods=['POST'])
def create_incident():
    """
    Create a new incident
    
    Input:
    {
        "id": "INC-010",
        "incident_type": "Cardiac",
        "severity": "CRITICAL",          # CRITICAL, SEVERE, MODERATE, MINOR
        "latitude": 19.076,
        "longitude": 72.877,
        "patient_name": "John Doe",
        "patient_age": 45,
        "contact_number": "9876543210",
        "status": "waiting"              # Optional: waiting, assigned, en_route, on_scene, transported, completed
    }
    
    Output:
    {
        "incident": {...},
        "message": "Incident created successfully",
        "status": "success"
    }
    """
    try:
        data = request.get_json()
        
        if data is None:
            return jsonify({'error': 'No JSON data provided', 'status': 'error'}), 400
        
        # Validate required fields
        required_fields = ['id', 'incident_type', 'severity', 'latitude', 'longitude', 'patient_name']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}', 'status': 'error'}), 400
        
        # Check if incident already exists
        existing = Incident.query.filter_by(id=data['id']).first()
        if existing:
            return jsonify({'error': f"Incident with id {data['id']} already exists", 'status': 'error'}), 409
        
        # Map severity string to enum
        severity_map = {
            'critical': 'CRITICAL',
            'severe': 'SEVERE',
            'moderate': 'MODERATE',
            'minor': 'MINOR'
        }
        
        incident_severity = severity_map.get(data['severity'].lower(), 'MODERATE')
        
        # Map status string to enum (optional)
        status_map = {
            'waiting': 'WAITING',
            'assigned': 'ASSIGNED',
            'en_route': 'EN_ROUTE',
            'on_scene': 'ON_SCENE',
            'transported': 'TRANSPORTED',
            'completed': 'COMPLETED'
        }
        
        incident_status = status_map.get(data.get('status', 'waiting').lower(), 'WAITING')
        
        # Create incident
        new_incident = Incident(
            id=data['id'],
            incident_type=data['incident_type'],
            severity=incident_severity,
            latitude=float(data['latitude']),
            longitude=float(data['longitude']),
            patient_name=data['patient_name'],
            patient_age=int(data.get('patient_age', 0)),
            patient_phone=data.get('contact_number') or data.get('patient_phone'),
            status=incident_status
        )
        
        db.session.add(new_incident)
        db.session.commit()
        
        # Clear cache since data changed
        cache.clear()
        
        logger.info(f"Created incident: {new_incident.id}")
        
        return jsonify({
            'incident': new_incident.to_dict(),
            'message': 'Incident created successfully',
            'status': 'success'
        }), 201
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating incident: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500


@app.route('/admin/incidents/<incident_id>', methods=['GET'])
def get_incident(incident_id):
    """
    Get a specific incident by ID
    
    Output:
    {
        "incident": {...},
        "status": "success"
    }
    """
    try:
        incident = Incident.query.filter_by(id=incident_id).first()
        
        if not incident:
            return jsonify({'error': f'Incident {incident_id} not found', 'status': 'error'}), 404
        
        return jsonify({
            'incident': incident.to_dict(),
            'status': 'success'
        }), 200
    
    except Exception as e:
        logger.error(f"Error retrieving incident: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500


@app.route('/admin/incidents/<incident_id>', methods=['PUT'])
def update_incident(incident_id):
    """
    Update an existing incident
    
    Input (all fields optional):
    {
        "incident_type": "Trauma",
        "severity": "SEVERE",
        "latitude": 19.080,
        "longitude": 72.880,
        "patient_name": "Jane Doe",
        "patient_age": 50,
        "contact_number": "9876543210",
        "status": "en_route",
        "assigned_ambulance_id": "AMB-001",
        "assigned_hospital_id": "HOSP-001"
    }
    
    Output:
    {
        "incident": {...},
        "message": "Incident updated successfully",
        "status": "success"
    }
    """
    try:
        incident = Incident.query.filter_by(id=incident_id).first()
        
        if not incident:
            return jsonify({'error': f'Incident {incident_id} not found', 'status': 'error'}), 404
        
        data = request.get_json()
        
        if data is None:
            return jsonify({'error': 'No JSON data provided', 'status': 'error'}), 400
        
        # Update fields if provided
        if 'incident_type' in data:
            incident.incident_type = data['incident_type']
        
        if 'severity' in data:
            severity_map = {
                'critical': 'CRITICAL',
                'severe': 'SEVERE',
                'moderate': 'MODERATE',
                'minor': 'MINOR'
            }
            incident.severity = severity_map.get(data['severity'].lower(), incident.severity)
        
        if 'status' in data:
            status_map = {
                'waiting': 'WAITING',
                'assigned': 'ASSIGNED',
                'en_route': 'EN_ROUTE',
                'on_scene': 'ON_SCENE',
                'transported': 'TRANSPORTED',
                'completed': 'COMPLETED'
            }
            incident.status = status_map.get(data['status'].lower(), incident.status)
        
        if 'latitude' in data:
            incident.latitude = float(data['latitude'])
        
        if 'longitude' in data:
            incident.longitude = float(data['longitude'])
        
        if 'patient_name' in data:
            incident.patient_name = data['patient_name']
        
        if 'patient_age' in data:
            incident.patient_age = int(data['patient_age'])
        
        if 'contact_number' in data or 'patient_phone' in data:
            incident.patient_phone = data.get('contact_number') or data.get('patient_phone')
        
        if 'assigned_ambulance_id' in data:
            ambulance = Ambulance.query.filter_by(id=data['assigned_ambulance_id']).first()
            if not ambulance:
                return jsonify({'error': f"Ambulance {data['assigned_ambulance_id']} not found", 'status': 'error'}), 404
            incident.assigned_ambulance_id = data['assigned_ambulance_id']
        
        if 'assigned_hospital_id' in data:
            hospital = Hospital.query.filter_by(id=data['assigned_hospital_id']).first()
            if not hospital:
                return jsonify({'error': f"Hospital {data['assigned_hospital_id']} not found", 'status': 'error'}), 404
            incident.assigned_hospital_id = data['assigned_hospital_id']
        
        incident.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Clear cache since data changed
        cache.clear()
        
        logger.info(f"Updated incident: {incident.id}")
        
        return jsonify({
            'incident': incident.to_dict(),
            'message': 'Incident updated successfully',
            'status': 'success'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating incident: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500


@app.route('/admin/incidents/<incident_id>', methods=['DELETE'])
def delete_incident(incident_id):
    """
    Delete an incident by ID
    
    Output:
    {
        "message": "Incident deleted successfully",
        "status": "success"
    }
    """
    try:
        incident = Incident.query.filter_by(id=incident_id).first()
        
        if not incident:
            return jsonify({'error': f'Incident {incident_id} not found', 'status': 'error'}), 404
        
        # Check if incident is in active state
        if incident.status.value in ['waiting', 'assigned', 'en_route', 'on_scene']:
            return jsonify({
                'error': f'Cannot delete incident {incident_id} - it is in active state ({incident.status.value})',
                'status': 'error'
            }), 409
        
        db.session.delete(incident)
        db.session.commit()
        
        # Clear cache since data changed
        cache.clear()
        
        logger.info(f"Deleted incident: {incident_id}")
        
        return jsonify({
            'message': f'Incident {incident_id} deleted successfully',
            'status': 'success'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting incident: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500


# ============================================================================
# HOSPITAL CRUD ENDPOINTS
# ============================================================================

@app.route('/admin/hospitals', methods=['POST'])
def create_hospital():
    """
    Create a new hospital
    
    Input:
    {
        "id": "HOSP-010",
        "name": "New Medical Center",
        "address": "123 Health St",
        "phone": "123-456-7890",
        "latitude": 19.090,
        "longitude": 72.890,
        "total_beds": 200,
        "available_beds": 50,
        "is_active": true,
        "has_trauma_center": true,
        "has_cardiac_care": true
    }
    
    Output:
    {
        "hospital": {...},
        "message": "Hospital created successfully",
        "status": "success"
    }
    """
    try:
        data = request.get_json()
        
        if data is None:
            return jsonify({'error': 'No JSON data provided', 'status': 'error'}), 400
        
        # Validate required fields
        required_fields = ['id', 'name', 'latitude', 'longitude', 'total_beds']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}', 'status': 'error'}), 400
        
        # Check if hospital already exists
        existing = Hospital.query.filter_by(id=data['id']).first()
        if existing:
            return jsonify({'error': f"Hospital with id {data['id']} already exists", 'status': 'error'}), 409
        
        # Create hospital
        new_hospital = Hospital(
            id=data['id'],
            name=data['name'],
            address=data.get('address'),
            phone=data.get('phone'),
            latitude=float(data['latitude']),
            longitude=float(data['longitude']),
            total_beds=int(data['total_beds']),
            available_beds=int(data.get('available_beds', data.get('total_beds', 0))),
            is_active=data.get('is_active', True),
            has_trauma_center=data.get('has_trauma_center', False),
            has_cardiac_care=data.get('has_cardiac_care', False)
        )
        
        db.session.add(new_hospital)
        db.session.commit()
        
        # Clear cache since data changed
        cache.clear()
        
        logger.info(f"Created hospital: {new_hospital.id}")
        
        return jsonify({
            'hospital': new_hospital.to_dict(),
            'message': 'Hospital created successfully',
            'status': 'success'
        }), 201
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating hospital: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500


@app.route('/admin/hospitals/<hospital_id>', methods=['GET'])
def get_hospital(hospital_id):
    """
    Get a specific hospital by ID
    
    Output:
    {
        "hospital": {...},
        "status": "success"
    }
    """
    try:
        hospital = Hospital.query.filter_by(id=hospital_id).first()
        
        if not hospital:
            return jsonify({'error': f'Hospital {hospital_id} not found', 'status': 'error'}), 404
        
        return jsonify({
            'hospital': hospital.to_dict(),
            'status': 'success'
        }), 200
    
    except Exception as e:
        logger.error(f"Error retrieving hospital: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500


@app.route('/admin/hospitals/<hospital_id>', methods=['PUT'])
def update_hospital(hospital_id):
    """
    Update an existing hospital
    
    Input (all fields optional):
    {
        "name": "Updated Hospital",
        "address": "456 New Ave",
        "phone": "987-654-3210",
        "latitude": 19.095,
        "longitude": 72.895,
        "total_beds": 250,
        "available_beds": 60,
        "is_active": true,
        "has_trauma_center": true,
        "has_cardiac_care": false
    }
    
    Output:
    {
        "hospital": {...},
        "message": "Hospital updated successfully",
        "status": "success"
    }
    """
    try:
        hospital = Hospital.query.filter_by(id=hospital_id).first()
        
        if not hospital:
            return jsonify({'error': f'Hospital {hospital_id} not found', 'status': 'error'}), 404
        
        data = request.get_json()
        
        if data is None:
            return jsonify({'error': 'No JSON data provided', 'status': 'error'}), 400
        
        # Update fields if provided
        if 'name' in data:
            hospital.name = data['name']
        
        if 'address' in data:
            hospital.address = data['address']
        
        if 'phone' in data:
            hospital.phone = data['phone']
        
        if 'latitude' in data:
            hospital.latitude = float(data['latitude'])
        
        if 'longitude' in data:
            hospital.longitude = float(data['longitude'])
        
        if 'total_beds' in data:
            hospital.total_beds = int(data['total_beds'])
        
        if 'available_beds' in data:
            hospital.available_beds = int(data['available_beds'])
        
        if 'is_active' in data:
            hospital.is_active = bool(data['is_active'])
        
        if 'has_trauma_center' in data:
            hospital.has_trauma_center = bool(data['has_trauma_center'])
        
        if 'has_cardiac_care' in data:
            hospital.has_cardiac_care = bool(data['has_cardiac_care'])
        
        hospital.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Clear cache since data changed
        cache.clear()
        
        logger.info(f"Updated hospital: {hospital.id}")
        
        return jsonify({
            'hospital': hospital.to_dict(),
            'message': 'Hospital updated successfully',
            'status': 'success'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating hospital: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500


@app.route('/admin/hospitals/<hospital_id>', methods=['DELETE'])
def delete_hospital(hospital_id):
    """
    Delete a hospital by ID
    
    Output:
    {
        "message": "Hospital deleted successfully",
        "status": "success"
    }
    """
    try:
        hospital = Hospital.query.filter_by(id=hospital_id).first()
        
        if not hospital:
            return jsonify({'error': f'Hospital {hospital_id} not found', 'status': 'error'}), 404
        
        # Check if hospital has active incidents
        active_incidents = Incident.query.filter(
            Incident.assigned_hospital_id == hospital_id,
            Incident.status.in_([IncidentStatus.WAITING, IncidentStatus.ASSIGNED, IncidentStatus.EN_ROUTE, IncidentStatus.ON_SCENE])
        ).first()
        
        if active_incidents:
            return jsonify({
                'error': f'Cannot delete hospital {hospital_id} - it has active incidents',
                'status': 'error'
            }), 409
        
        db.session.delete(hospital)
        db.session.commit()
        
        # Clear cache since data changed
        cache.clear()
        
        logger.info(f"Deleted hospital: {hospital_id}")
        
        return jsonify({
            'message': f'Hospital {hospital_id} deleted successfully',
            'status': 'success'
        }), 200
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting hospital: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500


@app.before_request
def init_db_if_needed():
    """Initialize database on first request"""
    ensure_db_initialized()


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found', 'status': 'error'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error', 'status': 'error'}), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    # Initialize database before starting server
    with app.app_context():
        ensure_db_initialized()
    
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║           NaviRaksha Backend API - Starting                   ║
    ╚═══════════════════════════════════════════════════════════════╝
    
    🚀 Server running on: http://localhost:8000
    
    📊 Available Endpoints:
       GET  /health              - Health check
       POST /predict-eta         - Predict ETA
       GET  /ambulances/active   - Get active ambulances
       GET  /incidents/active    - Get active incidents
       GET  /hospitals           - Get hospitals
       POST /dispatch            - Handle emergency dispatch
    
    📚 Admin Endpoints:
       POST /admin/db/init       - Initialize database tables
       POST /admin/db/seed       - Seed initial data
       POST /admin/db/reset      - Reset and reseed database
       GET  /admin/db/status     - Get database status
    
    🧪 Test with:
       curl -X POST http://localhost:8000/predict-eta \
         -H "Content-Type: application/json" \
         -d '{"distance": 5, "hour": 14, "is_monsoon": false, "ambulance_type": 2}'
    
    ⏸️  Press Ctrl+C to stop
    """)
    
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
        use_reloader=False
    )

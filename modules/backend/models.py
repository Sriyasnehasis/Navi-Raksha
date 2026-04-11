"""
NaviRaksha Database Models
SQLAlchemy models for Ambulances, Incidents, and Hospitals
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum

db = SQLAlchemy()

class AmbulanceType(enum.Enum):
    """Ambulance types"""
    ALS = 1
    BLS = 2
    ADVANCED = 3
    BIKE = 4

class AmbulanceStatus(enum.Enum):
    """Ambulance statuses"""
    AVAILABLE = "available"
    RESPONDING = "responding"
    EN_ROUTE = "en_route"
    ON_SCENE = "on_scene"
    TRANSPORTING = "transporting"
    NO_RESPONSE = "no_response"

class IncidentSeverity(enum.Enum):
    """Incident severity levels"""
    CRITICAL = "critical"
    SEVERE = "severe"
    MODERATE = "moderate"
    MINOR = "minor"

class IncidentStatus(enum.Enum):
    """Incident statuses"""
    WAITING = "waiting"
    ASSIGNED = "assigned"
    EN_ROUTE = "en_route"
    ON_SCENE = "on_scene"
    TRANSPORTED = "transported"
    COMPLETED = "completed"

# ============================================================================
# MODELS
# ============================================================================

class Ambulance(db.Model):
    """Ambulance model"""
    __tablename__ = 'ambulances'
    __table_args__ = (
        db.Index('idx_ambulance_status', 'status'),
        db.Index('idx_ambulance_type', 'type'),
        db.Index('idx_ambulance_incident', 'assigned_incident_id'),
    )
    
    id = db.Column(db.String(50), primary_key=True)  # AMB-001, AMB-002, etc.
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.Enum(AmbulanceType), nullable=False, default=AmbulanceType.BLS)
    status = db.Column(db.Enum(AmbulanceStatus), nullable=False, default=AmbulanceStatus.AVAILABLE)
    
    # Location
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    
    # Crew info
    driver_name = db.Column(db.String(100), nullable=True)
    crew_size = db.Column(db.Integer, default=1)
    
    # Status
    assigned_incident_id = db.Column(db.String(50), db.ForeignKey('incidents.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type.name,
            'status': self.status.value,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'driver_name': self.driver_name,
            'crew_size': self.crew_size,
            'assigned_incident_id': self.assigned_incident_id,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Ambulance {self.id}>'


class Incident(db.Model):
    """Incident/Emergency model"""
    __tablename__ = 'incidents'
    __table_args__ = (
        db.Index('idx_incident_status', 'status'),
        db.Index('idx_incident_severity', 'severity'),
        db.Index('idx_incident_ambulance', 'assigned_ambulance_id'),
        db.Index('idx_incident_hospital', 'assigned_hospital_id'),
    )
    
    id = db.Column(db.String(50), primary_key=True)  # INC-001, INC-002, etc.
    incident_type = db.Column(db.String(100), nullable=False)  # Cardiac, Trauma, etc.
    severity = db.Column(db.Enum(IncidentSeverity), nullable=False)
    status = db.Column(db.Enum(IncidentStatus), nullable=False, default=IncidentStatus.WAITING)
    
    # Location
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    location_description = db.Column(db.String(200), nullable=True)
    
    # Patient info
    patient_name = db.Column(db.String(100), nullable=True)
    patient_age = db.Column(db.Integer, nullable=True)
    patient_phone = db.Column(db.String(20), nullable=True)
    
    # Dispatch info
    assigned_ambulance_id = db.Column(db.String(50), db.ForeignKey('ambulances.id'), nullable=True)
    assigned_hospital_id = db.Column(db.String(50), db.ForeignKey('hospitals.id'), nullable=True)
    
    # Timing
    reported_at = db.Column(db.DateTime, default=datetime.utcnow)
    assigned_at = db.Column(db.DateTime, nullable=True)
    arrived_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'incident_type': self.incident_type,
            'severity': self.severity.value,
            'status': self.status.value,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'location_description': self.location_description,
            'patient_name': self.patient_name,
            'patient_age': self.patient_age,
            'patient_phone': self.patient_phone,
            'assigned_ambulance_id': self.assigned_ambulance_id,
            'assigned_hospital_id': self.assigned_hospital_id,
            'reported_at': self.reported_at.isoformat() if self.reported_at else None
        }
    
    def __repr__(self):
        return f'<Incident {self.id}>'


class Hospital(db.Model):
    """Hospital model"""
    __tablename__ = 'hospitals'
    __table_args__ = (
        db.Index('idx_hospital_active', 'is_active'),
        db.Index('idx_hospital_trauma', 'has_trauma_center'),
        db.Index('idx_hospital_cardiac', 'has_cardiac_care'),
        db.Index('idx_hospital_beds', 'available_beds'),
    )
    
    id = db.Column(db.String(50), primary_key=True)  # HOSP-001, etc.
    name = db.Column(db.String(150), nullable=False)
    address = db.Column(db.String(250), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    
    # Location
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    
    # Bed capacity
    total_beds = db.Column(db.Integer, nullable=False, default=100)
    available_beds = db.Column(db.Integer, nullable=False, default=50)
    emergency_beds = db.Column(db.Integer, nullable=False, default=10)
    icu_beds = db.Column(db.Integer, nullable=False, default=5)
    
    # Features
    has_trauma_center = db.Column(db.Boolean, default=False)
    has_cardiac_care = db.Column(db.Boolean, default=False)
    has_pediatric_care = db.Column(db.Boolean, default=False)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'phone': self.phone,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'total_beds': self.total_beds,
            'available_beds': self.available_beds,
            'emergency_beds': self.emergency_beds,
            'icu_beds': self.icu_beds,
            'has_trauma_center': self.has_trauma_center,
            'has_cardiac_care': self.has_cardiac_care,
            'has_pediatric_care': self.has_pediatric_care,
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f'<Hospital {self.name}>'


class Dispatch(db.Model):
    """Dispatch record model"""
    __tablename__ = 'dispatches'
    __table_args__ = (
        db.Index('idx_dispatch_incident', 'incident_id'),
        db.Index('idx_dispatch_ambulance', 'ambulance_id'),
        db.Index('idx_dispatch_hospital', 'hospital_id'),
        db.Index('idx_dispatch_status', 'status'),
    )
    
    id = db.Column(db.String(50), primary_key=True)  # DISP-001, etc.
    incident_id = db.Column(db.String(50), db.ForeignKey('incidents.id'), nullable=False)
    ambulance_id = db.Column(db.String(50), db.ForeignKey('ambulances.id'), nullable=False)
    hospital_id = db.Column(db.String(50), db.ForeignKey('hospitals.id'), nullable=True)
    
    # ETA prediction
    predicted_eta = db.Column(db.Float, nullable=False)  # minutes
    actual_eta = db.Column(db.Float, nullable=True)  # minutes
    
    # Status
    status = db.Column(db.String(50), default="dispatched")
    
    # Timing
    dispatched_at = db.Column(db.DateTime, default=datetime.utcnow)
    arrived_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'incident_id': self.incident_id,
            'ambulance_id': self.ambulance_id,
            'hospital_id': self.hospital_id,
            'predicted_eta': self.predicted_eta,
            'actual_eta': self.actual_eta,
            'status': self.status,
            'dispatched_at': self.dispatched_at.isoformat()
        }
    
    def __repr__(self):
        return f'<Dispatch {self.id}>'

"""
NaviRaksha Database Service Layer
Provides convenient methods for database queries
"""

from models import db, Ambulance, Incident, Hospital, Dispatch
from models import AmbulanceType, AmbulanceStatus, IncidentSeverity, IncidentStatus
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class AmbulanceService:
    """Service for ambulance operations"""
    
    @staticmethod
    def get_all_active():
        """Get all active ambulances"""
        try:
            ambulances = Ambulance.query.filter(
                Ambulance.status.in_([
                    AmbulanceStatus.AVAILABLE,
                    AmbulanceStatus.RESPONDING,
                    AmbulanceStatus.EN_ROUTE,
                    AmbulanceStatus.ON_SCENE
                ])
            ).all()
            return [a.to_dict() for a in ambulances]
        except Exception as e:
            logger.error(f"Error getting active ambulances: {e}")
            return []
    
    @staticmethod
    def get_by_id(ambulance_id):
        """Get ambulance by ID"""
        try:
            amb = Ambulance.query.get(ambulance_id)
            if amb:
                return amb.to_dict()
            return None
        except Exception as e:
            logger.error(f"Error getting ambulance {ambulance_id}: {e}")
            return None
    
    @staticmethod
    def get_available_by_type(ambulance_type):
        """Get available ambulances of specific type"""
        try:
            ambulances = Ambulance.query.filter(
                Ambulance.type == ambulance_type,
                Ambulance.status == AmbulanceStatus.AVAILABLE
            ).all()
            return [a.to_dict() for a in ambulances]
        except Exception as e:
            logger.error(f"Error getting available ambulances of type {ambulance_type}: {e}")
            return []
    
    @staticmethod
    def get_closest(latitude, longitude, ambulance_type=None):
        """Get closest available ambulance"""
        try:
            query = Ambulance.query.filter(Ambulance.status == AmbulanceStatus.AVAILABLE)
            
            if ambulance_type:
                query = query.filter(Ambulance.type == ambulance_type)
            
            ambulances = query.all()
            
            if not ambulances:
                return None
            
            # Calculate distances
            def distance(lat, lon):
                return ((lat - latitude) ** 2 + (lon - longitude) ** 2) ** 0.5
            
            # Find closest
            closest = min(ambulances, key=lambda a: distance(a.latitude, a.longitude))
            return closest.to_dict()
        
        except Exception as e:
            logger.error(f"Error getting closest ambulance: {e}")
            return None
    
    @staticmethod
    def update_status(ambulance_id, new_status):
        """Update ambulance status"""
        try:
            amb = Ambulance.query.get(ambulance_id)
            if amb:
                amb.status = new_status
                amb.updated_at = datetime.utcnow()
                db.session.commit()
                logger.info(f"Updated ambulance {ambulance_id} status to {new_status}")
                return amb.to_dict()
            return None
        except Exception as e:
            logger.error(f"Error updating ambulance status: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def update_location(ambulance_id, latitude, longitude):
        """Update ambulance location"""
        try:
            amb = Ambulance.query.get(ambulance_id)
            if amb:
                amb.latitude = latitude
                amb.longitude = longitude
                amb.updated_at = datetime.utcnow()
                db.session.commit()
                return amb.to_dict()
            return None
        except Exception as e:
            logger.error(f"Error updating ambulance location: {e}")
            db.session.rollback()
            return None


class IncidentService:
    """Service for incident operations"""
    
    @staticmethod
    def get_all_active():
        """Get all active incidents"""
        try:
            incidents = Incident.query.filter(
                Incident.status.in_([
                    IncidentStatus.WAITING,
                    IncidentStatus.ASSIGNED,
                    IncidentStatus.EN_ROUTE,
                    IncidentStatus.ON_SCENE
                ])
            ).all()
            return [i.to_dict() for i in incidents]
        except Exception as e:
            logger.error(f"Error getting active incidents: {e}")
            return []
    
    @staticmethod
    def get_by_id(incident_id):
        """Get incident by ID"""
        try:
            inc = Incident.query.get(incident_id)
            if inc:
                return inc.to_dict()
            return None
        except Exception as e:
            logger.error(f"Error getting incident {incident_id}: {e}")
            return None
    
    @staticmethod
    def get_by_severity(severity):
        """Get incidents by severity"""
        try:
            incidents = Incident.query.filter(
                Incident.severity == severity,
                Incident.status.in_([
                    IncidentStatus.WAITING,
                    IncidentStatus.ASSIGNED,
                    IncidentStatus.EN_ROUTE
                ])
            ).all()
            return [i.to_dict() for i in incidents]
        except Exception as e:
            logger.error(f"Error getting incidents by severity: {e}")
            return []
    
    @staticmethod
    def create(incident_type, severity, latitude, longitude, patient_name=None, patient_age=None):
        """Create new incident"""
        try:
            # Generate ID
            last_incident = Incident.query.order_by(Incident.id.desc()).first()
            incident_num = int(last_incident.id.split('-')[1]) + 1 if last_incident else 1
            incident_id = f"INC-{incident_num:03d}"
            
            incident = Incident(
                id=incident_id,
                incident_type=incident_type,
                severity=severity,
                latitude=latitude,
                longitude=longitude,
                patient_name=patient_name,
                patient_age=patient_age
            )
            
            db.session.add(incident)
            db.session.commit()
            logger.info(f"Created incident {incident_id}")
            return incident.to_dict()
        except Exception as e:
            logger.error(f"Error creating incident: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def assign_ambulance(incident_id, ambulance_id):
        """Assign ambulance to incident"""
        try:
            inc = Incident.query.get(incident_id)
            amb = Ambulance.query.get(ambulance_id)
            
            if inc and amb:
                inc.assigned_ambulance_id = ambulance_id
                inc.status = IncidentStatus.ASSIGNED
                inc.assigned_at = datetime.utcnow()
                
                amb.assigned_incident_id = incident_id
                amb.status = AmbulanceStatus.RESPONDING
                
                db.session.commit()
                logger.info(f"Assigned ambulance {ambulance_id} to incident {incident_id}")
                return inc.to_dict()
            return None
        except Exception as e:
            logger.error(f"Error assigning ambulance: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def update_status(incident_id, new_status):
        """Update incident status"""
        try:
            inc = Incident.query.get(incident_id)
            if inc:
                inc.status = new_status
                inc.updated_at = datetime.utcnow()
                db.session.commit()
                return inc.to_dict()
            return None
        except Exception as e:
            logger.error(f"Error updating incident status: {e}")
            db.session.rollback()
            return None


class HospitalService:
    """Service for hospital operations"""
    
    @staticmethod
    def get_all():
        """Get all active hospitals"""
        try:
            hospitals = Hospital.query.filter(Hospital.is_active == True).all()
            return [h.to_dict() for h in hospitals]
        except Exception as e:
            logger.error(f"Error getting hospitals: {e}")
            return []
    
    @staticmethod
    def get_by_id(hospital_id):
        """Get hospital by ID"""
        try:
            hosp = Hospital.query.get(hospital_id)
            if hosp:
                return hosp.to_dict()
            return None
        except Exception as e:
            logger.error(f"Error getting hospital {hospital_id}: {e}")
            return None
    
    @staticmethod
    def get_with_beds():
        """Get hospitals with available beds"""
        try:
            hospitals = Hospital.query.filter(
                Hospital.is_active == True,
                Hospital.available_beds > 0
            ).all()
            return [h.to_dict() for h in hospitals]
        except Exception as e:
            logger.error(f"Error getting hospitals with beds: {e}")
            return []
    
    @staticmethod
    def get_by_specialty(specialty):
        """Get hospitals by specialty"""
        try:
            if specialty == "trauma":
                hospitals = Hospital.query.filter(Hospital.has_trauma_center == True).all()
            elif specialty == "cardiac":
                hospitals = Hospital.query.filter(Hospital.has_cardiac_care == True).all()
            elif specialty == "pediatric":
                hospitals = Hospital.query.filter(Hospital.has_pediatric_care == True).all()
            else:
                hospitals = []
            
            return [h.to_dict() for h in hospitals]
        except Exception as e:
            logger.error(f"Error getting hospitals by specialty: {e}")
            return []
    
    @staticmethod
    def get_closest(latitude, longitude):
        """Get closest hospital to location"""
        try:
            hospitals = Hospital.query.filter(Hospital.is_active == True).all()
            
            if not hospitals:
                return None
            
            # Calculate distances
            def distance(lat, lon):
                return ((lat - latitude) ** 2 + (lon - longitude) ** 2) ** 0.5
            
            # Find closest
            closest = min(hospitals, key=lambda h: distance(h.latitude, h.longitude))
            return closest.to_dict()
        except Exception as e:
            logger.error(f"Error getting closest hospital: {e}")
            return None
    
    @staticmethod
    def update_beds(hospital_id, available_beds):
        """Update available beds"""
        try:
            hosp = Hospital.query.get(hospital_id)
            if hosp:
                hosp.available_beds = available_beds
                hosp.updated_at = datetime.utcnow()
                db.session.commit()
                return hosp.to_dict()
            return None
        except Exception as e:
            logger.error(f"Error updating hospital beds: {e}")
            db.session.rollback()
            return None


class DispatchService:
    """Service for dispatch operations"""
    
    @staticmethod
    def create(incident_id, ambulance_id, hospital_id, predicted_eta):
        """Create dispatch record"""
        try:
            # Generate ID
            last_dispatch = Dispatch.query.order_by(Dispatch.id.desc()).first()
            dispatch_num = int(last_dispatch.id.split('-')[1]) + 1 if last_dispatch else 1
            dispatch_id = f"DISP-{dispatch_num:03d}"
            
            dispatch = Dispatch(
                id=dispatch_id,
                incident_id=incident_id,
                ambulance_id=ambulance_id,
                hospital_id=hospital_id,
                predicted_eta=predicted_eta,
                status="dispatched"
            )
            
            db.session.add(dispatch)
            db.session.commit()
            logger.info(f"Created dispatch {dispatch_id}")
            return dispatch.to_dict()
        except Exception as e:
            logger.error(f"Error creating dispatch: {e}")
            db.session.rollback()
            return None
    
    @staticmethod
    def get_by_incident(incident_id):
        """Get dispatch by incident"""
        try:
            dispatch = Dispatch.query.filter_by(incident_id=incident_id).first()
            if dispatch:
                return dispatch.to_dict()
            return None
        except Exception as e:
            logger.error(f"Error getting dispatch for incident: {e}")
            return None

"""
NaviRaksha Database Initialization
Creates database tables and seeds with initial data
"""

import os
import sys
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from models import db, Ambulance, Incident, Hospital, Dispatch
from models import AmbulanceType, AmbulanceStatus, IncidentSeverity, IncidentStatus

def init_db(app):
    """Initialize database"""
    with app.app_context():
        # Create all tables
        print("Creating database tables...")
        db.create_all()
        print("[OK] Tables created")

def seed_db(app):
    """Seed database with initial data"""
    with app.app_context():
        # Check if data already exists
        if Ambulance.query.first():
            print("[OK] Database already seeded")
            return
        
        print("\nSeeding database with initial data...")
        
        # Create ambulances
        ambulances = [
            Ambulance(
                id="ALS-001",
                name="Advanced Life Support Unit 1",
                type=AmbulanceType.ALS,
                status=AmbulanceStatus.AVAILABLE,
                latitude=19.076,
                longitude=72.8777,
                driver_name="Raj Kumar",
                crew_size=2
            ),
            Ambulance(
                id="ALS-002",
                name="Advanced Life Support Unit 2",
                type=AmbulanceType.ALS,
                status=AmbulanceStatus.RESPONDING,
                latitude=19.086,
                longitude=72.8877,
                driver_name="Priya Singh",
                crew_size=2
            ),
            Ambulance(
                id="BLS-001",
                name="Basic Life Support Unit 1",
                type=AmbulanceType.BLS,
                status=AmbulanceStatus.AVAILABLE,
                latitude=19.092,
                longitude=72.89,
                driver_name="Amit Patel",
                crew_size=1
            ),
            Ambulance(
                id="BLS-002",
                name="Basic Life Support Unit 2",
                type=AmbulanceType.BLS,
                status=AmbulanceStatus.ON_SCENE,
                latitude=19.082,
                longitude=72.865,
                driver_name="Suresh Nair",
                crew_size=1
            ),
            Ambulance(
                id="MINI-001",
                name="Mini Ambulance",
                type=AmbulanceType.BIKE,
                status=AmbulanceStatus.AVAILABLE,
                latitude=19.095,
                longitude=72.875,
                driver_name="Deepa Gupta",
                crew_size=1
            ),
        ]
        
        for amb in ambulances:
            db.session.add(amb)
        print(f"  [OK] Added {len(ambulances)} ambulances")
        
        # Create incidents
        incidents = [
            Incident(
                id="INC-001",
                incident_type="Cardiac",
                severity=IncidentSeverity.CRITICAL,
                status=IncidentStatus.ASSIGNED,
                latitude=19.0750,
                longitude=72.8700,
                location_description="Vashi - Sector 5",
                patient_name="Ramesh Sharma",
                patient_age=55,
                patient_phone="9876543210",
                assigned_ambulance_id="ALS-001",
                assigned_hospital_id="HOSP-001"
            ),
            Incident(
                id="INC-002",
                incident_type="Trauma",
                severity=IncidentSeverity.SEVERE,
                status=IncidentStatus.EN_ROUTE,
                latitude=19.0850,
                longitude=72.8900,
                location_description="Belapur - Main Road",
                patient_name="Priya Verma",
                patient_age=28,
                patient_phone="9123456789",
                assigned_ambulance_id="BLS-002",
                assigned_hospital_id="HOSP-002"
            ),
            Incident(
                id="INC-003",
                incident_type="Respiratory",
                severity=IncidentSeverity.MODERATE,
                status=IncidentStatus.WAITING,
                latitude=19.0920,
                longitude=72.8950,
                location_description="Nerul - Park Area",
                patient_name="Ajay Kumar",
                patient_age=45,
                patient_phone="9988776655"
            ),
        ]
        
        for inc in incidents:
            db.session.add(inc)
        print(f"  [OK] Added {len(incidents)} incidents")
        
        # Create hospitals
        hospitals = [
            Hospital(
                id="HOSP-001",
                name="Fortis Hospital Navi Mumbai",
                address="Sector 7, Vashi, Navi Mumbai",
                phone="02227570000",
                latitude=19.0760,
                longitude=72.8777,
                total_beds=150,
                available_beds=45,
                emergency_beds=8,
                icu_beds=3,
                has_trauma_center=True,
                has_cardiac_care=True,
                has_pediatric_care=True
            ),
            Hospital(
                id="HOSP-002",
                name="Apollo Clinic Vashi",
                address="Sector 9, Vashi",
                phone="02227570001",
                latitude=19.0860,
                longitude=72.8877,
                total_beds=200,
                available_beds=78,
                emergency_beds=12,
                icu_beds=5,
                has_trauma_center=True,
                has_cardiac_care=True,
                has_pediatric_care=False
            ),
            Hospital(
                id="HOSP-003",
                name="Sai Nursing Home",
                address="Sector 10, Nerul",
                phone="02227570002",
                latitude=19.0900,
                longitude=72.8950,
                total_beds=80,
                available_beds=22,
                emergency_beds=5,
                icu_beds=2,
                has_trauma_center=False,
                has_cardiac_care=True,
                has_pediatric_care=False
            ),
            Hospital(
                id="HOSP-004",
                name="Nerul Hospital",
                address="Main Road, Nerul",
                phone="02227570003",
                latitude=19.0820,
                longitude=72.8650,
                total_beds=120,
                available_beds=55,
                emergency_beds=7,
                icu_beds=3,
                has_trauma_center=True,
                has_cardiac_care=False,
                has_pediatric_care=True
            ),
        ]
        
        for hosp in hospitals:
            db.session.add(hosp)
        print(f"  [OK] Added {len(hospitals)} hospitals")
        
        # Commit all changes
        db.session.commit()
        print("\n[OK] Database seeded successfully!")

def reset_db(app):
    """Reset database - drop all tables"""
    with app.app_context():
        print("Dropping all tables...")
        db.drop_all()
        print("[OK] All tables dropped")
        
        # Recreate
        init_db(app)
        seed_db(app)

if __name__ == '__main__':
    # For manual testing
    from flask import Flask
    
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///navi_raksha.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--reset', action='store_true', help='Reset database')
    args = parser.parse_args()
    
    if args.reset:
        reset_db(app)
    else:
        init_db(app)
        seed_db(app)

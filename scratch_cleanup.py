import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate('firebase-key.json')
    firebase_admin.initialize_app(cred)

db = firestore.client()

def purge_firestore():
    print("Starting Firestore Purge...")
    
    # 1. Delete Incidents
    incs_ref = db.collection('incidents')
    docs = incs_ref.stream()
    count = 0
    for doc in docs:
        doc.reference.delete()
        count += 1
    print(f"Deleted {count} incidents.")
    
    # 2. Reset Ambulances
    ambs_ref = db.collection('ambulances')
    docs = ambs_ref.stream()
    count = 0
    for doc in docs:
        doc.reference.update({
            'status': 'available',
            'assigned_incident': None
        })
        count += 1
    print(f"Reset {count} ambulances.")
    print("Database is now clean!")

if __name__ == "__main__":
    purge_firestore()

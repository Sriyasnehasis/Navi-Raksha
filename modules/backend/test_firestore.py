import firebase_admin
from firebase_admin import credentials, firestore
import os
import sys

# Add current dir to path
sys.path.append(os.path.dirname(__file__))

def test_connection():
    print("\n[DIAGNOSTIC] --- NAVIRAKSHA FIRESTORE ---")
    
    # 1. Check Key File
    key_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'firebase-key.json'))
    print(f"Checking Key at: {key_path}")
    
    if not os.path.exists(key_path):
        print("ERROR: firebase-key.json NOT FOUND in root!")
        return

    try:
        # 2. Initialize
        cred = credentials.Certificate(key_path)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        
        db = firestore.client()
        project_id = firebase_admin.get_app().project_id
        
        print(f"SUCCESS: Connected to Project: {project_id}")

        # 3. Test Write
        print("Attempting test write to 'diagnostics' collection...")
        doc_ref = db.collection('diagnostics').document('test_run')
        doc_ref.set({
            'status': 'Connection Successful',
            'message': 'If you see this, Firestore is WORKING!'
        })
        print("TEST WRITE SUCCESSFUL! Check your Firestore console.")
        
    except Exception as e:
        print(f"FAILED: {str(e)}")

if __name__ == "__main__":
    test_connection()

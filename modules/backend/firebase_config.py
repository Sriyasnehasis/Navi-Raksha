import firebase_admin
from firebase_admin import credentials, firestore
import os
import logging

logger = logging.getLogger(__name__)

_db = None

def init_firebase():
    global _db
    if _db is not None:
        return _db
    
    try:
        # Look for service account key
        key_path = os.path.join(os.path.dirname(__file__), '..', '..', 'firebase-key.json')
        
        if os.path.exists(key_path):
            cred = credentials.Certificate(key_path)
            firebase_admin.initialize_app(cred)
            _db = firestore.client()
            logger.info("✅ Firebase Admin initialized with service account")
        else:
            # Fallback to default credentials (useful for some cloud environments)
            try:
                firebase_admin.initialize_app()
                _db = firestore.client()
                logger.info("✅ Firebase Admin initialized with default credentials")
            except Exception:
                logger.warning("⚠️ Firebase credentials not found. Firebase features will be disabled.")
                _db = None
                
        return _db
    except Exception as e:
        logger.error(f"❌ Failed to initialize Firebase: {e}")
        return None

def get_firestore():
    global _db
    if _db is None:
        return init_firebase()
    return _db

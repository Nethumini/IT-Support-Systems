import joblib
import os
import pandas as pd
from pathlib import Path
import threading

class SLAService:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        # Only initialize once
        if self._initialized:
            return
        
        # Use Path to get absolute path relative to this file
        base_dir = Path(__file__).resolve().parent.parent  # backend/app/
        self.model_path = base_dir / "models" / "ml" / "sla_model.joblib"
        self.encoder_path = base_dir / "models" / "ml" / "category_encoder.joblib"
        self.model = None
        self.encoder = None
        self._load()
        self._initialized = True

    def _load(self):
        if self.model_path.exists() and self.encoder_path.exists():
            try:
                self.model = joblib.load(str(self.model_path))
                self.encoder = joblib.load(str(self.encoder_path))
            except Exception as e:
                print(f"Warning: Could not load SLA models: {e}")
                self.model = None
                self.encoder = None

    def predict_resolution_time(self, category, priority_str, description):
        if not self.model: return 0
        
        # 1. Convert Inputs to Numbers
        # Priority Map
        p_map = {"low": 1, "medium": 2, "high": 3}
        priority_val = p_map.get(priority_str.lower(), 2)
        
        # Word Count
        word_count = len(description.split())
        
        # Category Code (Handle unknown categories safely)
        try:
            cat_code = self.encoder.transform([category])[0]
        except:
            cat_code = 0 # Default to 0 if unknown
            
        # 2. Predict
        features = pd.DataFrame([[cat_code, priority_val, word_count]], 
                              columns=['category_code', 'priority', 'word_count'])
        
        predicted_hours = self.model.predict(features)[0]
        return round(max(0.5, predicted_hours), 1)

# Lazy initialization function
def get_or_initialize_sla_service():
    """
    Lazily initialize and return SLA service instance.
    Returns None if initialization fails (e.g., ML models missing).
    """
    try:
        return SLAService()
    except Exception as e:
        print(f"Error initializing SLA service: {e}")
        return None

sla_service = None
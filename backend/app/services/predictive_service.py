import joblib
import os
import logging

logger = logging.getLogger(__name__)

class PredictiveService:
    def __init__(self):
        # Path to the model we just created
        self.model_path = "app/models/ml/system_health_model.joblib"
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                logger.info("✅ ML Model loaded successfully")
            else:
                logger.warning("⚠️ ML Model file not found. Did you run train_model.py?")
        except Exception as e:
            logger.error(f"Failed to load ML model: {e}")

    def predict_health(self, cpu: float, ram: float, disk: float, temp: float) -> dict:
        if not self.model:
            return {"status": "unknown", "risk_score": 0, "message": "AI Model not loaded"}

        # Prepare the numbers for the AI
        features = [[cpu, ram, disk, temp]]
        
        # Ask the AI for a prediction
        # predict() gives 0 or 1. predict_proba() gives the % chance.
        prediction = self.model.predict(features)[0]
        probability = self.model.predict_proba(features)[0][1] # Chance of crashing

        risk_score = round(probability * 100, 1)

        if prediction == 1:
            return {
                "status": "critical",
                "risk_score": risk_score,
                "message": f"⚠️ CRITICAL: System failure likely! Risk: {risk_score}%"
            }
        else:
            return {
                "status": "healthy",
                "risk_score": risk_score,
                "message": "System is stable."
            }

# Create a single instance to be used by the API
predictive_service = PredictiveService()
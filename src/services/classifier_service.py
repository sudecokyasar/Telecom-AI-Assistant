import joblib
from pathlib import Path
import numpy as np

class TicketClassifierService:
    def __init__(self, model_path: Path):
        if not model_path.exists():
            raise FileNotFoundError(f"Model dosyası bulunamadı: {model_path}")
        self.pipeline = joblib.load(model_path)
    
    def predict(self, text: str) -> dict:
        category = self.pipeline.predict([text])[0]
        probabilities = self.pipeline.predict_proba([text])[0]
        confidence = float(np.max(probabilities))
        
        return {
            "category": category,
            "confidence": round(confidence * 100, 2)
        }
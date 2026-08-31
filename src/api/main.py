from pathlib import Path
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
import json

from src.services.classifier_service import TicketClassifierService
from src.services.rag_service import RAGAssistantService
from typing import List, Dict, Optional

# Proje Yolları
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
MODEL_PATH = ROOT_DIR / "models" / "ticket_classifier.pkl"
CHROMA_DIR = ROOT_DIR / "data" / "chroma_db"
ENV_PATH = ROOT_DIR / ".env"

app = FastAPI(
    title="Telecom AI Support & Fault Resolution API",
    description="Telekom müşteri biletlerini otomatik sınıflandıran ve RAG ile çözüm üreten AI servisi.",
    version="1.0.0"
)

# Servisleri başlat
try:
    classifier_service = TicketClassifierService(MODEL_PATH)
    rag_service = RAGAssistantService(CHROMA_DIR, ENV_PATH)
except Exception as e:
    print(f"Başlatma Hatası: {e}")
    classifier_service = None
    rag_service = None

class CategoryResponse(BaseModel):
    category: str
    confidence_score: float

class FullResolutionResponse(BaseModel):
    ticket_text: str
    category: str
    confidence_score: float
    retrieved_sources: list[str]
    ai_resolution: str

# --- Endpoint'ler ---
@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "classifier_ready": classifier_service is not None,
        "rag_ready": rag_service is not None
    }

@app.post("/predict-category", response_model=CategoryResponse, tags=["Classification"])
def predict_category(request: TicketRequest):
    if not classifier_service:
        raise HTTPException(status_code=500, detail="Sınıflandırıcı model yüklenemedi.")
    
    result = classifier_service.predict(request.ticket_text)
    return {
        "category": result["category"],
        "confidence_score": result["confidence"]
    }

class TicketRequest(BaseModel):
    ticket_text: str = Field(..., min_length=1, example="Dediğiniz adımı yaptım ama ışık hala kırmızı.")
    chat_history: Optional[List[Dict[str, str]]] = Field(default=[], example=[
        {"role": "user", "content": "İnternetim kesildi."},
        {"role": "assistant", "content": "Modemi kapatıp 30 saniye bekleyin."}
    ])

@app.post("/resolve-ticket", response_model=FullResolutionResponse, tags=["RAG Resolution"])
def resolve_ticket(request: TicketRequest):
    if not classifier_service or not rag_service:
        raise HTTPException(status_code=500, detail="AI servisleri aktif değil.")
    
    # Kategori tahmini
    cat_res = classifier_service.predict(request.ticket_text)
    
    # RAG + LLM (Geçmiş konuşmalarla birlikte)
    rag_res = rag_service.generate_resolution(
        ticket_text=request.ticket_text,
        category_info=cat_res,
        chat_history=request.chat_history
    )
    
    return {
        "ticket_text": request.ticket_text,
        "category": cat_res["category"],
        "confidence_score": cat_res["confidence"],
        "retrieved_sources": rag_res["sources"],
        "ai_resolution": rag_res["response"]
    }

CAMARA_DATA_PATH = Path("data/camara_registry.json")

def load_camara_db():
    if not CAMARA_DATA_PATH.exists():
        return {}
    with open(CAMARA_DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# CAMARA Device Status API (GSMA Standard)
@app.get("/camara/device-status/v0/connectivity", tags=["GSMA CAMARA API"])
def get_device_connectivity(phone_number: str = Query(..., description="E.164 Telefon Numarası")):
    db = load_camara_db()
    subscriber = db.get(phone_number)
    if not subscriber:
        raise HTTPException(status_code=404, detail="Cihaz veya abone bulunamadı.")
    return {
        "phoneNumber": phone_number,
        "deviceStatus": subscriber["device_status"]
    }

# CAMARA SIM / Roaming Status API (GSMA Standard)
@app.get("/camara/sim-manager/v0/roaming-status", tags=["GSMA CAMARA API"])
def get_sim_roaming_status(phone_number: str = Query(..., description="E.164 Telefon Numarası")):
    db = load_camara_db()
    subscriber = db.get(phone_number)
    if not subscriber:
        raise HTTPException(status_code=404, detail="SIM kaydı bulunamadı.")
    return {
        "phoneNumber": phone_number,
        "simDetails": subscriber["sim_status"],
        "billing": subscriber["billing_summary"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
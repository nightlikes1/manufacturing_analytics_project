from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import polars as pl
import pandas as pd
import os
from src.features import create_features
from src.utils import load_config

# Yükleme ve Ayarlar
config = load_config()
app = FastAPI(
    title="Manufacturing Analytics API",
    description="Endüstriyel Kestirimci Bakım Modeli API'si",
    version="1.0.0"
)

# Modeli Yükle
model_path = config["model"]["path"]
if not os.path.exists(model_path):
    raise FileNotFoundError(f"Model dosyası bulunamadı: {model_path}")

model = joblib.load(model_path)

# İstek Şeması
class PredictionRequest(BaseModel):
    air_temp: float
    process_temp: float
    rpm: int
    torque: float
    tool_wear: int

class PredictionResponse(BaseModel):
    prediction: int
    probability: float
    status: str

@app.get("/")
def read_root():
    return {"message": "API Çalışıyor. Tahmin için /predict endpoint'ini kullanın."}

@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    # Veriyi hazırla
    data = {
        "air_temp": request.air_temp,
        "process_temp": request.process_temp,
        "rpm": request.rpm,
        "torque": request.torque,
        "tool_wear": request.tool_wear
    }
    
    # Feature Engineering
    df = pl.DataFrame([data])
    full_df = create_features(df).to_pandas()
    
    # Modelin beklediği sütunları seç
    model_features = config["features"]["numerical"]
    df_processed = full_df[model_features]
    
    # Tahmin
    prediction = model.predict(df_processed)[0]
    probability = model.predict_proba(df_processed)[0][1]
    
    status = "Arıza Riski Yüksek" if prediction == 1 else "Normal"
    
    return {
        "prediction": int(prediction),
        "probability": float(probability),
        "status": status
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

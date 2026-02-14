from fastapi.testclient import TestClient
from src.api import app
import pytest

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "API Çalışıyor. Tahmin için /predict endpoint'ini kullanın."}

def test_predict_normal_case():
    """
    Geçerli bir veri ile tahmin isteği atıldığında doğru formatta cevap dönmeli.
    """
    payload = {
        "air_temp": 300.0,
        "process_temp": 310.0,
        "rpm": 1500,
        "torque": 40.0,
        "tool_wear": 100
    }
    
    response = client.post("/predict", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    # Cevap şemasını kontrol et
    assert "prediction" in data
    assert "probability" in data
    assert "status" in data
    assert isinstance(data["prediction"], int)
    assert data["prediction"] in [0, 1]

def test_predict_missing_field():
    """
    Eksik veri gönderildiğinde 422 Hatası dönmeli (FastAPI validation).
    """
    payload = {
        "air_temp": 300.0,
        # "process_temp" eksik
        "rpm": 1500,
        "torque": 40.0
    }
    
    response = client.post("/predict", json=payload)
    assert response.status_code == 422

# Not: Modelin doğruluğunu test etmiyoruz (o MLflow'un işi), 
# sadece API'nin çalışıp çalışmadığını (kontrat testi) yapıyoruz.

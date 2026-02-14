import joblib
import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from src.utils import get_logger

logger = get_logger(__name__)

def train_model(X, y, params: dict):
    """
    Trains a Random Forest model.
    """
    logger.info("Training model...")
    logger.info("Training model...")
    # Default parametreleri al
    params = params or {}
    n_estimators = params.get("n_estimators", 100)
    random_state = params.get("random_state", 42)
    
    # Parametreleri temizle (sadece sklearn'ün kabul ettiklerini gönderelim diyeceğim ama
    # kwargs ile hepsini yollamak daha kolay, fakat RandomForestClassifier **kwargs kabul ediyor mu?
    # Evet ediyor. Ama biz güvenli olsun diye bilinenleri çekip kalanı kwargs olarak verelim.
    # En kolayı: sözlüğü direkt unpacking yapmak.
    
    model = RandomForestClassifier(**params)
    model.fit(X, y)
    
    logger.info("Model training completed.")
    return model

def evaluate_model(model, X_test, y_test):
    """
    Evaluates the model and logs the classification report.
    """
    logger.info("Evaluating model...")
    y_pred = model.predict(X_test)
    
    report = classification_report(y_test, y_pred)
    logger.info("\n" + report)
    
    return report

def save_model(model, path: str):
    """
    Saves the trained model using joblib.
    """
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(model, path)
        logger.info(f"Model saved to {path}")
    except Exception as e:
        logger.error(f"Error saving model: {e}")
        raise e

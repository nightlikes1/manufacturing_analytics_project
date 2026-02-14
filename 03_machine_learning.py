import polars as pl
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os

def model_egitimi():
    # 1. İşlenmiş veriyi yükle
    df = pl.read_csv("data/processed/refined_sensor_data.csv")
    
    # 2. Özellik seçimi (Modelin öğreneceği sütunlar)
    features = ["air_temp_c", "process_temp_c", "rpm", "torque", "tool_wear", "power_factor", "temp_diff"]
    X = df.select(features).to_pandas()
    y = df.select("target").to_pandas().values.ravel()
    
    # 3. Veriyi böl (%80 Eğitim, %20 Test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print("🧠 Model eğitiliyor (Random Forest)...")
    # 4. Modeli kur ve eğit
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # 5. Tahmin ve Değerlendirme
    y_pred = model.predict(X_test)
    
    print("\n--- MODEL PERFORMANS RAPORU ---")
    print(classification_report(y_test, y_pred))
    
    # 6. Modeli Kaydet (İleride kullanmak için - Deployment hazırlığı)
    os.makedirs("src/models", exist_ok=True)
    joblib.dump(model, "src/models/maintenance_model.pkl")
    print("\n✅ Model 'src/models/maintenance_model.pkl' olarak kaydedildi.")

if __name__ == "__main__":
    model_egitimi()
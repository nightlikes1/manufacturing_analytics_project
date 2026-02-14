import polars as pl
import os

def veriyi_indir_ve_hazirla():
    # Klasörleri oluştur (Düzenli çalışmak profesyonelliktir)
    os.makedirs("data/raw", exist_ok=True)
    
    print("🚀 Gerçek dünya üretim verisi indiriliyor...")
    
    # UCI Machine Learning Repository - Predictive Maintenance Dataset
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/00601/ai4i2020.csv"
    
    # Polars ile veriyi oku
    df = pl.read_csv(url)
    
    # Sütun isimlerini daha profesyonel hale getirelim
    df = df.rename({
        "UDI": "id",
        "Air temperature [K]": "air_temp",
        "Process temperature [K]": "process_temp",
        "Rotational speed [rpm]": "rpm",
        "Torque [Nm]": "torque",
        "Tool wear [min]": "tool_wear",
        "Machine failure": "target"
    })
    
    # Veriyi kaydet
    df.write_csv("data/raw/sensor_data.csv")
    
    print("✅ Başarılı! Veri seti 'data/raw/sensor_data.csv' konumuna kaydedildi.")
    print(f"📊 Toplam Satır Sayısı: {df.height}")
    print(df.head(3))

if __name__ == "__main__":
    veriyi_indir_ve_hazirla()
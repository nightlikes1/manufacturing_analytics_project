import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt

def analiz_ve_ozellik_muhendisligi():
    # 1. Veriyi yükle
    df = pl.read_csv("data/raw/sensor_data.csv")
    
    # 2. Veri Mühendisliği: Yeni anlamlı özellikler türetme
    df = df.with_columns([
        # Kelvin -> Celsius dönüşümü
        (pl.col("air_temp") - 273.15).alias("air_temp_c"),
        (pl.col("process_temp") - 273.15).alias("process_temp_c"),
        
        # Güç Faktörü (Tork * RPM) - Makine ne kadar zorlanıyor?
        (pl.col("torque") * pl.col("rpm")).alias("power_factor"),
        
        # Sıcaklık Artışı (İşlem sırasındaki ısınma miktarı)
        (pl.col("process_temp") - pl.col("air_temp")).alias("temp_diff")
    ])
    
    print("✅ Yeni özellikler (Features) oluşturuldu.")
    
    # 3. Analiz: Korelasyon Matrisi (Hangi değişken arıza ile ilişkili?)
    # Görselleştirme için Pandas'a geçici dönüş (Seaborn uyumu için)
    pdf = df.to_pandas()
    plt.figure(figsize=(10, 8))
    correlation_matrix = pdf.select_dtypes(include=['float64', 'int64']).corr()
    
    sns.heatmap(correlation_matrix, annot=True, cmap='RdYlGn', fmt=".2f")
    plt.title("Sensörler ve Arıza Arasındaki İlişki")
    
    # Grafiği kaydet
    os.makedirs("outputs", exist_ok=True)
    plt.savefig("outputs/correlation_analysis.png")
    print("📊 Analiz grafiği 'outputs/correlation_analysis.png' olarak kaydedildi.")
    
    # İşlenmiş veriyi kaydet (Silver Layer)
    os.makedirs("data/processed", exist_ok=True)
    df.write_csv("data/processed/refined_sensor_data.csv")
    print("💾 İşlenmiş veri 'data/processed/refined_sensor_data.csv' konumuna kaydedildi.")

if __name__ == "__main__":
    import os
    analiz_ve_ozellik_muhendisligi()
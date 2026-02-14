import polars as pl
import plotly.express as px
import plotly.graph_objects as go
import os

def dashboard_olustur():
    # 1. İşlenmiş veriyi yükle
    if not os.path.exists("data/processed/refined_sensor_data.csv"):
        print("❌ Hata: İşlenmiş veri bulunamadı! Lütfen önce 02_analysis_and_features.py dosyasını çalıştır.")
        return

    df = pl.read_csv("data/processed/refined_sensor_data.csv").to_pandas()
    
    print("🎨 Dashboard hazırlanıyor...")

    # 2. Ana Grafik: Tork vs RPM (Arıza Durumuna Göre Renklendirilmiş)
    # Bu grafik makinenin 'güvenli çalışma bölgesini' gösterir.
    fig = px.scatter(
        df, x="rpm", y="torque", color="target",
        title="<b>Fabrika Makine Sağlık İzleme Dashboard</b>",
        labels={"target": "Arıza Durumu (0:Normal, 1:Arıza)", "rpm": "Devir Sayısı (RPM)", "torque": "Tork (Nm)"},
        hover_data=['air_temp_c', 'tool_wear', 'power_factor'],
        color_continuous_scale=["#2ecc71", "#e74c3c"], # Yeşil (Normal) ve Kırmızı (Arıza)
        template="plotly_dark" # Profesyonel koyu tema
    )

    # 3. Kritik Sınırları Çizelim (Mühendislik İçgörüsü)
    fig.add_hline(y=60, line_dash="dash", line_color="yellow", 
                 annotation_text="Yüksek Tork Riski", annotation_position="top left")
    
    # 4. Çıktı Klasörünü Kontrol Et ve Kaydet
    os.makedirs("outputs", exist_ok=True)
    output_path = "outputs/production_dashboard.html"
    fig.write_html(output_path)
    
    print(f"✅ Dashboard başarıyla oluşturuldu: {output_path}")
    print("💡 ŞİMDİ YAPMAN GEREKEN: 'outputs' klasörüne git ve 'production_dashboard.html' dosyasına çift tıkla!")

if __name__ == "__main__":
    dashboard_olustur()
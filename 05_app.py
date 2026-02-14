import streamlit as st
import polars as pl
import pandas as pd
import joblib
import plotly.express as px
import os
from src.utils import load_config, get_logger
from src.features import create_features
import shap
import matplotlib.pyplot as plt
import time
from src.simulator import generate_live_data
from src.database import init_db, insert_record, fetch_history

# Veritabanını Başlat (Eğer yoksa oluşturur)
init_db()

# Konfigürasyonu yükle
config = load_config()
logger = get_logger("Streamlit App")

# Sayfa Ayarları
st.set_page_config(
    page_title="Üretim Analitiği Dashboard",
    page_icon="🏭",
    layout="wide"
)

# Modeli Yükle
@st.cache_resource
def load_model():
    model_path = config["model"]["path"]
    if os.path.exists(model_path):
        return joblib.load(model_path)
    return None

model = load_model()

# Başlık ve Açıklama
st.title("🏭 Endüstriyel Kestirimci Bakım Dashboard")
st.markdown("""
Bu uygulama, üretim hattındaki makinelerden gelen sensör verilerini analiz eder ve 
**Yapay Zeka** kullanarak olası arızaları önceden tahmin eder.
""")

# Yan Menü - Mod Seçimi
st.sidebar.header("⚙️ Veri Kaynağı")
mode = st.sidebar.radio("Mod Seçiniz", ["Manuel Giriş", "Canlı Veri Simülasyonu 📡"])

def user_input_features():
    # Manuel Mod
    if mode == "Manuel Giriş":
        st.sidebar.subheader("Manuel Ayarlar")
        air_temp = st.sidebar.slider("Hava Sıcaklığı [K]", 295.0, 305.0, 300.0)
        process_temp = st.sidebar.slider("İşlem Sıcaklığı [K]", 305.0, 315.0, 310.0)
        rpm = st.sidebar.slider("Devir Hızı [RPM]", 1100, 2900, 1500)
        torque = st.sidebar.slider("Tork [Nm]", 0.0, 80.0, 40.0)
        tool_wear = st.sidebar.slider("Alet Aşınması [min]", 0, 300, 100)
    
    # Canlı Simülasyon
    else:
        st.sidebar.markdown("---")
        st.sidebar.info("📡 Canlı veri akışı simüle ediliyor...")
        
        
        # Session State kullanarak veriyi tutabiliriz
        if 'live_data' not in st.session_state:
            st.session_state['live_data'] = generate_live_data()
            
        sim_data = st.session_state['live_data']
        
        # Her 2 saniyede bir yenilemek için rerun butonu
        if st.sidebar.button("Veriyi Yenile 🔄"):
             st.session_state['live_data'] = generate_live_data()
             sim_data = st.session_state['live_data'] # Güncel veriyi al
             
        # Otomatik akış kontrolü (Checkbox)
        # Key vererek session state'de tutulmasını sağlıyoruz
        st.sidebar.checkbox("Otomatik Yenile (2sn)", key="auto_refresh")
            
        # Değerleri gösterelim (düzenlenemez olarak)
        
        # Değerleri gösterelim (düzenlenemez olarak)
        st.sidebar.metric("Hava Sıcaklığı", f"{sim_data['air_temp']:.2f} K")
        st.sidebar.metric("Tork", f"{sim_data['torque']:.2f} Nm")
        
        # Değerleri değişkenlere ata ki aşağıdaki 'data' sözlüğü kullansın
        air_temp = sim_data['air_temp']
        process_temp = sim_data['process_temp']
        rpm = sim_data['rpm']
        torque = sim_data['torque']
        tool_wear = sim_data['tool_wear']

    # Ham veri oluştur (Hesaplanan sütunlar olmadan)
    data = {
        "air_temp": air_temp,
        "process_temp": process_temp,
        "rpm": rpm,
        "torque": torque,
        "tool_wear": tool_wear
    }
    
    # Polars DataFrame oluştur ve Feature Engineering uygula
    df = pl.DataFrame([data])
    df_processed = create_features(df)
    
    # Modele uygun pandas dataframe'e çevir
    full_df = df_processed.to_pandas()
    
    # Modelin beklediği sütunları seç (params.yaml'dan)
    model_features = config["features"]["numerical"]
    return full_df[model_features], full_df

input_df, full_input_df = user_input_features()

# Ana Sayfa Düzeni (Kolonlar)

# Sekmeler Oluştur
tab_live, tab_history = st.tabs(["📡 Canlı İzleme", "📚 Geçmiş Kayıtlar"])

with tab_live:
    # KPI Metrikleri
    st.markdown("### 📊 Anlık Durum Özeti")
    kpi1, kpi2, kpi3 = st.columns(3)

    # Hesaplanan değerleri al (full_input_df'ten)
    power_factor = full_input_df["power_factor"][0]
    temp_diff = full_input_df["temp_diff"][0]

    if model:
        # Model sadece input_df (filtrelenmiş) kullanır
        prediction = model.predict(input_df)[0]
        probability = model.predict_proba(input_df)[0][1]
        
        # --- VERİTABANI KAYDI ---
        # Sadece otomatik yenileme modunda veya butonla tetiklenen modda kaydetmek mantıklı.
        # Manuel modda sürekli slider değişiminde kayıt atmasın (demo için).
        # Ama kullanıcı "Manuel" girip sonucu görmek istiyor. Kaydedelim.
        # Kayıt verisi hazırla (Raw inputlar + Tahmin)
        record_data = full_input_df.to_dict(orient="records")[0]
        insert_record(record_data, int(prediction), float(probability))
        # ------------------------
        
        kpi1.metric(
            label="Tahmin Edilen Durum",
            value="ARIZA RİSKİ" if prediction == 1 else "NORMAL",
            delta="-Riskli" if prediction == 1 else "+Güvenli",
            delta_color="inverse"
        )
        
        kpi2.metric(
            label="Arıza Olasılığı",
            value=f"%{probability*100:.1f}",
            delta=f"{probability*100:.1f}% Risk",
            delta_color="inverse"
        )
    else:
        kpi1.metric("Durum", "Model Yok")
        kpi2.metric("Olasılık", "-")

    kpi3.metric(
        label="Güç Faktörü (W)",
        value=f"{power_factor:.2f}",
        help="Tork x Devir Hızı"
    )

    st.markdown("---")

    # Ana Sayfa Düzeni (Kolonlar)
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("📝 Girilen Değerler")
        # Sadece ham verileri gösterelim, kafa karışıklığı olmasın
        display_cols = ["rpm", "torque", "tool_wear", "air_temp", "process_temp"]
        # full_input_df'te tüm sütunlar var
        st.write(full_input_df[display_cols].T)

        
        st.subheader("🔍 Tahmin")
        if model:
            # Tahmin zaten yukarıda yapıldı (prediction, probability)
            if prediction == 1:
                st.error(f"⚠️ DİKKAT: Arıza Riski Yüksek! (%{probability*100:.2f})")
            else:
                st.success(f"✅ Durum Normal (%{probability*100:.2f} Arıza Riski)")
        else:
            st.warning("Model dosyası bulunamadı! Lütfen önce eğitimi çalıştırın.")

    with col2:
        st.subheader("📊 Analiz Grafiği")
        # Geçmiş veriyi yükle (bağlam oluşturmak için)
        processed_path = config["data"]["processed_path"]
        if os.path.exists(processed_path):
            df_hist = pl.read_csv(processed_path).to_pandas()
            
            # Görselleştirme
            fig = px.scatter(
                df_hist, x="rpm", y="torque", color="target",
                color_continuous_scale=["#2ecc71", "#e74c3c"], # Yeşil, Kırmızı
                title="Makine Çalışma Zarfları (RPM vs Tork)",
                opacity=0.3
            )
            
            # Güncel noktayı büyük bir işaretle ekle (full_input_df kullanmalıyız)
            fig.add_scatter(
                x=full_input_df["rpm"], 
                y=full_input_df["torque"],
                mode='markers',
                marker=dict(size=20, color='blue', symbol='x'),
                name="Güncel Değer"
            )
            
            # Kritik sınır
            fig.add_hline(y=60, line_dash="dash", line_color="yellow", annotation_text="Risk Sınırı")
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Geçmiş veri bulunamadı, grafik oluşturulamıyor.")

    st.markdown("---")
    st.subheader("🤖 Yapay Zeka Karar Analizi (XAI)")

    if model:
        # SHAP Analizi
        try:
            # Explainer oluştur
            explainer = shap.TreeExplainer(model)
            
            # Tek bir gözlem için SHAP değerlerini hesapla
            shap_values = explainer(input_df)
            
            # Görselleştirme
            col_shap1, col_shap2 = st.columns([2, 1])
            
            with col_shap1:
                st.markdown("**Neden bu sonuç çıktı? (Arıza Riski Analizi)**")
                
                # Waterfall Plot
                fig_shap, ax = plt.subplots(figsize=(8, 5))
                
                explanation_to_plot = None
                if len(shap_values.shape) == 3:
                     # (Sample, Feature, Class) -> (1, 7, 2) -> Arıza (1) sınıfı
                     explanation_to_plot = shap_values[0, :, 1]
                else:
                     # (Sample, Feature) -> (1, 7)
                     explanation_to_plot = shap_values[0]
                
                shap.plots.waterfall(explanation_to_plot, show=False)
                st.pyplot(fig_shap, clear_figure=True)
                
            with col_shap2:
                st.info("""
                **Grafik Nasıl Okunur?**
                - **Kırmızı Çubuklar:** Arıza riskini ARTIRAN faktörler.
                - **Mavi Çubuklar:** Arıza riskini AZALTAN faktörler.
                - **E[f(x)]:** Ortalama risk değeri.
                - **f(x):** Modelin hesapladığı risk.
                """)
                
        except Exception as e:
            import traceback
            st.error(f"SHAP analizi hatası: {e}")
            # Hata detayını gizleyip daha temiz bir mesaj verebiliriz veya geliştirme aşamasında açık tutabiliriz.
            # st.code(traceback.format_exc())

with tab_history:
    st.markdown("### 📜 Geçmiş Raporlar")
    st.info("Sistem tarafından kaydedilen son 100 işlem kaydı aşağıdadır.")
    
    # Veritabanından verileri çek
    df_logs = fetch_history(limit=100)
    
    if not df_logs.empty:
        # Zaman Serisi Grafiği (Risk Olasılığı)
        st.subheader("Risk Trendi")
        fig_trend = px.line(df_logs, x="timestamp", y="probability", 
                            title="Zaman İçinde Arıza Riski Değişimi",
                            markers=True)
        # Riskli bölgeyi kırmızı yapalım (0.5 üstü)
        fig_trend.add_hline(y=0.5, line_dash="dash", line_color="red", annotation_text="Kritik Eşik")
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # Detaylı Tablo
        st.subheader("Kayıt Detayları")
        st.dataframe(df_logs, use_container_width=True)
        
        # İndirme Butonu
        csv = df_logs.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Raporu İndir (CSV) 📥",
            data=csv,
            file_name='uretim_raporu.csv',
            mime='text/csv',
        )
    else:
        st.warning("Henüz hiç kayıt bulunamadı.")

# ---------------------------------------------------------
# OTOMATİK YENİLEME MANTIĞI (Scriptin en sonunda olmalı)
# ---------------------------------------------------------
# Eğer "Canlı Veri" modundaysak ve kullanıcı "Otomatik Yenile"yi seçtiyse:
# 1. Tüm grafikleri çizdir (yukarıdaki kodlar çalıştı).
# 2. 2 saniye bekle.
# 3. Yeni veriyi üret ve kaydet.
# 4. Sayfayı yenile (Başa dön).

if mode == "Canlı Veri Simülasyonu 📡" and st.session_state.get("auto_refresh"):
    time.sleep(2)
    st.session_state["live_data"] = generate_live_data()
    st.rerun()




# 🏭 Endüstriyel Kestirimci Bakım ve Makine Arıza Tahmini

Bu proje, üretim hattındaki makinelerden gelen sensör verilerini kullanarak olası arızaları önceden tahmin eden uçtan uca bir **Veri Bilimi ve Makine Öğrenmesi** çözümüdür. Proje, veri çekme aşamasından Docker ile dağıtım (deployment) aşamasına kadar tüm modern veri hatlarını (pipeline) kapsar.

## 🚀 Öne Çıkan Özellikler
- **Yüksek Performanslı ETL:** Geleneksel Pandas yerine Rust tabanlı **Polars** kütüphanesi kullanılarak optimize edilmiş veri işleme.
- **Gelişmiş Modelleme:** Random Forest algoritması ile arızaları **%82 Recall** oranıyla tespit etme.
- **İnteraktif Analitik:** Plotly ile hazırlanan, kritik tork ve devir sınırlarını gösteren dinamik dashboard.
- **Konteynerizasyon:** Her bilgisayarda aynı şekilde çalışması için **Docker** entegrasyonu.

## 🛠️ Kullanılan Teknolojiler
- **Dil:** Python 3.11
- **Veri İşleme:** Polars, NumPy, PyArrow
- **Makine Öğrenmesi:** Scikit-Learn
- **Görselleştirme:** Plotly, Seaborn, Matplotlib
- **Dağıtım:** Docker

## 📈 İş İçgörüleri (Insights)
Analizler sonucunda elde edilen kritik bulgular:
1. **Kritik Tork Sınırı:** Tork değerinin 60 Nm üzerine çıktığı durumlarda arıza riskinin %40 arttığı gözlemlendi.
2. **RPM ve Tork İlişkisi:** Arızaların büyük çoğunluğu düşük devir (RPM) ve yüksek tork kombinasyonunda gerçekleşiyor.
3. **Güç Faktörü:** Yeni türetilen `power_factor` değişkeni, arıza tahmininde en güçlü belirleyicilerden biri oldu.

## 🐳 Docker ile Çalıştırma
Projeyi bağımlılıklarla uğraşmadan çalıştırmak için:

```bash
# 1. İmajı oluşturun
docker build -t uretim-analiz-app .

# 2. Konteyneri çalıştırın
docker run --name aktif-analiz uretim-analiz-app
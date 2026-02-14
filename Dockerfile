# 1. Hafif bir Python imajı seçiyoruz
FROM python:3.11-slim

# 2. Çalışma dizinini belirliyoruz
WORKDIR /app

# 3. Sistem bağımlılıklarını yüklüyoruz (Görselleştirme kütüphaneleri için gerekebilir)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 4. Kütüphane listesini kopyalayıp yüklüyoruz
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Tüm proje dosyalarını kopyalıyoruz
COPY . .

# 6. Konteyner başladığında çalışacak komutu belirliyoruz 
# (Önce dashboard'u oluştursun sonra çalışmaya devam etsin)
CMD ["python", "04_dashboard_summary.py"]
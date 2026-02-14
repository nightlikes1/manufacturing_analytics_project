import psycopg2
import pandas as pd
from datetime import datetime
import os
from src.utils import get_logger

logger = get_logger(__name__)

# Docker ortam değişkenlerini al, yoksa varsayılanları (localhost) kullan
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "manufacturing_db")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASS = os.getenv("DB_PASS", "secret123")
DB_PORT = os.getenv("DB_PORT", "5432")

def get_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            port=DB_PORT
        )
        return conn
    except Exception as e:
        logger.error(f"Veritabanı bağlantı hatası: {e}")
        # Eğer bağlantı kurulamazsa None dönebilir veya hata fırlatabiliriz.
        # Uygulamanın çökmemesi için None dönüp yukarıda kontrol etmek daha iyi olabilir ama
        # Veritabanı kritik olduğu için hatayı loglayıp fırlatmak daha dürüst bir yaklaşım.
        raise e

def init_db():
    """
    Veritabanını ve gerekli tabloları oluşturur.
    PostgreSQL için tablo yapısı.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Logs tablosu: Sensör verileri + Model Tahminleri
        # Postgres'te AUTOINCREMENT yerine SERIAL kullanılır.
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            air_temp REAL,
            process_temp REAL,
            rpm INTEGER,
            torque REAL,
            tool_wear INTEGER,
            prediction INTEGER,
            probability REAL,
            status TEXT
        )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        logger.info("Veritabanı ve tablo kontrolü tamamlandı (PostgreSQL).")
    except Exception as e:
        logger.error(f"Tablo oluşturma hatası: {e}")

def insert_record(data: dict, prediction: int, probability: float):
    """
    Bir tahmin sonucunu veritabanına kaydeder.
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        status = "Riskli" if prediction == 1 else "Normal"
        # Postgres otomatik timestamp atar ama biz yine de gönderelim veya default bırakalım.
        # Python tarafında zamanı belirlemek daha kontrollü.
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Postgres yer tutucusu %s dir.
        cursor.execute("""
        INSERT INTO logs (timestamp, air_temp, process_temp, rpm, torque, tool_wear, prediction, probability, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            timestamp,
            data['air_temp'],
            data['process_temp'],
            data['rpm'],
            data['torque'],
            data['tool_wear'],
            prediction,
            probability,
            status
        ))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Kayıt ekleme hatası: {e}")

def fetch_history(limit=100) -> pd.DataFrame:
    """
    Son kayıtları DataFrame olarak getirir.
    """
    try:
        conn = get_connection()
        query = f"SELECT * FROM logs ORDER BY id DESC LIMIT {limit}"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except Exception as e:
        logger.error(f"Veri çekme hatası: {e}")
        return pd.DataFrame() # Hata durumunda boş df dön


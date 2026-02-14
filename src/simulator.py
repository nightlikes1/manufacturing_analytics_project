import random
import pandas as pd
import time

def generate_live_data():
    """
    Üretim hattındaki bir makineden geliyormuş gibi anlık sensör verisi üretir.
    Değerler normal dağılıma yakın ancak bazen anomali içerecek şekilde ayarlanmıştır.
    """
    # Ortalama değerler ve varyasyon (UCI veri setine dayalı tahminler)
    # Air Temp [K]: ~300, Process Temp [K]: ~310, RPM: ~1500, Torque: ~40, Wear: ~100
    
    air_temp = random.normalvariate(300, 2)
    process_temp = air_temp + random.normalvariate(10, 1) # Proses genelde havodan 10 derece sıcak
    
    # RPM ve Tork ters orantılıdır (bu fiziğe uygunluk sağlar!)
    rpm = random.normalvariate(1500, 100)
    torque = (40 * 1500) / rpm + random.normalvariate(0, 5) 
    
    tool_wear = random.randint(0, 250)
    
    # %5 İhtimalle Anomali (Arıza Riski) Oluşturalım
    if random.random() < 0.05:
        torque += 30 # Tork fırlasın
        tool_wear += 100 # Aşınma artmış olsun
    
    return {
        "air_temp": air_temp,
        "process_temp": process_temp,
        "rpm": int(rpm),
        "torque": torque,
        "tool_wear": tool_wear,
        "timestamp": pd.Timestamp.now()
    }

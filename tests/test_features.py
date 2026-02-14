import pytest
import polars as pl
from src.features import create_features

def test_create_features_correct_logic():
    """
    Özellik mühendisliğinin doğru hesaplama yaptığını test eder.
    """
    # Örnek DataFrame
    raw_data = {
        "air_temp": [300.0],
        "process_temp": [310.0],
        "rpm": [1500],
        "torque": [40.0],
        "tool_wear": [100]
    }
    df = pl.DataFrame(raw_data)
    
    # Fonksiyonu çalıştır
    result_df = create_features(df)
    
    # 1. Kelvin -> Celsius Dönüşümü (300K - 273.15 = 26.85C)
    air_temp_c = result_df["air_temp_c"][0]
    assert air_temp_c == pytest.approx(26.85, 0.01)
    
    # 2. Güç Faktörü (1500 * 40 = 60000)
    power_factor = result_df["power_factor"][0]
    assert power_factor == 60000.0
    
    # 3. Sıcaklık Farkı (310 - 300 = 10)
    temp_diff = result_df["temp_diff"][0]
    assert temp_diff == 10.0

def test_create_features_empty_dataframe():
    """
    Boş DataFrame verildiğinde hata vermeden boş dönmeli.
    """
    df = pl.DataFrame({})
    # Polars boş df operasyonunda hata verebilir veya vermeyebilir. 
    # Ancak create_features sütun isimlerine bağımlı.
    # Boş ama şeması doğru bir df verelim.
    df_schema = pl.DataFrame(schema={
        "air_temp": pl.Float64, "process_temp": pl.Float64, 
        "rpm": pl.Int64, "torque": pl.Float64, "tool_wear": pl.Int64
    })
    
    result_df = create_features(df_schema)
    assert result_df.height == 0
    assert "air_temp_c" in result_df.columns

import polars as pl
from src.utils import get_logger
import os

logger = get_logger(__name__)

def create_features(df: pl.DataFrame) -> pl.DataFrame:
    """
    Applies feature engineering to the raw dataframe.
    """
    logger.info("Starting feature engineering...")
    
    # Renaming columns (if needed, though ingestion usually handles this, 
    # but let's ensure consistency if we want to move renaming here or keep it in ingestion.
    # The original script renamed during ingestion. We'll assume ingestion handles renaming 
    # based on the original 01_ingestion.py, but we can double check. 
    # Actually 01_ingestion.py did renaming. Let's keep that separation or move it.
    # For now, let's assume the input df has the 'professional' names from ingestion.
    
    df = df.with_columns([
        # Kelvin -> Celsius
        (pl.col("air_temp") - 273.15).alias("air_temp_c"),
        (pl.col("process_temp") - 273.15).alias("process_temp_c"),
        
        # Power Factor
        (pl.col("torque") * pl.col("rpm")).alias("power_factor"),
        
        # Temp Diff
        (pl.col("process_temp") - pl.col("air_temp")).alias("temp_diff")
    ])
    
    logger.info("Feature engineering completed.")
    return df

def save_processed_data(df: pl.DataFrame, path: str):
    """
    Saves the processed dataframe to a CSV file.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.write_csv(path)
    logger.info(f"Processed data saved to {path}")

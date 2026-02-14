import polars as pl
import os
from src.utils import get_logger

logger = get_logger(__name__)

def ingest_data(url: str, raw_path: str) -> pl.DataFrame:
    """
    Downloads data from a URL and saves it to a local path.
    """
    if os.path.exists(raw_path):
        logger.info(f"Data already exists at {raw_path}")
        return pl.read_csv(raw_path)
        
    logger.info(f"Downloading data from {url}...")
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(raw_path), exist_ok=True)
        
        df = pl.read_csv(url)
        df.write_csv(raw_path)
        logger.info(f"Data saved to {raw_path}")
        return df
    except Exception as e:
        logger.error(f"Error downloading data: {e}")
        raise e

def load_data(path: str) -> pl.DataFrame:
    """
    Loads data from a local CSV file.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Data file not found at {path}")
    
    logger.info(f"Loading data from {path}...")
    return pl.read_csv(path)

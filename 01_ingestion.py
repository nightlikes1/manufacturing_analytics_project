import polars as pl
from src.utils import load_config, get_logger
from src.data import ingest_data

def main():
    logger = get_logger("Ingestion")
    config = load_config()
    
    url = config["data"]["raw_url"]
    save_path = config["data"]["raw_path"]
    
    logger.info("Starting Data Ingestion...")
    
    # Ingest data (download or load)
    df = ingest_data(url, save_path)
    
    # Renaming logic - kept here as part of "raw" preparation or could be moved to src/data.py
    # Since the original script did it, let's keep it consistent but clean.
    # Actually, let's check if ingest_data did it? No, ingest_data just returned raw read.
    # So we apply renaming here before "finalizing" the raw step or update ingest_data?
    # Better: Update ingest_data to optionally rename or do it here. 
    # Let's do it here to keep business logic visible but use method chaining.
    
    # Renaming logic - only if raw columns exist
    if "UDI" in df.columns:
        logger.info("Renaming columns...")
        df = df.rename({
            "UDI": "id",
            "Air temperature [K]": "air_temp",
            "Process temperature [K]": "process_temp",
            "Rotational speed [rpm]": "rpm",
            "Torque [Nm]": "torque",
            "Tool wear [min]": "tool_wear",
            "Machine failure": "target"
        })
    else:
        logger.info("Columns already renamed or not found.")
    
    # Save again if we modified it? 
    # Original script: read -> rename -> save.
    # My ingest_data: read -> save -> return. 
    # If I rename AFTER ingest_data, the saved file in ingest_data is the ORIGINAL raw with old names.
    # But 02 script expects new names.
    # So I should overwrite the file with renamed columns or change ingest_data to handle renaming.
    # Let's overwrite here for simplicity and to match the flow "Raw -> Clean Raw".
    
    df.write_csv(save_path)
    logger.info(f"Data renamed and saved again to {save_path}")
    
    logger.info(f"Total Rows: {df.height}")
    logger.info(f"\n{df.head(3)}")

if __name__ == "__main__":
    main()
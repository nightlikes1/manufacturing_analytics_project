import polars as pl
import seaborn as sns
import matplotlib.pyplot as plt
import os
from src.utils import load_config, get_logger
from src.features import create_features

def main():
    logger = get_logger("Analysis & Features")
    config = load_config()
    
    raw_path = config["data"]["raw_path"]
    processed_path = config["data"]["processed_path"]
    
    # 1. Load Data
    logger.info(f"Loading raw data from {raw_path}")
    if not os.path.exists(raw_path):
        logger.error("Raw data not found! Run 01_ingestion.py first.")
        return

    df = pl.read_csv(raw_path)
    
    # 2. Feature Engineering
    df = create_features(df)
    
    # 3. Analysis: Correlation Matrix
    logger.info("Generating correlation matrix...")
    pdf = df.to_pandas()
    plt.figure(figsize=(10, 8))
    correlation_matrix = pdf.select_dtypes(include=['float64', 'int64']).corr()
    
    sns.heatmap(correlation_matrix, annot=True, cmap='RdYlGn', fmt=".2f")
    plt.title("Correlation Analysis")
    
    output_plot = config.get("reports", {}).get("correlation_plot", "outputs/correlation_analysis.png")
    os.makedirs(os.path.dirname(output_plot), exist_ok=True)
    plt.savefig(output_plot)
    logger.info(f"Correlation plot saved to {output_plot}")
    
    # 4. Save Processed Data
    os.makedirs(os.path.dirname(processed_path), exist_ok=True)
    df.write_csv(processed_path)
    logger.info(f"Processed data saved to {processed_path}")

if __name__ == "__main__":
    main()
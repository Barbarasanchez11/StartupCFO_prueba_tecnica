import pandas as pd
from src.config import INPUT_PL_FILE, MAYOR_FILE, COLUMN_MAPPING

def load_data(file_path):
    """Generic function to load an Excel file."""
    try:
        print(f"[INFO] Reading file: {file_path}")
    
        df = pd.read_excel(file_path, engine='openpyxl')
        print(f"[SUCCESS] Loaded {len(df)} rows from {file_path}")
        return df
    except FileNotFoundError:
        print(f"[ERROR] File not found: {file_path}. Please check the data folder.")
        return None
    except Exception as e:
        print(f"[ERROR] An unexpected error occurred: {e}")
        return None

def normalize_mayor(df):
    """Rename columns in Mayor to match InputPL structure."""
    if df is not None:
        print(f"[INFO] Normalizing columns using mapping: {COLUMN_MAPPING}")
        df = df.rename(columns=COLUMN_MAPPING)
    return df

def get_prepared_data():
    """Main function to load and prepare both datasets."""
    # 1. Load InputPL
    input_pl_df = load_data(INPUT_PL_FILE)
    
    # 2. Load Mayor
    mayor_df = load_data(MAYOR_FILE)
    
    # 3. Normalize Mayor
    mayor_df = normalize_mayor(mayor_df)
    
    return input_pl_df, mayor_df

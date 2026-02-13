import pandas as pd
from src.config import INPUT_PL_FILE, MAYOR_FILE, COLUMN_MAPPING

def load_data(file_path):
    """
    Generic function to load an Excel file.
    """
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

def normalize_data(df, is_mayor=False):
    """
    Standardize column names and data types (especially dates).
    """
    if df is None:
        return None

    # Si es el archivo del Mayor, renombro las columnas primero
    if is_mayor:
        print(f"[INFO] Normalizing Mayor columns...")
        df = df.rename(columns=COLUMN_MAPPING)

    # Me aseguro de que la columna 'Fecha' sea de tipo datetime en ambos
    # Esto evita el error de tipos al hacer el merge
    if 'Fecha' in df.columns:
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')
    
    return df

def get_prepared_data():
    """
    Main function to load and prepare both datasets.
    """
    # 1. Cargo el InputPL y lo normalizo
    input_df = load_data(INPUT_PL_FILE)
    input_df = normalize_data(input_df, is_mayor=False)
    
    # 2. Cargo el Mayor y lo normalizo
    mayor_df = load_data(MAYOR_FILE)
    mayor_df = normalize_data(mayor_df, is_mayor=True)
    
    return input_df, mayor_df

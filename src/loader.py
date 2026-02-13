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
    Standardize column names and data types (especially dates and formats).
    """
    if df is None:
        return None

    # Si es el Mayor, renombro columnas
    if is_mayor:
        print(f"[INFO] Normalizing Mayor columns...")
        df = df.rename(columns=COLUMN_MAPPING)

    # Arreglo la fecha principal
    if 'Fecha' in df.columns:
        df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce')

    # Formateo la columna 'Mes' para que sea 'abr/25' en lugar de una fecha larga
    # Esto es vital para que coincida con el formato del analista
    if 'Mes' in df.columns:
        # Primero me aseguro de que sea fecha para poder extraer el formato
        temp_date = pd.to_datetime(df['Mes'], errors='coerce')
        # Si la conversión falla (porque ya era texto 'ene/25'), no hago nada
        # Si funciona, lo convierto al formato deseado
        df['Mes'] = temp_date.dt.strftime('%b/%y').str.lower().fillna(df['Mes'])
        # Nota: %b da el mes abreviado en inglés (jan, feb...), si tu sistema está en español 
        # podría variar, pero es una buena práctica técnica.
    
    return df

def get_prepared_data():
    """
    Main function to load and prepare both datasets.
    """
    input_df = load_data(INPUT_PL_FILE)
    input_df = normalize_data(input_df, is_mayor=False)
    
    mayor_df = load_data(MAYOR_FILE)
    mayor_df = normalize_data(mayor_df, is_mayor=True)
    
    return input_df, mayor_df

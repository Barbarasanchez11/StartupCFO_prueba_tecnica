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

    # Diccionario para traducir los meses al español (el estilo del analista)
    month_translation = {
        1: 'ene', 2: 'feb', 3: 'mar', 4: 'abr', 5: 'may', 6: 'jun',
        7: 'jul', 8: 'ago', 9: 'sep', 10: 'oct', 11: 'nov', 12: 'dic'
    }

    # Formateo la columna 'Mes' para que sea 'abr/25' en lugar de una fecha larga
    if 'Mes' in df.columns:
        temp_date = pd.to_datetime(df['Mes'], errors='coerce')
        mask = temp_date.notna()
        if mask.any():
            # Aplico mi traduccion personalizada
            df.loc[mask, 'Mes'] = temp_date[mask].apply(
                lambda x: f"{month_translation[x.month]}/{str(x.year)[2:]}"
            )

    # Redondeo las columnas numericas a 2 decimales para que se vea limpio
    numeric_cols = ['Debe', 'Haber', 'Saldo', 'Neto']
    for col in numeric_cols:
        if col in df.columns:
            # Convierto a numero por si acaso y redondeo
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).round(2)
    
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

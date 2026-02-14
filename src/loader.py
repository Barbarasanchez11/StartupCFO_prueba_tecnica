import pandas as pd
from src.config import INPUT_PL_FILE, MAYOR_FILE, COLUMN_MAPPING

def load_data(file_source):
    """
    Generic function to load an Excel file from a path or a file-like object.
    """
    try:
        if isinstance(file_source, str):
            print(f"[INFO] Reading file from path: {file_source}")
        else:
            print(f"[INFO] Reading file from upload buffer")
            
        df = pd.read_excel(file_source, engine='openpyxl')
        print(f"[SUCCESS] Loaded {len(df)} rows")
        return df
    except FileNotFoundError:
        print(f"[ERROR] File not found: {file_source}")
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
        # Forzamos a que sea tipo 'object' (texto) para no tener errores de tipo
        df['Mes'] = df['Mes'].astype(object)
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

def get_prepared_data(input_source=INPUT_PL_FILE, mayor_source=MAYOR_FILE):
    """
    Main function to load and prepare both datasets.
    Accepts paths or file-like objects.
    """
    input_df = load_data(input_source)
    input_df = normalize_data(input_df, is_mayor=False)
    
    mayor_df = load_data(mayor_source)
    mayor_df = normalize_data(mayor_df, is_mayor=True)
    
    return input_df, mayor_df

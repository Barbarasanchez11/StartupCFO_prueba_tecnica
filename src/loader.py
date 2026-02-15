import pandas as pd
from src.config import INPUT_PL_FILE, MAYOR_FILE, COLUMN_MAPPING, INPUT_PL_COLS, UNIQUE_IDENTIFIERS

def validate_columns(df, required_cols, file_label):
    """
    Checks if all required columns are present in the DataFrame.
    Raises ValueError if columns are missing.
    """
    # Excluyo 'END' porque es un marcador de fila, no una columna real que pandas lea siempre
    cols_to_check = [c for c in required_cols if c != "END"]
    missing = [col for col in cols_to_check if col not in df.columns]
    
    if missing:
        raise ValueError(f"Error de Estructura en {file_label}: Faltan las columnas: {', '.join(missing)}")

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

    # Arreglo la fecha principal con detección de errores
    if 'Fecha' in df.columns:
        # Intentamos la conversión
        temp_fecha = pd.to_datetime(df['Fecha'], errors='coerce')
        
        # Identificamos filas donde la conversión falló (pero no eran vacías ni decían 'END')
        is_not_end = df['Fecha'].astype(str).str.upper().str.strip() != 'END'
        invalid_dates = temp_fecha.isna() & df['Fecha'].notna() & is_not_end
        
        if invalid_dates.any():
            bad_rows = df.index[invalid_dates].tolist()
            # Calculamos la fila real de Excel (index 0 de pandas es fila 2 del Excel normalmente)
            excel_rows = [i + 2 for i in bad_rows]
            example_val = df.loc[bad_rows[0], 'Fecha']
            file_label = "Mayor" if is_mayor else "InputPL"
            
            raise ValueError(
                f" **Error de Formato en {file_label}**: Se han encontrado fechas ilegibles.\n\n"
                f"**Filas conflictivas (en Excel):** {excel_rows[:10]}{'...' if len(excel_rows) > 10 else ''}\n"
                f"**Ejemplo de valor incorrecto:** '{example_val}'\n\n"
                f"Por favor, asegúrate de que todas las celdas de la columna 'Fecha' tengan un formato válido (DD/MM/YYYY)."
            )
        
        df['Fecha'] = temp_fecha

    # Diccionario para traducir los meses al español (el estilo del analista)
    month_translation = {
        1: 'ene', 2: 'feb', 3: 'mar', 4: 'abr', 5: 'may', 6: 'jun',
        7: 'jul', 8: 'ago', 9: 'sep', 10: 'oct', 11: 'nov', 12: 'dic'
    }

    # Si tenemos Fecha, el Mes debe ser derivado de ella para evitar errores (como el famoso dic/99)
    if 'Fecha' in df.columns:
        # Nos aseguramos de que sea datetime
        temp_date = pd.to_datetime(df['Fecha'], errors='coerce')
        mask = temp_date.notna()
        if mask.any():
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
    Raises ValueError if validation fails.
    """
    # 1. Cargar datos brutos
    input_df = load_data(input_source)
    mayor_df = load_data(mayor_source)

    if input_df is None or mayor_df is None:
        raise ValueError("No se pudieron cargar los archivos seleccionados.")

    # 2. Validar estructura del InputPL (todas las columnas definidas)
    validate_columns(input_df, INPUT_PL_COLS, "InputPL")

    # 3. Normalizar
    input_df = normalize_data(input_df, is_mayor=False)
    mayor_df = normalize_data(mayor_df, is_mayor=True)

    # 4. Validar estructura del Mayor (identificadores únicos y concepto)
    mayor_required = UNIQUE_IDENTIFIERS + ["Concepto"]
    validate_columns(mayor_df, mayor_required, "Mayor")
    
    return input_df, mayor_df

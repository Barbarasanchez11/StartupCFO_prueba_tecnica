import pandas as pd
from src.config import INPUT_PL_FILE, MAYOR_FILE, COLUMN_MAPPING, INPUT_PL_COLS, UNIQUE_IDENTIFIERS
from src.logger import get_logger

logger = get_logger(__name__)

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
            logger.info(f"Reading file from path: {file_source}")
        else:
            logger.info("Reading file from upload buffer")
            
        df = pd.read_excel(file_source, engine='openpyxl')
        logger.success(f"Loaded {len(df)} rows")
        return df
    except FileNotFoundError:
        logger.error(f"File not found: {file_source}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return None

def normalize_data(df, is_mayor=False):
    """
    Standardize column names and data types (especially dates and formats).
    """
    if df is None:
        return None

    # Si es el Mayor, renombro columnas
    if is_mayor:
        logger.info("Normalizing Mayor columns...")
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

    # Diccionario para traducir los meses al español
    month_translation = {
        1: 'ene', 2: 'feb', 3: 'mar', 4: 'abr', 5: 'may', 6: 'jun',
        7: 'jul', 8: 'ago', 9: 'sep', 10: 'oct', 11: 'nov', 12: 'dic'
    }

    # 🔧 FUNCIÓN HELPER: Formatea fecha a "mes/año"
    def format_month_year(date_value):
        """Convierte una fecha a formato 'ene/25', 'feb/25', etc."""
        if pd.isna(date_value):
            return None
        try:
            if hasattr(date_value, 'month') and hasattr(date_value, 'year'):
                return f"{month_translation[date_value.month]}/{str(date_value.year)[2:]}"
        except (KeyError, AttributeError):
            pass
        return None

    # 🔧 NUEVA LÓGICA: Procesar columna 'Mes' de forma completa
    if 'Mes' in df.columns:
        logger.info("Processing 'Mes' column...")
        
        # Forzar tipo object para trabajar con strings y fechas
        df['Mes'] = df['Mes'].astype(object)
        
        # PASO 1: Intentar parsear valores existentes en 'Mes' como fechas
        temp_mes_date = pd.to_datetime(df['Mes'], errors='coerce')
        mask_valid_from_mes = temp_mes_date.notna()
        
        # Si algunos valores de 'Mes' son fechas válidas, formatearlos
        if mask_valid_from_mes.any():
            df.loc[mask_valid_from_mes, 'Mes'] = temp_mes_date[mask_valid_from_mes].apply(format_month_year)
        
        # PASO 2: Para los valores que NO se pudieron formatear, derivarlos de 'Fecha'
        # Identificar celdas vacías, None, o inválidas en 'Mes'
        mask_needs_fecha_derivation = (
            ~mask_valid_from_mes |  # No se pudo parsear de 'Mes'
            df['Mes'].isna() |  # Es NaN
            (df['Mes'].astype(str).str.strip() == '') |  # String vacío
            (df['Mes'].astype(str).str.strip() == 'None') |  # String "None"
            (df['Mes'].astype(str).str.strip() == 'nan')  # String "nan"
        )
        
        if mask_needs_fecha_derivation.any() and 'Fecha' in df.columns:
            logger.info(f"Deriving {mask_needs_fecha_derivation.sum()} 'Mes' values from 'Fecha' column...")
            
            # Usar la columna 'Fecha' (ya normalizada como datetime)
            fecha_values = df.loc[mask_needs_fecha_derivation, 'Fecha']
            formatted_from_fecha = fecha_values.apply(format_month_year)
            
            # Actualizar solo donde 'Fecha' tiene un valor válido
            valid_fecha_mask = formatted_from_fecha.notna()
            if valid_fecha_mask.any():
                # Crear índice combinado: mask_needs_fecha_derivation Y valid_fecha_mask
                final_mask = mask_needs_fecha_derivation.copy()
                final_mask[mask_needs_fecha_derivation] = valid_fecha_mask
                
                df.loc[final_mask, 'Mes'] = formatted_from_fecha[valid_fecha_mask].values
        
        # PASO 3: Limpiar valores residuales (None, nan, etc.) → string vacío
        cleanup_mask = (
            df['Mes'].isna() | 
            (df['Mes'].astype(str).str.strip() == 'None') |
            (df['Mes'].astype(str).str.strip() == 'nan')
        )
        if cleanup_mask.any():
            df.loc[cleanup_mask, 'Mes'] = ''
        
        logger.success("'Mes' column processed successfully.")

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

import pandas as pd
from src.config import INPUT_PL_FILE, MAYOR_FILE, COLUMN_MAPPING, INPUT_PL_COLS, UNIQUE_IDENTIFIERS
from src.logger import get_logger

logger = get_logger(__name__)

def validate_columns(df, required_cols, file_label):
    """
    Checks if all required columns are present in the DataFrame.
    Raises ValueError if columns are missing.
    """
  
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

  
    if is_mayor:
        logger.info("Normalizing Mayor columns...")
        df = df.rename(columns=COLUMN_MAPPING)

  
    if 'Fecha' in df.columns:
        temp_fecha = pd.to_datetime(df['Fecha'], errors='coerce')
        
       
        is_not_end = df['Fecha'].astype(str).str.upper().str.strip() != 'END'
        invalid_dates = temp_fecha.isna() & df['Fecha'].notna() & is_not_end
        
        if invalid_dates.any():
            bad_rows = df.index[invalid_dates].tolist()
           
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

  
    month_translation = {
        1: 'ene', 2: 'feb', 3: 'mar', 4: 'abr', 5: 'may', 6: 'jun',
        7: 'jul', 8: 'ago', 9: 'sep', 10: 'oct', 11: 'nov', 12: 'dic'
    }

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

   
    if 'Mes' in df.columns:
        logger.info("Processing 'Mes' column...")
        
        df['Mes'] = df['Mes'].astype(object)
        

        temp_mes_date = pd.to_datetime(df['Mes'], errors='coerce')
        mask_valid_from_mes = temp_mes_date.notna()
        

        if mask_valid_from_mes.any():
            df.loc[mask_valid_from_mes, 'Mes'] = temp_mes_date[mask_valid_from_mes].apply(format_month_year)

        mask_needs_fecha_derivation = (
            ~mask_valid_from_mes | 
            df['Mes'].isna() | 
            (df['Mes'].astype(str).str.strip() == '') | 
            (df['Mes'].astype(str).str.strip() == 'None') |  
            (df['Mes'].astype(str).str.strip() == 'nan')  
        )
        
        if mask_needs_fecha_derivation.any() and 'Fecha' in df.columns:
            logger.info(f"Deriving {mask_needs_fecha_derivation.sum()} 'Mes' values from 'Fecha' column...")
            
            fecha_values = df.loc[mask_needs_fecha_derivation, 'Fecha']
            formatted_from_fecha = fecha_values.apply(format_month_year)
            
            valid_fecha_mask = formatted_from_fecha.notna()
            if valid_fecha_mask.any():
              
                final_mask = mask_needs_fecha_derivation.copy()
                final_mask[mask_needs_fecha_derivation] = valid_fecha_mask
                
                df.loc[final_mask, 'Mes'] = formatted_from_fecha[valid_fecha_mask].values
        
       
        cleanup_mask = (
            df['Mes'].isna() | 
            (df['Mes'].astype(str).str.strip() == 'None') |
            (df['Mes'].astype(str).str.strip() == 'nan')
        )
        if cleanup_mask.any():
            df.loc[cleanup_mask, 'Mes'] = ''
        
        logger.success("'Mes' column processed successfully.")


    numeric_cols = ['Debe', 'Haber', 'Saldo', 'Neto']
    for col in numeric_cols:
        if col in df.columns:
           
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).round(2)
    
    return df

def get_prepared_data(input_source=INPUT_PL_FILE, mayor_source=MAYOR_FILE):
    """
    Main function to load and prepare both datasets.
    Accepts paths or file-like objects.
    Raises ValueError if validation fails.
    """
    input_df = load_data(input_source)
    mayor_df = load_data(mayor_source)

    if input_df is None or mayor_df is None:
        raise ValueError("No se pudieron cargar los archivos seleccionados.")

    validate_columns(input_df, INPUT_PL_COLS, "InputPL")

    input_df = normalize_data(input_df, is_mayor=False)
    mayor_df = normalize_data(mayor_df, is_mayor=True)

    mayor_required = UNIQUE_IDENTIFIERS + ["Concepto"]
    validate_columns(mayor_df, mayor_required, "Mayor")
    
    return input_df, mayor_df

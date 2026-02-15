import pandas as pd
from src.config import UNIQUE_IDENTIFIERS

def audit_data_quality(df, file_label):
    """
    Performs a data quality audit on the DataFrame to find potential quality issues.
    Returns a list of warning messages.
    """
    warnings = []
    
    if df is None or df.empty:
        return warnings

    for col in ['Debe', 'Haber']:
        if col in df.columns:
            negatives = df[pd.to_numeric(df[col], errors='coerce') < 0]
            if not negatives.empty:
                count = len(negatives)
                rows = (negatives.index + 2).tolist()[:5]
                warnings.append(f"**[{file_label}]** Detectados {count} valores negativos en la columna '{col}' (Filas Excel aprox: {rows}...).")

    critical_cols = ['Concepto', 'Nº Asiento', 'Fecha']
    for col in critical_cols:
        if col in df.columns:
            empties = df[df[col].isna() | (df[col].astype(str).str.strip() == "")]
            if col == 'Nº Asiento':
                empties = empties[empties[col].astype(str).str.upper() != 'END']
            
            if not empties.empty:
                count = len(empties)
                rows = (empties.index + 2).tolist()[:5]
                warnings.append(f" **[{file_label}]** Detectadas {count} celdas vacías en la columna crítica '{col}' (Filas Excel aprox: {rows}...).")


    if all(c in df.columns for c in UNIQUE_IDENTIFIERS):
        clean_df = df[df['Nº Asiento'].astype(str).str.upper() != 'END']
        
        duplicates = clean_df.groupby(UNIQUE_IDENTIFIERS).size()
        duplicate_groups = duplicates[duplicates > 1]
        
        if not duplicate_groups.empty:
            count_groups = len(duplicate_groups)
            total_duplicate_rows = duplicate_groups.sum()

            first_duplicate_key = duplicate_groups.index[0]
            mask = True
            for idx, col in enumerate(UNIQUE_IDENTIFIERS):
                if col == 'Fecha':
                    mask = mask & (pd.to_datetime(clean_df[col]) == pd.to_datetime(first_duplicate_key[idx]))
                else:
                    mask = mask & (clean_df[col] == first_duplicate_key[idx])
            duplicate_rows = clean_df[mask]
            example_rows = (duplicate_rows.index + 2).tolist()[:5]
            
            warnings.append(
                f"**[{file_label}]** Detectados {count_groups} grupos de duplicados exactos "
                f"(mismo Nº Asiento, Fecha y Saldo) con un total de {total_duplicate_rows} filas afectadas "
                f"(Filas Excel aprox: {example_rows}...)."
            )

    if all(c in df.columns for c in ['Nº Asiento', 'Fecha', 'Saldo']):
        clean_df = df[df['Nº Asiento'].astype(str).str.upper() != 'END']
        inconsistent = clean_df.groupby(['Nº Asiento', 'Fecha'])['Saldo'].nunique()
        bad_groups = inconsistent[inconsistent > 1]
        
        if not bad_groups.empty:
            count = len(bad_groups)
            warnings.append(f" **[{file_label}]** Detectadas {count} posibles inconsistencias: Registros con mismo Nº Asiento y Fecha pero diferente Saldo (posibles duplicados con error).")

    return warnings

def remove_exact_duplicates(df, file_label):
    """
    Removes exact duplicates (same Nº Asiento, Fecha and Saldo) from the DataFrame.
    Keeps only the first occurrence of each duplicate group.
    
    Args:
        df: DataFrame to clean
        file_label: File label for informative messages
    
    Returns:
        tuple: (df_cleaned, removed_count, summary_message)
            - df_cleaned: DataFrame without duplicates
            - removed_count: Number of rows removed
            - summary_message: Summary message of what was removed
    """
    if df is None or df.empty:
        return df, 0, ""
    
    if not all(c in df.columns for c in UNIQUE_IDENTIFIERS):
        return df, 0, ""
  
    original_size = len(df)

    end_mask = df['Nº Asiento'].astype(str).str.upper() == 'END'
    end_rows = df[end_mask].copy() if end_mask.any() else pd.DataFrame()
    clean_df = df[~end_mask].copy()

    df_cleaned = clean_df.drop_duplicates(subset=UNIQUE_IDENTIFIERS, keep='first')

    if not end_rows.empty:
        df_cleaned = pd.concat([df_cleaned, end_rows], ignore_index=False)
        df_cleaned = df_cleaned.sort_index()
    
    removed_count = original_size - len(df_cleaned)
    
    if removed_count > 0:
        summary_message = f"[{file_label}] Se eliminaron {removed_count} duplicados exactos automáticamente."
    else:
        summary_message = ""
    
    return df_cleaned, removed_count, summary_message

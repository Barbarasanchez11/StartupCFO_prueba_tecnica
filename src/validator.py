import pandas as pd
from src.config import UNIQUE_IDENTIFIERS

def audit_data_quality(df, file_label):
    """
    Realiza una auditoría sobre el DataFrame para encontrar posibles problemas de calidad.
    Retorna una lista de mensajes de advertencia.
    """
    warnings = []
    
    if df is None or df.empty:
        return warnings

    # 1. Detectar valores negativos en Debe o Haber
    for col in ['Debe', 'Haber']:
        if col in df.columns:
            # Filtramos los negativos
            negatives = df[pd.to_numeric(df[col], errors='coerce') < 0]
            if not negatives.empty:
                count = len(negatives)
                # Obtenemos las primeras 5 filas para no saturar
                rows = (negatives.index + 2).tolist()[:5]
                warnings.append(f"**[{file_label}]** Detectados {count} valores negativos en la columna '{col}' (Filas Excel aprox: {rows}...).")

    # 2. Detectar celdas vacías en campos críticos
    critical_cols = ['Concepto', 'Nº Asiento', 'Fecha']
    for col in critical_cols:
        if col in df.columns:
            # Buscamos nulos o strings vacíos
            empties = df[df[col].isna() | (df[col].astype(str).str.strip() == "")]
            # Filtramos la fila 'END' que no cuenta como error
            if col == 'Nº Asiento':
                empties = empties[empties[col].astype(str).str.upper() != 'END']
            
            if not empties.empty:
                count = len(empties)
                rows = (empties.index + 2).tolist()[:5]
                warnings.append(f" **[{file_label}]** Detectadas {count} celdas vacías en la columna crítica '{col}' (Filas Excel aprox: {rows}...).")

    # 3. Detectar duplicados exactos ( mismo Nº Asiento, Fecha y Saldo)
    if all(c in df.columns for c in UNIQUE_IDENTIFIERS):
        # Filtramos 'END' para evitar falsos positivos
        clean_df = df[df['Nº Asiento'].astype(str).str.upper() != 'END']
        
        # Agrupamos por los identificadores únicos y contamos cuántas filas hay en cada grupo
        duplicates = clean_df.groupby(UNIQUE_IDENTIFIERS).size()
        duplicate_groups = duplicates[duplicates > 1]
        
        if not duplicate_groups.empty:
            # Contamos cuántos grupos de duplicados hay
            count_groups = len(duplicate_groups)
            # Contamos el total de filas duplicadas (incluyendo las originales)
            total_duplicate_rows = duplicate_groups.sum()
            
            # Obtenemos las filas donde están los duplicados para reportar
            # Tomamos el primer grupo de duplicados como ejemplo
            first_duplicate_key = duplicate_groups.index[0]
            # Filtramos las filas que coinciden con este grupo de duplicados
            mask = True
            for idx, col in enumerate(UNIQUE_IDENTIFIERS):
                if col == 'Fecha':
                    # Para fechas, comparamos usando pd.Timestamp para evitar problemas de tipo
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

    # 4. Detectar inconsistencias (Mismo Asiento y Fecha, pero diferente Saldo)
    if all(c in df.columns for c in ['Nº Asiento', 'Fecha', 'Saldo']):
        # Agrupamos por Asiento y Fecha y contamos cuántos Saldos diferentes hay
        # Filtramos 'END' para evitar falsos positivos
        clean_df = df[df['Nº Asiento'].astype(str).str.upper() != 'END']
        inconsistent = clean_df.groupby(['Nº Asiento', 'Fecha'])['Saldo'].nunique()
        bad_groups = inconsistent[inconsistent > 1]
        
        if not bad_groups.empty:
            count = len(bad_groups)
            warnings.append(f" **[{file_label}]** Detectadas {count} posibles inconsistencias: Registros con mismo Nº Asiento y Fecha pero diferente Saldo (posibles duplicados con error).")

    return warnings

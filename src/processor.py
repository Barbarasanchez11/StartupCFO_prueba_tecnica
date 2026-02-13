import pandas as pd
from src.config import UNIQUE_IDENTIFIERS

def find_missing_records(input_df, mayor_df):
    """
    Compare Mayor with InputPL to find rows that exist in Mayor 
    but are not yet in InputPL based on UNIQUE_IDENTIFIERS.
    """
    
    # Si falta algún archivo, no puedo comparar nada, así que salgo
    if input_df is None or mayor_df is None:
        print("[ERROR] Cannot compare: one or both DataFrames are empty.")
        return None

    print(f"[INFO] Comparing records using identifiers: {UNIQUE_IDENTIFIERS}")

    # 'merge' (como un BUSCARV) para cruzar las dos tablas.
    # El indicator=True me crea una columna que me dice de dónde viene cada fila.
    comparison_df = pd.merge(
        mayor_df, 
        input_df[UNIQUE_IDENTIFIERS], 
        on=UNIQUE_IDENTIFIERS, 
        how='left', 
        indicator=True
    )

    # Solo me quedo con las filas que están únicamente en el Mayor (left_only)
    missing_records = comparison_df[comparison_df['_merge'] == 'left_only'].copy()

    # Borro la columna auxiliar dl merge porque ya no me sirve
    missing_records = missing_records.drop(columns=['_merge'])

    # Limpio las posibles filas que digan 'END', que no son movimientos reales
    missing_records = missing_records[missing_records['Nº Asiento'] != 'END']

    print(f"[SUCCESS] He terminado la comparación. He encontrado {len(missing_records)} registros nuevos.")
    
    return missing_records

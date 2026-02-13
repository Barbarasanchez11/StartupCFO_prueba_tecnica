from src.loader import get_prepared_data
from src.processor import find_missing_records
from src.classifier import classify_missing_records

def main():
    print("--- StartupCFO Tool ---")
    
    # 1. Empiezo cargando los archivos Excel
    input_df, mayor_df = get_prepared_data()
    
    # Si tengo los dos dataframes puedo seguir
    if input_df is not None and mayor_df is not None:
        
        # 2. Busco las líneas que faltan en el InputPL
        new_movements = find_missing_records(input_df, mayor_df)
        
        # Si he encontrado cosas nuevas, las clasifico
        if new_movements is not None and len(new_movements) > 0:
            
            # 3. Clasifico los gastos aprendiendo del pasado
            classified_df = classify_missing_records(new_movements, input_df)
            
            # Muestro un pequeño resumen por consola para ver que tal
            print(f"[DEBUG] Ready to insert {len(classified_df)} classified movements.")
            
            # Si quieres ver una muestra de los resultados:
            # print(classified_df[['Concepto', 'Tipo de gasto', 'Confidence']].head())
            
        else:
            print("[INFO] No new records found to add.")
            
    else:
        print("[ERROR] Could not load all required files.")

    print("----------------------------------")

if __name__ == "__main__":
    main()

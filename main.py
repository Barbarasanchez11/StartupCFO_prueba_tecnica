from src.loader import get_prepared_data
from src.processor import find_missing_records
from src.classifier import classify_missing_records
from src.writer import save_to_excel
from src.config import INPUT_PL_FILE

def main():
    print("--- StartupCFO Tool ---")
    
    # 1. Empiezo cargando y preparando los datos de los Excel
    input_df, mayor_df = get_prepared_data()
    
    # Si todo se ha cargado bien, sigo adelante
    if input_df is not None and mayor_df is not None:
        
        # 2. Comparo para ver qué movimientos faltan en el histórico
        new_movements = find_missing_records(input_df, mayor_df)
        
        # Si hay algo nuevo, me pongo manos a la obra
        if new_movements is not None and len(new_movements) > 0:
            
            # 3. Clasifico los gastos usando lógica fuzzy (IA sencillita)
            classified_df = classify_missing_records(new_movements, input_df)
            
            # 4. Por último, inyecto los nuevos datos en el Excel final
            save_to_excel(classified_df, INPUT_PL_FILE)
            
        else:
            print("[INFO] No new records found to add. Everything is up to date!")
            
    else:
        print("[ERROR] Flow stopped because of missing or corrupt files.")

    print("----------------------------------")

if __name__ == "__main__":
    main()

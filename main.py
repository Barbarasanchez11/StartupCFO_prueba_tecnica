from src.loader import get_prepared_data
from src.processor import find_missing_records
from src.classifier import classify_missing_records
from src.writer import save_to_excel
from src.config import INPUT_PL_FILE

def main():
    print("--- StartupCFO Tool ---")
    
    # 1. Empiezo cargando y preparando los datos de los Excel
    try:
        input_df, mayor_df = get_prepared_data()
    except ValueError as e:
        print(f"[ERROR] {e}")
        return

    # Si todo se ha cargado bien, sigo adelante
    if input_df is not None and mayor_df is not None:
        # Auditoría de Calidad
        from src.validator import audit_data_quality
        all_warnings = audit_data_quality(input_df, "InputPL") + audit_data_quality(mayor_df, "Mayor")
        if all_warnings:
            print("\n[WARNING] Se han detectado problemas de calidad en los datos:")
            for warning in all_warnings:
                print(f"  {warning}")
            print("")
        
        # Opción de Limpieza de Duplicados
        has_duplicates = any("duplicados exactos" in warning.lower() for warning in all_warnings)
        if has_duplicates:
            print("\n[INFO] Se han detectado duplicados exactos en los datos.")
            response = input("¿Desea eliminar duplicados exactos automáticamente? (s/n): ").strip().lower()
            
            if response == 's' or response == 'y' or response == 'yes' or response == 'si':
                from src.validator import remove_exact_duplicates
                
                # Limpiar InputPL
                input_df, removed_input, msg_input = remove_exact_duplicates(input_df, "InputPL")
                if msg_input:
                    print(f"  {msg_input}")
                
                # Limpiar Mayor
                mayor_df, removed_mayor, msg_mayor = remove_exact_duplicates(mayor_df, "Mayor")
                if msg_mayor:
                    print(f"  {msg_mayor}")
                
                total_removed = removed_input + removed_mayor
                if total_removed > 0:
                    print(f"[SUCCESS] Se eliminaron {total_removed} duplicados en total. Continuando con datos limpios...\n")
            else:
                print("[INFO] Continuando sin eliminar duplicados...\n")
        
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

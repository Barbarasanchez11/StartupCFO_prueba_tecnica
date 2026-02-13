from src.loader import get_prepared_data
from src.processor import find_missing_records

def main():
    print("--- StartupCFO Tool ---")
    
    # Cargo los datos de los dos Excel
    input_df, mayor_df = get_prepared_data()
    
   
    if input_df is not None:
        print("[DEBUG] InputPL is ready in memory.")
    else:
        print("[DEBUG] InputPL is missing (Expected for now).")
        
    if mayor_df is not None:
        print("[DEBUG] Mayor is ready and normalized.")
    else:
        print("[DEBUG] Mayor is missing (Expected for now).")

    print("-------------------------------------------")

if __name__ == "__main__":
    main()
